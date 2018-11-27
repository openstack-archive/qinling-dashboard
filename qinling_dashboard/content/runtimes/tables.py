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


from django.utils.translation import ugettext_lazy as _

from horizon import tables

from qinling_dashboard import api
from qinling_dashboard import utils


class CreateRuntime(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Runtime")
    url = "horizon:project:runtimes:create"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("function_engine", "runtime:create"),)
    icon = "plus"
    ajax = True


class RuntimesFilterAction(tables.FilterAction):

    def filter(self, table, runtimes, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [runtime for runtime in runtimes
                if q in runtime.name.lower()]


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, runtime_id):
        execution = api.qinling.runtime_get(request, runtime_id)
        return execution


class RuntimesTable(tables.DataTable):

    id = tables.Column("id",
                       verbose_name=_("Id"),
                       link="horizon:project:runtimes:detail")

    name = tables.Column("name",
                         verbose_name=_("Name"))

    image = tables.Column("image",
                          verbose_name=_("Image"))

    created_at = tables.Column("created_at",
                               verbose_name=_("Created At"))

    updated_at = tables.Column("updated_at",
                               verbose_name=_("Updated At"))

    project_id = tables.Column("project_id",
                               verbose_name=_("Project ID"))

    is_public = tables.Column("is_public",
                              verbose_name=_("Is Public"))

    status = tables.Column(
        "status",
        status=True,
        status_choices=utils.FUNCTION_ENGINE_STATUS_CHOICES,
        display_choices=utils.FUNCTION_ENGINE_STATUS_DISPLAY_CHOICES)

    def __init__(self, request, data=None, needs_form_wrapper=None, **kwargs):
        super(RuntimesTable, self).__init__(request, data,
                                            needs_form_wrapper, **kwargs)
        if not request.user.is_superuser:
            del self.columns["is_public"]

    class Meta(object):
        name = "runtimes"
        verbose_name = _("Runtimes")
        status_columns = ["status"]
        multi_select = True
        row_class = UpdateRow
        table_actions = (CreateRuntime,
                         RuntimesFilterAction,)
