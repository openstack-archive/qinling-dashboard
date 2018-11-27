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

from django.utils.http import urlunquote

from qinling_dashboard import api
from qinling_dashboard.test import helpers as test

import mock


INDEX_TEMPLATE = 'horizon/common/_data_table_view.html'
INDEX_URL = reverse('horizon:project:runtimes:index')


class RuntimesTests(test.TestCase):

    @test.create_mocks({
        api.qinling: [
            'runtime_create',
        ]})
    def test_execution_create_with_maximum_params(self):
        data_runtime = self.runtimes.first()

        self.mock_runtime_create.return_value = data_runtime

        image_name = 'dummy/dockerimage'
        form_data = {'image': image_name,
                     'name': 'test_name',
                     'description': 'description',
                     'untrusted': 'on'}

        url = reverse('horizon:project:runtimes:create')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        self.mock_runtime_create.assert_called_once_with(
            test.IsHttpRequest(),
            image=image_name,
            name='test_name',
            description='description',
            trusted=False)

    @test.create_mocks({
        api.qinling: [
            'runtime_create',
        ]})
    def test_execution_create_with_minimum_params(self):
        data_runtime = self.runtimes.first()

        self.mock_runtime_create.return_value = data_runtime

        image_name = 'dummy/dockerimage'
        form_data = {'image': image_name}

        url = reverse('horizon:project:runtimes:create')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        self.mock_runtime_create.assert_called_once_with(
            test.IsHttpRequest(), image=image_name)

    @test.create_mocks({
        api.qinling: [
            'runtimes_list',
        ]})
    def test_index(self):
        data_runtimes = self.runtimes.list()
        self.mock_runtimes_list.return_value = data_runtimes

        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, INDEX_TEMPLATE)
        runtimes = res.context['runtimes_table'].data
        self.assertItemsEqual(runtimes, self.runtimes.list())

        self.mock_runtimes_list.assert_has_calls(
            [
                mock.call(test.IsHttpRequest()),
            ])

    @test.create_mocks({
        api.qinling: [
            'runtimes_list',
        ]})
    def test_index_runtimes_list_returns_exception(self):
        self.mock_runtimes_list.side_effect = self.exceptions.qinling

        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, INDEX_TEMPLATE)

        self.assertEqual(len(res.context['runtimes_table'].data), 0)
        self.assertMessageCount(res, error=1)

        self.mock_runtimes_list.assert_has_calls(
            [
                mock.call(test.IsHttpRequest()),
            ])

    @test.create_mocks({
        api.qinling: [
            'runtime_get',
        ]})
    def test_detail(self):
        runtime_id = self.runtimes.first().id
        self.mock_runtime_get.return_value = self.runtimes.first()

        url = urlunquote(reverse('horizon:project:runtimes:detail',
                                 args=[runtime_id]))
        res = self.client.get(url)

        result_runtime = res.context['runtime']

        self.assertEqual(runtime_id, result_runtime.id)

        self.assertTemplateUsed(res, 'project/runtimes/detail.html')

        self.mock_runtime_get.assert_has_calls(
            [
                mock.call(test.IsHttpRequest(), runtime_id),
            ])

    @test.create_mocks({
        api.qinling: [
            'runtime_get',
        ]})
    def test_detail_runtime_get_returns_exception(self):
        runtime_id = self.runtimes.first().id
        self.mock_runtime_get.side_effect = self.exceptions.qinling

        url = urlunquote(reverse('horizon:project:runtimes:detail',
                                 args=[runtime_id]))

        res = self.client.get(url)

        redir_url = INDEX_URL
        self.assertRedirectsNoFollow(res, redir_url)

        self.mock_runtime_get.assert_has_calls(
            [
                mock.call(test.IsHttpRequest(), runtime_id),
            ])
