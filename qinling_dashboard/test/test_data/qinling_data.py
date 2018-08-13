#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from qinlingclient.v1 import function
from qinlingclient.v1 import function_execution
from qinlingclient.v1 import function_version
from qinlingclient.v1 import runtime

from qinling_dashboard.test.test_data import utils


PROJECT_ID = "87173d0c07d547bfa1343cabe2e6fe69"
RUNTIME_ID_BASE = "6cb1f505-9a42-4569-a94d-9c2f4b7e7b4{0}"
FUNCTION_ID_BASE = "aacb5032-f8b9-4ad5-8fd4-8017d0d1c54{0}"
EXECUTION_ID_BASE = "f0b5d7f5-d1f1-4f3e-9080-16e4cd918f9{0}"
VERSION_ID_BASE = "30c3e142-2850-4a89-90a7-0a4e4d654f{0}{1}"


def data(TEST):
    TEST.runtimes = utils.TestDataContainer()
    TEST.functions = utils.TestDataContainer()
    TEST.executions = utils.TestDataContainer()
    TEST.versions = utils.TestDataContainer()

    for i in range(10):
        runtime_data = {
            "id": RUNTIME_ID_BASE.format(i),
            "name": "python2.7-runtime-{0}".format(i),
            "status": "available",
            "created_at": "2018-07-11 01:09:13",
            "description": None,
            "image": "openstackqinling/python-runtime",
            "updated_at": "2018-07-11 01:09:28",
            "is_public": True,
            "project_id": PROJECT_ID,
        }
        rt = runtime.Runtime(runtime.RuntimeManager(None), runtime_data)
        TEST.runtimes.add(rt)

    for i in range(10):
        function_data = {
            "id": FUNCTION_ID_BASE.format(i),
            "count": 0,
            "code": "{\"source\": \"package\", "
                    "\"md5sum\": \"976325c9b41bc5a2ddb54f3493751f7e\"}",
            "description": None,
            "created_at": "2018-08-01 08:33:50",
            "updated_at": None,
            "latest_version": 0,
            "memory_size": 33554432,
            "timeout": None,
            "entry": "qinling_test.main",
            "project_id": PROJECT_ID,
            "cpu": 100,
            "runtime_id": RUNTIME_ID_BASE.format(i),
            "name": "github_test"
        }
        func = function.Function(function.FunctionManager(None), function_data)
        TEST.functions.add(func)

    for i in range(10):
        execution_data = {
            "status": "success",
            "project_id": PROJECT_ID,
            "description": None,
            "updated_at": "2018-08-01 06:09:58",
            "created_at": "2018-08-01 06:09:55",
            "sync": True,
            "function_version": 0,
            "result": "{\"duration\": 0.788, \"output\": 30}",
            "input": None,
            "function_id": FUNCTION_ID_BASE.format(i),
            "id": EXECUTION_ID_BASE.format(i),
        }
        execution = function_execution.FunctionExecution(
            function_execution.ExecutionManager(None), execution_data)
        TEST.executions.add(execution)

    # Each mocked function has 10 of version data.
    for i in range(10):
        this_function_id = FUNCTION_ID_BASE.format(i)
        for j in range(10):
            version_data = {
                "count": 0,
                "version_number": j,
                "function_id": this_function_id,
                "description": "",
                "created_at": "2018-08-03 02:01:44",
                "updated_at": None,
                "project_id": PROJECT_ID,
                "id": VERSION_ID_BASE.format(i, j)
            }
            version = function_version.FunctionVersion(
                function_version.FunctionVersionManager(None), version_data)
            TEST.versions.add(version)
