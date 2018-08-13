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


LOG = logging.getLogger(__name__)


class ExecutionOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "project/executions/_detail_overview.html"

    def get_context_data(self, request):
        execution = self.tab_group.kwargs["execution"]
        return {"execution": execution,
                "result": execution.result}


class ExecutionLogsTab(tabs.Tab):
    name = _("Execution Logs")
    slug = "execution_logs"
    template_name = "project/executions/_detail_logs.html"

    def get_context_data(self, request):
        execution_logs = self.tab_group.kwargs["execution_logs"]
        return {"execution_logs": execution_logs}


class ExecutionDetailTabs(tabs.TabGroup):
    slug = "execution_details"
    tabs = (ExecutionOverviewTab,
            ExecutionLogsTab)
    sticky = True
    show_single_tab = False
