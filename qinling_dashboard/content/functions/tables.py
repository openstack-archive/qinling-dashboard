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

from django.utils.http import urlencode

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

from qinling_dashboard import api

from qinling_dashboard.content.executions import tables as e_tables


class CreateFunction(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Function")
    url = "horizon:project:functions:create"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("function_engine", "function:create"),)
    icon = "plus"
    ajax = True


class CreateFunctionVersion(tables.LinkAction):
    name = "create_version"
    verbose_name = _("Create Version")
    url = "horizon:project:functions:create_version"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("function_engine", "function:version_create"),)

    def allowed(self, request, datum):
        """Function versioning is only allowed for package type function."""
        code = datum.code
        if code['source'] == 'package':
            return True
        return False


class UpdateFunction(tables.LinkAction):
    name = "update"
    verbose_name = _("Update Function")
    url = "horizon:project:functions:update"
    classes = ("ajax-modal",)
    policy_rules = (("function_engine", "function:update"),)
    icon = "edit"
    ajax = True


class DownloadFunction(tables.LinkAction):
    name = "download"
    verbose_name = _("Download Function")
    url = "horizon:project:functions:download"
    icon = "download"
    policy_rules = (("function_engine", "function:download"),)

    def allowed(self, request, datum):
        """Function downloading is only allowed for package type function."""
        code = datum.code
        if code['source'] == 'package':
            return True
        return False


class DeleteFunction(tables.DeleteAction):
    policy_rules = (("function_engine", "function:delete"),)
    help_text = _("Deleted functions are not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Function",
            u"Delete Functions",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Delete Function",
            u"Delete Functions",
            count
        )

    def delete(self, request, func):
        api.qinling.function_delete(request, func)


class FunctionsFilterAction(tables.FilterAction):

    def filter(self, table, functions, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [function for function in functions
                if q in function.name.lower()]


class RuntimeIDColumn(tables.Column):

    def get_link_url(self, datum):
        if not hasattr(datum, 'id'):
            return None
        runtime_id = datum.runtime_id
        result = reverse(self.link, args=(runtime_id,))
        return result


def get_memory_size(function):
    return "{:,}".format(function.memory_size)


class FunctionsTable(tables.DataTable):

    id = tables.Column("id",
                       verbose_name=_("Id"),
                       link="horizon:project:functions:detail")

    name = tables.Column("name",
                         verbose_name=_("Name"))

    description = tables.Column("description",
                                verbose_name=_("Description"))

    runtime_id = RuntimeIDColumn("runtime_id",
                                 verbose_name=_("Runtime ID"),
                                 link="horizon:project:runtimes:detail")

    entry = tables.Column("entry",
                          verbose_name=_("Entry"))

    created_at = tables.Column("created_at",
                               verbose_name=_("Created At"))

    updated_at = tables.Column("updated_at",
                               verbose_name=_("Updated At"))

    cpu = tables.Column("cpu", verbose_name=_("CPU  (Milli CPU)"))
    memory_size = tables.Column(get_memory_size,
                                verbose_name=_("Memory Size (Bytes)"))

    def get_object_display(self, datum):
        return datum.id

    class Meta(object):
        name = "functions"
        verbose_name = _("Functions")
        multi_select = True

        table_actions = (
            CreateFunction,
            DeleteFunction,
            FunctionsFilterAction
        )
        row_actions = (
            UpdateFunction,
            DownloadFunction,
            CreateFunctionVersion,
            DeleteFunction
        )


class DeleteFunctionVersion(tables.DeleteAction):
    policy_rules = (("function_engine", "function_version:delete"),)
    help_text = _("Deleted function versions are not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Function Version",
            u"Delete Function Versions",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Delete Function Version",
            u"Delete Function Versions",
            count
        )

    def delete(self, request, version_id):
        functions = api.qinling.functions_list(request, with_version=True)

        for f in functions:
            for v in f.versions:
                if v.id == version_id:
                    version_number = v.version_number
                    function_id = v.function_id
                    api.qinling.version_delete(request,
                                               function_id, version_number)


class CreateFunctionExecution(tables.LinkAction):
    name = "create_execution_from_function"
    verbose_name = _("Create Execution")
    url = "horizon:project:functions:create_execution"
    classes = ("ajax-modal",)
    policy_rules = (("function_engine", "function_execution:create"),)
    icon = "plus"

    def get_link_url(self, datum):
        function_id = datum.function_id
        version_number = datum.version_number

        base_url = reverse(self.url, args=(function_id,))

        params = urlencode({"function_id": function_id,
                            "version": version_number})
        return "?".join([base_url, params])


class FunctionVersionColumn(tables.Column):

    def get_link_url(self, datum):
        version_number = datum.version_number
        function_id = self.table.kwargs['function_id']
        result = reverse(self.link, args=(function_id,
                                          version_number))
        return result


class FunctionColumn(tables.Column):

    def get_link_url(self, datum):
        function_id = datum.function_id
        result = reverse(self.link, args=(function_id,))
        result += "?tab=function_details__overview"
        return result


class FunctionVersionsTable(tables.DataTable):

    id = FunctionVersionColumn("id",
                               verbose_name=_("Id"),
                               link="horizon:project:functions:version_detail")

    description = tables.Column("description",
                                verbose_name=_("Description"))

    function_id = FunctionColumn("function_id",
                                 verbose_name=_("Function ID"),
                                 link="horizon:project:functions:detail")

    version_number = tables.Column("version_number",
                                   verbose_name=_("Version Number"))

    count = tables.Column("count", verbose_name=_("Count"))

    created_at = tables.Column("created_at",
                               verbose_name=_("Created At"))

    updated_at = tables.Column("updated_at",
                               verbose_name=_("Updated At"))

    def get_object_display(self, datum):
        return datum.id

    class Meta(object):
        name = "function_versions"
        verbose_name = _("Versions")
        multi_select = True

        table_actions = (DeleteFunctionVersion,)
        row_actions = (CreateFunctionExecution,
                       DeleteFunctionVersion,)


class FunctionExecutionsTable(e_tables.ExecutionsTable):

    class Meta(object):
        name = "function_executions"
        verbose_name = _("Executions")
        multi_select = True

        table_actions = (e_tables.DeleteExecution,)
        row_actions = (e_tables.LogLink,
                       e_tables.DeleteExecution,)
