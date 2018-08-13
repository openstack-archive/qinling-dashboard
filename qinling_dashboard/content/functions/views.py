# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import io

from django import shortcuts

from django.http import HttpResponse
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tables
from horizon import tabs

from horizon.utils import memoized

from qinling_dashboard import api

from qinling_dashboard import exceptions as q_exc

from qinling_dashboard.content.executions import views as ex_views

from qinling_dashboard.content.functions import forms as project_forms
from qinling_dashboard.content.functions import tables as project_tables
from qinling_dashboard.content.functions import tabs as project_tabs


class CreateFunctionExecutionView(ex_views.CreateExecutionView):

    modal_header = submit_label = page_title = _("Create Execution")
    submit_url = "horizon:project:functions:create_execution"
    success_url = "horizon:project:functions:detail"

    def get_context_data(self, **kwargs):
        context = super(CreateFunctionExecutionView, self).\
            get_context_data(**kwargs)
        submit_url = reverse(self.submit_url,
                             args=(self.kwargs['function_id'],))
        context['submit_url'] = submit_url
        return context

    def get_success_url(self):
        function_id = self.kwargs['function_id']
        result = reverse(self.success_url, args=(function_id,))
        result += "?tab=function_details__executions_of_this_function"
        return result


class CreateFunctionView(forms.ModalFormView):

    form_class = project_forms.CreateFunctionForm
    modal_header = submit_label = page_title = _("Create Function")
    template_name = "project/functions/create_function.html"
    submit_url = reverse_lazy("horizon:project:functions:create")
    success_url = reverse_lazy("horizon:project:functions:index")


class UpdateFunctionView(forms.ModalFormView):

    form_class = project_forms.UpdateFunctionForm
    modal_header = submit_label = page_title = _("Update Function")
    template_name = "project/functions/update_function.html"
    submit_url = "horizon:project:functions:update"
    success_url = reverse_lazy("horizon:project:functions:index")

    @memoized.memoized_method
    def get_object(self, *args, **kwargs):
        function_id = self.kwargs['function_id']
        try:
            return api.qinling.function_get(self.request, function_id)
        except Exception:
            redirect = reverse("horizon:project:functions:index")
            msg = _('Unable to retrieve function details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateFunctionView, self).\
            get_context_data(**kwargs)
        function_id = self.kwargs['function_id']
        context['function_id'] = function_id
        context['submit_url'] = reverse(self.submit_url, args=(function_id,))
        return context

    def get_initial(self):
        initial = super(UpdateFunctionView, self).get_initial()
        func = self.get_object()
        code = getattr(func, 'code', {})
        code_swift = code.get('swift', {})
        source = code.get('source', '')

        initial.update({
            'function_id': func.id,
            'name': getattr(func, 'name', ''),
            'description': getattr(func, 'description', ''),
            'cpu': getattr(func, 'cpu', ''),
            'memory_size': getattr(func, 'memory_size', ''),
            'runtime_id': getattr(func, 'runtime_id', ''),
            'entry': getattr(func, 'entry', ''),
            'code_type': code.get('source', ''),
            'swift_container': code_swift.get('container', ''),
            'swift_object': code_swift.get('object', ''),
            'image': code.get('image', ''),
            'source': source,
        })
        return initial


class CreateFunctionVersionView(forms.ModalFormView):

    form_class = project_forms.CreateFunctionVersionForm
    modal_header = submit_label = page_title = _("Create Version")
    template_name = "project/functions/create_version.html"
    submit_url = "horizon:project:functions:create_version"
    success_url = "horizon:project:functions:detail"

    def get_success_url(self):
        function_id = self.kwargs['function_id']
        result = reverse(self.success_url, args=(function_id,))
        result += "?tab=function_details__versions_of_this_function"
        return result

    def get_context_data(self, **kwargs):
        context = super(CreateFunctionVersionView, self).\
            get_context_data(**kwargs)
        function_id = self.kwargs['function_id']
        context['function_id'] = function_id
        context['submit_url'] = reverse(self.submit_url, args=(function_id,))
        return context

    def get_initial(self):
        initial = super(CreateFunctionVersionView, self).get_initial()
        initial.update({
            'function_id': self.kwargs["function_id"],
        })
        return initial


class IndexView(tables.DataTableView):

    table_class = project_tables.FunctionsTable
    page_title = _("Functions")

    def get_data(self):
        try:
            functions = api.qinling.functions_list(self.request)
        except Exception:
            functions = []
            msg = _('Unable to retrieve functions list.')
            exceptions.handle(self.request, msg)
        return functions


class DetailView(tabs.TabbedTableView):
    tab_group_class = project_tabs.FunctionDetailTabs
    template_name = 'project/functions/detail.html'
    page_title = _("Function Details: {{ resource_name }}")
    failure_url = reverse_lazy('horizon:project:functions:index')

    @memoized.memoized_method
    def _get_data(self):
        function_id = self.kwargs['function_id']
        try:
            function = api.qinling.function_get(self.request, function_id)
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve '
                  'details for Function "%s".') % function_id,
                redirect=self.failure_url
            )
        return function

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        func = self._get_data()
        table = project_tables.FunctionsTable(self.request)
        resource_name = func.name if func.name else func.id
        context["function"] = func
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(func)
        context["table_id"] = "runtime"
        context["resource_name"] = resource_name
        context["object_id"] = func.id
        return context

    def _get_executions(self):
        function_id = self.kwargs['function_id']
        try:
            executions = api.qinling.executions_list(self.request, function_id)
        except Exception:
            executions = []
            messages.error(self.request, _(
                'Unable to get executions of '
                'this function "%s".') % function_id)
        return executions

    def _get_versions(self):
        function_id = self.kwargs['function_id']
        try:
            versions = api.qinling.versions_list(self.request, function_id)
        except Exception:
            versions = []
            messages.error(self.request, _(
                'Unable to get versions of this function "%s".') % function_id)
        return versions

    def get_tabs(self, request, *args, **kwargs):
        func = self._get_data()
        executions = self._get_executions()
        versions = self._get_versions()
        return self.tab_group_class(request,
                                    function=func,
                                    executions=executions,
                                    versions=versions,
                                    **kwargs)

    @staticmethod
    def get_redirect_url():
        return reverse('horizon:project:functions:index')


class VersionDetailView(tabs.TabView):
    tab_group_class = project_tabs.FunctionVersionDetailTabs
    template_name = 'project/functions/detail_version.html'
    page_title = _("Function Version Details: "
                   "{{ version.function_id }} "
                   "(Version Number={{ version_number }})")
    failure_url = reverse_lazy('horizon:project:functions:index')

    def get_redirect_url(self, version_number=None):
        function_id = self.kwargs['function_id']

        if not version_number:
            return reverse('horizon:project:functions:detail',
                           args=(function_id,))

        return reverse('horizon:project:functions:version_detail',
                       args=(function_id, version_number))

    @memoized.memoized_method
    def get_data(self):
        function_id = self.kwargs['function_id']
        version_number = int(self.kwargs['version_number'])
        try:
            version = api.qinling.version_get(self.request,
                                              function_id,
                                              version_number)
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve details for '
                  'function version "%s".') % (function_id, version_number),
                redirect=self.failure_url
            )
        return version

    def get_context_data(self, **kwargs):
        context = super(VersionDetailView, self).get_context_data(**kwargs)
        version = self.get_data()

        table = project_tables.FunctionVersionsTable(self.request)
        context["version"] = version
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(version)
        context["table_id"] = "function_version"
        context["object_id"] = version.version_number
        return context

    def get_tabs(self, request, *args, **kwargs):
        version = self.get_data()
        return self.tab_group_class(request,
                                    version=version,
                                    **kwargs)


def download_function(request, function_id):
    try:
        data = api.qinling.function_download(request, function_id)

        output = io.BytesIO()
        for chunk in data:
            output.write(chunk)
        ctx = output.getvalue()

        response = HttpResponse(ctx, content_type='application/octet-stream')
        response['Content-Length'] = str(len(response.content))

        response['Content-Disposition'] = \
            'attachment; filename=qinling-function-' + function_id + '.zip'
        return response
    except q_exc.NOT_FOUND as ne:
        messages.error(request,
                       _('Error because file not found function: %s') % ne)
    except Exception as e:
        messages.error(request, _('Error downloading function: %s') % e)
        return shortcuts.redirect(request.build_absolute_uri())
