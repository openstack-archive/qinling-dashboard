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

import mock

from qinling_dashboard import api
from qinling_dashboard.test import helpers as test


class QinlingApiTests(test.APIMockTestCase):

    # Runtimes
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_runtimes_list(self, mock_qinlingclient):
        """Test for api.qinling.runtimes_list()"""
        runtimes = self.runtimes.list()

        qclient = mock_qinlingclient.return_value
        qclient.runtimes.list.return_value = runtimes

        result = api.qinling.runtimes_list(self.request)
        self.assertItemsEqual(result, runtimes)

        qclient.runtimes.list.assert_called_once_with()

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_runtime_get(self, mock_qinlingclient):
        """Test for api.qinling.runtime_get()"""
        runtime = self.runtimes.first()

        qclient = mock_qinlingclient.return_value
        qclient.runtimes.get.return_value = runtime

        result = api.qinling.runtime_get(self.request, runtime.id)
        self.assertEqual(result, runtime)

        qclient.runtimes.get.assert_called_once_with(runtime.id)

    # Functions
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create(self, mock_qinlingclient):
        """Test for api.qinling.function_create()"""
        func = self.functions.first()

        qclient = mock_qinlingclient.return_value
        qclient.functions.create.return_value = func

        params = {}
        result = api.qinling.function_create(self.request, **params)
        self.assertEqual(result, func)

        qclient.functions.create.assert_called_once_with(**params)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_update(self, mock_qinlingclient):
        """Test for api.qinling.function_update()"""
        func = self.functions.first()

        qclient = mock_qinlingclient.return_value
        qclient.functions.update.return_value = func

        params = {}
        result = api.qinling.function_update(self.request, func.id, **params)
        self.assertEqual(result, func)

        qclient.functions.update.assert_called_once_with(func.id, **params)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_delete(self, mock_qinlingclient):
        """Test for api.qinling.function_delete()"""
        func = self.functions.first()

        qclient = mock_qinlingclient.return_value
        qclient.functions.delete.return_value = None

        result = api.qinling.function_delete(self.request, func.id)
        self.assertIsNone(result)

        qclient.functions.delete.assert_called_once_with(func.id)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_functions_list(self, mock_qinlingclient):
        """Test for api.qinling.functions_list()"""
        functions = self.functions.list()

        qclient = mock_qinlingclient.return_value
        qclient.functions.list.return_value = functions

        result = api.qinling.functions_list(self.request)
        self.assertItemsEqual(result, functions)

        qclient.functions.list.assert_called_once_with()

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_get(self, mock_qinlingclient):
        """Test for api.qinling.function_get()"""
        func = self.functions.first()

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = func

        result = api.qinling.function_get(self.request, func.id)
        self.assertEqual(result, func)

        qclient.functions.get.assert_called_once_with(func.id)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_download(self, mock_qinlingclient):
        """Test for api.qinling.function_download()"""
        func = self.functions.first()

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = func

        result = api.qinling.function_download(self.request, func.id)
        self.assertEqual(result, func)

        qclient.functions.get.assert_called_once_with(func.id, download=True)

    # Function Executions
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_execution_create(self, mock_qinlingclient):
        """Test for api.qinling.execution_create()"""
        func = self.functions.first()
        execution = self.executions.first()

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.create.return_value = execution

        result = api.qinling.execution_create(self.request, func.id,
                                              version=1, sync=True,
                                              input=None)
        self.assertEqual(result, execution)

        qclient.function_executions.create.assert_called_once_with(func.id,
                                                                   1,
                                                                   True,
                                                                   None)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_execution_delete(self, mock_qinlingclient):
        """Test for api.qinling.execution_delete()"""
        execution = self.executions.first()

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.create.return_value = execution

        result = api.qinling.execution_delete(self.request, execution.id)
        self.assertIsNone(result)

        qclient.function_executions.delete.\
            assert_called_once_with(execution.id)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_execution_log_get(self, mock_qinlingclient):
        """Test for api.qinling.execution_log_get()"""
        execution = self.executions.first()
        log_contents = "this is log line."

        class FakeResponse(object):
            _content = log_contents

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.http_client.json_request.\
            return_value = FakeResponse(), "dummybody"

        result = api.qinling.execution_log_get(self.request, execution.id)
        self.assertEqual(result, log_contents)

        url = '/v1/executions/%s/log' % execution.id
        qclient.function_executions.http_client.\
            json_request.assert_called_once_with(url, 'GET')

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_executions_list(self, mock_qinlingclient):
        """Test for api.qinling.executions_list()"""
        executions = self.executions.list()

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.list.return_value = executions

        result = api.qinling.executions_list(self.request)
        self.assertItemsEqual(result, executions)

        qclient.function_executions.list.assert_called_once_with()

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_execution_get(self, mock_qinlingclient):
        """Test for api.qinling.execution_get()"""
        execution = self.executions.first()

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.get.return_value = execution

        result = api.qinling.execution_get(self.request, execution.id)
        self.assertEqual(result, execution)

        qclient.function_executions.get.assert_called_once_with(execution.id)

    # Function Versions
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_versions_list(self, mock_qinlingclient):
        """Test for api.qinling.versions_list()"""
        versions = self.versions.list()
        func = self.functions.first()

        this_function_id = func.id

        my_versions = [v for v in versions
                       if v.function_id == this_function_id]

        qclient = mock_qinlingclient.return_value
        qclient.function_versions.list.return_value = my_versions

        result = api.qinling.versions_list(self.request,
                                           this_function_id)
        self.assertItemsEqual(result, my_versions)

        qclient.function_versions.list.\
            assert_called_once_with(this_function_id)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_version_get(self, mock_qinlingclient):
        """Test for api.qinling.version_get()"""
        versions = self.versions.list()
        func = self.functions.first()

        this_function_id = func.id
        this_version_number = 1

        my_version = [v for v in versions
                      if v.function_id == this_function_id and
                      v.version_number == this_version_number][0]

        qclient = mock_qinlingclient.return_value
        qclient.function_versions.get.return_value = my_version

        result = api.qinling.version_get(self.request,
                                         this_function_id,
                                         this_version_number)
        self.assertEqual(result, my_version)

        qclient.function_versions.get.\
            assert_called_once_with(this_function_id, this_version_number)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_version_create(self, mock_qinlingclient):
        """Test for api.qinling.version_create()"""
        version = self.versions.first()
        func = self.functions.first()

        this_function_id = func.id

        qclient = mock_qinlingclient.return_value
        qclient.function_versions.create.return_value = version

        result = api.qinling.version_create(self.request,
                                            this_function_id,
                                            "description sample")
        self.assertEqual(result, version)

        qclient.function_versions.create.\
            assert_called_once_with(this_function_id, "description sample")
