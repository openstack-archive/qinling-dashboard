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

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from qinling_dashboard import api
from qinling_dashboard.content.runtimes import forms as project_forms
from qinling_dashboard.content.runtimes import tables as project_tables
from qinling_dashboard.content.runtimes import tabs as project_tabs


class CreateRuntimeView(forms.ModalFormView):

    form_class = project_forms.CreateRuntimeForm
    modal_header = submit_label = page_title = _("Create Runtime")
    template_name = 'project/runtimes/create.html'
    submit_url = reverse_lazy("horizon:project:runtimes:create")
    success_url = reverse_lazy("horizon:project:runtimes:index")


class IndexView(tables.DataTableView):

    table_class = project_tables.RuntimesTable
    page_title = _("Runtimes")

    def get_data(self):
        try:
            runtimes = api.qinling.runtimes_list(self.request)
        except Exception:
            runtimes = []
            msg = _('Unable to retrieve runtimes list.')
            exceptions.handle(self.request, msg)
        return runtimes


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.RuntimeDetailTabs
    template_name = 'project/runtimes/detail.html'
    page_title = _("Runtime Details: {{ resource_name }}")
    failure_url = reverse_lazy('horizon:project:runtimes:index')

    @memoized.memoized_method
    def get_data(self):
        runtime_id = self.kwargs['runtime_id']
        try:
            runtime = api.qinling.runtime_get(self.request, runtime_id)
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve '
                  'details for Runtime "%s".') % runtime_id,
                redirect=self.failure_url
            )
        return runtime

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        runtime = self.get_data()
        table = project_tables.RuntimesTable(self.request)
        resource_name = runtime.name if runtime.name else runtime.id
        context["runtime"] = runtime
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(runtime)
        context["table_id"] = "runtime"
        context["resource_name"] = resource_name
        context["object_id"] = runtime.id
        return context

    def get_tabs(self, request, *args, **kwargs):
        runtime = self.get_data()
        return self.tab_group_class(request,
                                    runtime=runtime,
                                    **kwargs)

    @staticmethod
    def get_redirect_url():
        return reverse('horizon:project:runtimes:index')
