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

import logging

from django.utils.translation import ugettext_lazy as _

from horizon import tabs

from qinling_dashboard.content.functions import tables as project_tables


LOG = logging.getLogger(__name__)


class FunctionOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "project/functions/_detail_overview.html"
    failure_url = 'horizon:project:functions:index'

    def get_context_data(self, request):
        func = self.tab_group.kwargs['function']
        func.memory_size = "{:,}".format(func.memory_size)
        return {"function": func,
                "code": func.code}


class FunctionExecutionsTab(tabs.TableTab):
    table_classes = (project_tables.FunctionExecutionsTable,)
    name = _("Executions of this function")
    slug = "executions_of_this_function"
    template_name = "project/functions/_detail_executions.html"
    # preload = False

    def get_function_executions_data(self):
        return self.tab_group.kwargs['executions']


class FunctionVersionsTab(tabs.TableTab):
    table_classes = (project_tables.FunctionVersionsTable,)
    name = _("Versions of this function")
    slug = "versions_of_this_function"
    template_name = "project/functions/_detail_versions.html"

    def get_function_versions_data(self):
        return self.tab_group.kwargs['versions']


class FunctionDetailTabs(tabs.TabGroup):
    slug = "function_details"
    tabs = (FunctionOverviewTab,
            FunctionExecutionsTab,
            FunctionVersionsTab)
    sticky = True
    show_single_tab = False


class FunctionVersionOerviewTab(tabs.Tab):
    name = _("Version detail")
    slug = "versions_detail_overview"
    template_name = "project/functions/_detail_version_overview.html"
    preload = False

    def get_context_data(self, request):
        version = self.tab_group.kwargs['version']
        return {"version": version}


class FunctionVersionDetailTabs(tabs.TabGroup):
    slug = "function_version_details"
    tabs = (FunctionVersionOerviewTab,)
    sticky = True
    show_single_tab = False
