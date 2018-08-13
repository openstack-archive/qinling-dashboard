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

import json

import mock

from django.urls import reverse

from django.utils.http import urlunquote

from qinling_dashboard import api

from qinling_dashboard.test import helpers as test


INDEX_TEMPLATE = 'horizon/common/_data_table_view.html'
INDEX_URL = reverse('horizon:project:executions:index')


class ExecutionsTests(test.TestCase):

    @test.create_mocks({
        api.qinling: [
            'executions_list',
            'execution_delete',
        ]})
    def test_execution_delete(self):
        data_executions = self.executions.list()
        data_execution = self.executions.first()
        execution_id = data_execution.id

        self.mock_executions_list.return_value = data_executions
        self.mock_execution_delete.return_value = None

        form_data = {'action': 'executions__delete__%s' % execution_id}
        res = self.client.post(INDEX_URL, form_data)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        self.mock_execution_delete.assert_called_once_with(
            test.IsHttpRequest(), execution_id)

    @test.create_mocks({
        api.qinling: [
            'execution_create',
            'functions_list',
            'function_get',
            'versions_list',
        ]})
    def test_execution_create(self):
        data_execution = self.executions.first()

        data_functions = self.functions.list()

        data_function = self.functions.first()
        function_id = data_function.id

        data_versions = self.versions.list()
        my_versions = [v for v in data_versions
                       if v.function_id == function_id]

        self.mock_versions_list.return_value = data_versions
        self.mock_function_get.return_value = data_function
        self.mock_functions_list.return_value = data_functions
        self.mock_execution_create.return_value = data_execution
        self.mock_versions_list.return_value = my_versions

        form_data = {'func': function_id,
                     'version': 0,
                     'sync': True,
                     'input_params': 'K1=V1\nK2=V2'}

        url = reverse('horizon:project:executions:create')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        input_dict = {'K1': 'V1', 'K2': 'V2'}
        input_params = json.dumps(input_dict)

        self.mock_execution_create.assert_called_once_with(
            test.IsHttpRequest(), function_id, 0, True, input_params)

    @test.create_mocks({
        api.qinling: [
            'execution_create',
            'functions_list',
            'function_get',
            'versions_list',
        ]})
    def test_execution_create_function_input_params_is_not_key_value(self):

        data_functions = self.functions.list()

        data_function = self.functions.first()
        function_id = data_function.id

        data_versions = self.versions.list()
        my_versions = [v for v in data_versions
                       if v.function_id == function_id]

        self.mock_versions_list.return_value = data_versions
        self.mock_function_get.return_value = data_function
        self.mock_functions_list.return_value = data_functions
        self.mock_versions_list.return_value = my_versions

        form_data = {'func': function_id,
                     'version': 0,
                     'sync': True,
                     'input_params': 'K1=V1\nK2='}

        url = reverse('horizon:project:executions:create')
        res = self.client.post(url, form_data)

        expected_msg = "Not key-value pair."
        self.assertContains(res, expected_msg)

    @test.create_mocks({
        api.qinling: [
            'execution_create',
            'functions_list',
            'function_get',
            'versions_list',
        ]})
    def test_execution_create_function_version_does_not_exist(self):

        data_functions = self.functions.list()

        data_function = self.functions.first()
        function_id = data_function.id

        data_versions = self.versions.list()
        my_versions = [v for v in data_versions
                       if v.function_id == function_id]

        self.mock_versions_list.return_value = data_versions
        self.mock_function_get.return_value = data_function
        self.mock_functions_list.return_value = data_functions
        self.mock_versions_list.return_value = my_versions

        invalid_version = 10
        form_data = {'func': function_id,
                     'version': invalid_version,
                     'sync': True,
                     'input_params': ""}

        url = reverse('horizon:project:executions:create')
        res = self.client.post(url, form_data)

        expected_msg = "This function does not " \
                       "have specified version number: %s" % invalid_version
        self.assertContains(res, expected_msg)

    @test.create_mocks({
        api.qinling: [
            'execution_create',
            'functions_list',
            'function_get',
            'versions_list',
        ]})
    def test_execution_create_function_id_is_not_in_choices(self):

        data_functions = self.functions.list()

        data_function = self.functions.first()
        function_id = data_function.id

        data_versions = self.versions.list()
        my_versions = [v for v in data_versions
                       if v.function_id == function_id]

        self.mock_versions_list.return_value = data_versions
        self.mock_function_get.return_value = data_function
        self.mock_functions_list.return_value = data_functions
        self.mock_versions_list.return_value = my_versions

        form_data = {'func': function_id + 'a',  # function does not exist
                     'version': 0,
                     'sync': True,
                     'input_params': ""}

        url = reverse('horizon:project:executions:create')
        res = self.client.post(url, form_data)

        expected_msg = \
            "%s is not one of the available choices." % (function_id + 'a')
        self.assertContains(res, expected_msg)

    # You should not mock api.qinling.executions_list/get itself here,
    # because inside of executions_list, execution.result is converted
    # from str to dict.
    # If you mock everything about this executions_list, above conversion
    # method won't be called then it causes error in table rendering.
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_index(self, mock_qinlingclient):
        data_executions = self.executions.list()

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.list.return_value = data_executions

        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, INDEX_TEMPLATE)
        executions = res.context['executions_table'].data
        self.assertItemsEqual(executions, self.executions.list())

        qclient.function_executions.list.assert_called_once_with()

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_index_executions_list_returns_exception(self, mock_qinlingclient):
        # data_executions = self.executions.list()

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.list.side_effect = self.exceptions.qinling

        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, INDEX_TEMPLATE)

        self.assertEqual(len(res.context['executions_table'].data), 0)
        self.assertMessageCount(res, error=1)

        qclient.function_executions.list.assert_called_once_with()

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_detail(self, mock_qinlingclient):
        execution_id = self.executions.first().id
        data_execution = self.executions.first()

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.get.return_value = data_execution

        url = urlunquote(reverse('horizon:project:executions:detail',
                                 args=[execution_id]))
        res = self.client.get(url)

        result_execution = res.context['execution']

        self.assertEqual(execution_id, result_execution.id)

        self.assertTemplateUsed(res, 'project/executions/detail.html')

        qclient.function_executions.get.assert_called_once_with(execution_id)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_detail_execution_get_returns_exception(self, mock_qinlingclient):
        execution_id = self.executions.first().id

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.get.side_effect = self.exceptions.qinling

        url = urlunquote(reverse('horizon:project:executions:detail',
                                 args=[execution_id]))
        res = self.client.get(url)

        redir_url = INDEX_URL
        self.assertRedirectsNoFollow(res, redir_url)

        qclient.function_executions.get.assert_called_once_with(execution_id)

    @test.create_mocks({
        api.qinling: [
            'execution_get',
            'execution_log_get',
        ]})
    def test_detail_execution_log_tab(self):
        execution_id = self.executions.first().id
        log_contents = "this is log line."

        self.mock_execution_get.return_value = self.executions.first()
        self.mock_execution_log_get.return_value = log_contents

        url_base = 'horizon:project:executions:detail_execution_logs'
        url = urlunquote(reverse(url_base, args=[execution_id]))
        res = self.client.get(url)

        result_logs = res.context['execution_logs']

        self.assertTemplateUsed(res, 'project/executions/detail.html')
        self.assertEqual(log_contents, result_logs)

        self.mock_execution_get.assert_has_calls(
            [
                mock.call(test.IsHttpRequest(), execution_id),
            ])
        self.mock_execution_log_get.assert_has_calls(
            [
                mock.call(test.IsHttpRequest(), execution_id),
            ])

    @test.create_mocks({
        api.qinling: [
            'execution_get',
            'execution_log_get',
        ]})
    def test_detail_execution_log_tab_log_get_returns_exception(self):
        execution_id = self.executions.first().id

        self.mock_execution_get.return_value = self.executions.first()
        self.mock_execution_log_get.side_effect = self.exceptions.qinling

        url_base = 'horizon:project:executions:detail_execution_logs'
        url = urlunquote(reverse(url_base, args=[execution_id]))
        res = self.client.get(url)

        result_logs = res.context['execution_logs']

        self.assertTemplateUsed(res, 'project/executions/detail.html')

        self.assertEqual(result_logs, "")

        self.mock_execution_get.assert_has_calls(
            [
                mock.call(test.IsHttpRequest(), execution_id),
            ])
        self.mock_execution_log_get.assert_has_calls(
            [
                mock.call(test.IsHttpRequest(), execution_id),
            ])
