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
from qinling_dashboard.content.executions import forms as project_forms
from qinling_dashboard.content.executions import tables as project_tables
from qinling_dashboard.content.executions import tabs as project_tabs


class CreateExecutionView(forms.ModalFormView):

    form_class = project_forms.CreateExecutionForm
    modal_header = submit_label = page_title = _("Create Execution")
    template_name = 'project/executions/create.html'
    submit_url = reverse_lazy("horizon:project:executions:create")
    success_url = reverse_lazy("horizon:project:executions:index")


class IndexView(tables.DataTableView):

    table_class = project_tables.ExecutionsTable
    page_title = _("Executions")

    def get_data(self):
        try:
            executions = api.qinling.executions_list(self.request)
        except Exception:
            executions = []
            msg = _('Unable to retrieve executions list.')
            exceptions.handle(self.request, msg)
        return executions


class DetailView(tabs.TabbedTableView):
    tab_group_class = project_tabs.ExecutionDetailTabs
    template_name = 'project/executions/detail.html'
    page_title = _("Execution Details: {{ resource_name }}")
    failure_url = reverse_lazy('horizon:project:executions:index')

    @memoized.memoized_method
    def _get_data(self):
        execution_id = self.kwargs['execution_id']
        try:
            execution = api.qinling.execution_get(self.request, execution_id)
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve '
                  'details for execution "%s".') % execution_id,
                redirect=self.failure_url
            )
        return execution

    def _get_execution_logs(self):
        execution_id = self.kwargs['execution_id']
        try:
            execution_logs = api.qinling.execution_log_get(self.request,
                                                           execution_id)
        except Exception:
            execution_logs = ""
            msg = _('Unable to retrieve execution logs.')
            exceptions.handle(self.request, msg)
        return execution_logs

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        execution = self._get_data()
        table = project_tables.ExecutionsTable(self.request)
        context["execution"] = execution
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(execution)
        context["table_id"] = "execution"
        context["resource_name"] = execution.id
        context["object_id"] = execution.id
        return context

    def get_tabs(self, request, *args, **kwargs):
        execution = self._get_data()
        execution_logs = self._get_execution_logs()
        return self.tab_group_class(request,
                                    execution=execution,
                                    execution_logs=execution_logs,
                                    **kwargs)

    @staticmethod
    def get_redirect_url():
        return reverse('horizon:project:executions:index')
