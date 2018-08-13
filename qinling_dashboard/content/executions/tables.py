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

from django import template

from django.urls import reverse

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

from qinling_dashboard import api
from qinling_dashboard import utils


class CreateExecution(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Execution")
    url = "horizon:project:executions:create"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("function_engine", "function_execution:create"),)
    icon = "plus"
    ajax = True


class LogLink(tables.LinkAction):
    name = "console"
    verbose_name = _("Show Execution Logs")
    url = "horizon:project:executions:detail"
    classes = ("btn-console",)
    policy_rules = (("function_engine", "function_execution:log_show"),)

    def get_link_url(self, datum):
        base_url = super(LogLink, self).get_link_url(datum)
        return base_url + "?tab=execution_details__execution_logs"


class DeleteExecution(tables.DeleteAction):
    policy_rules = (("function_engine", "function_execution:delete"),)
    help_text = _("Deleted executions are not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Execution",
            u"Delete Executions",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Delete Execution",
            u"Delete Executions",
            count
        )

    def delete(self, request, execution):
        api.qinling.execution_delete(request, execution)


class ExecutionsFilterAction(tables.FilterAction):

    def filter(self, table, functions, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [function for function in functions
                if q in function.name.lower()]


class FunctionIDColumn(tables.Column):

    def get_link_url(self, datum):
        function_id = datum.function_id
        result = reverse(self.link, args=(function_id,))
        result += "?tab=function_details__overview"
        return result


def get_result(datum):
    template_name = 'project/executions/_execution_result.html'
    result = datum.result

    if result is None:
        return result

    duration = result.get('duration', '')
    output = result.get('output', '')

    if isinstance(output, dict) and 'error' in output:
        output = output.get('error')

    context = {
        "duration": duration,
        "output": output
    }
    return template.loader.render_to_string(template_name, context)


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, execution_id):
        execution = api.qinling.execution_get(request, execution_id)
        return execution


class ExecutionsTable(tables.DataTable):

    id = tables.Column("id",
                       verbose_name=_("Id"),
                       link="horizon:project:executions:detail")

    function_id = FunctionIDColumn("function_id",
                                   verbose_name=_("Function ID"),
                                   link="horizon:project:functions:detail")

    function_version = tables.Column("function_version",
                                     verbose_name=_("Function Version"))

    description = tables.Column("description",
                                verbose_name=_("Description"))

    input = tables.Column("input", verbose_name=_("Input"))

    result = tables.Column(get_result,
                           verbose_name=_("Result"))

    sync = tables.Column("sync", verbose_name=_("Sync"))

    created_at = tables.Column("created_at",
                               verbose_name=_("Created At"))

    updated_at = tables.Column("updated_at",
                               verbose_name=_("Updated At"))

    project_id = tables.Column("project_id",
                               verbose_name=_("Project ID"))

    status = tables.Column(
        "status",
        status=True,
        status_choices=utils.FUNCTION_ENGINE_STATUS_CHOICES,
        display_choices=utils.FUNCTION_ENGINE_STATUS_DISPLAY_CHOICES)

    def get_object_display(self, datum):
        return datum.id

    class Meta(object):
        name = "executions"
        verbose_name = _("Executions")
        status_columns = ["status"]
        multi_select = True
        row_class = UpdateRow

        table_actions = (
            CreateExecution,
            DeleteExecution,
            ExecutionsFilterAction,
        )
        row_actions = (LogLink,
                       DeleteExecution,)
