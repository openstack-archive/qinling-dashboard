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

import copy

from django.core.files import uploadedfile

from django.http import response

from django.urls import reverse

from django.utils.http import urlunquote

from qinling_dashboard import api
from qinling_dashboard.content.functions import forms as project_fm
from qinling_dashboard.test import helpers as test
from qinling_dashboard.utils import calculate_md5

import mock

import six

INDEX_TEMPLATE = 'horizon/common/_data_table_view.html'
INDEX_URL = reverse('horizon:project:functions:index')
FULL_FORM = {
    "name": "",
    "description": "",
    "cpu": "",
    "memory_size": "",
    "code_type": "",
    "package_file": "",
    "runtime": "",
    "entry": "",
    "swift_container": "",
    "swift_object": "",
    "image": "",
}

FILE_CONTENT = six.b('DUMMY_FILE')


class FunctionsTests(test.TestCase):

    def _mock_function_version_list(self, mock_qinlingclient):

        data_functions = self.functions.list()

        def _versions_list_side_effect(function_id):
            all_versions = self.versions.list()
            my_versions = [v for v in all_versions
                           if v.function_id == function_id]
            return my_versions

        qclient = mock_qinlingclient.return_value

        # mock function_versions.list
        qclient.function_versions.list.side_effect = \
            _versions_list_side_effect

        # mock functions.list
        qclient.functions.list.return_value = data_functions

    def _create_temp_file(self):
        temp_file = uploadedfile.SimpleUploadedFile(
            name='aaaa.zip',
            content=FILE_CONTENT,
            content_type='application/zip',

        )
        return temp_file

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_update_image_case(self, mock_qinlingclient):
        """Test update function by image"""
        self._mock_function_version_list(mock_qinlingclient)

        func = self.functions.first()
        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = func
        qclient.functions.update.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        image = "dummy/image"

        form_data = {}
        form_data.update({
            "function_id": func.id,
            "name": "test_name",
            "description": "description",
            "cpu": project_fm.CPU_MIN_VALUE,
            "memory_size": project_fm.MEMORY_MIN_VALUE,
            "code_type": "image",
            "image": image,
        })

        url = reverse('horizon:project:functions:update', args=[func.id])
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        # create expected form data.
        actual_form_data = copy.deepcopy(form_data)

        del actual_form_data['code_type']
        del actual_form_data['function_id']
        del actual_form_data['image']

        qclient.functions.update.\
            assert_called_once_with(func.id, **actual_form_data)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_update_swift_case(self, mock_qinlingclient):
        """Test update function by swift"""
        self._mock_function_version_list(mock_qinlingclient)

        func = self.functions.first()
        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = func
        qclient.functions.update.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        swift_container = "dummy_container"
        swift_object = "dummy_object"

        form_data = {}
        form_data.update({
            "function_id": func.id,
            "name": "test_name",
            "description": "description",
            "cpu": project_fm.CPU_MIN_VALUE,
            "memory_size": project_fm.MEMORY_MIN_VALUE,
            "code_type": "swift",
            "entry_swift": "main.main",
            "swift_container": swift_container,
            "swift_object": swift_object,
        })

        url = reverse('horizon:project:functions:update', args=[func.id])
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        # create expected form data.
        actual_form_data = copy.deepcopy(form_data)

        del actual_form_data['code_type']
        del actual_form_data['function_id']
        del actual_form_data['entry_swift']

        del actual_form_data['swift_container']
        del actual_form_data['swift_object']

        qclient.functions.update.\
            assert_called_once_with(func.id, **actual_form_data)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_update_package_case_if_blank_value_is_correctly_handled(
            self, mock_qinlingclient):
        """Test update function by package

        check if blank string is correctly handled as meaning of
        'removing values'
        """
        self._mock_function_version_list(mock_qinlingclient)

        func = self.functions.first()
        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = func
        qclient.functions.update.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        form_data = {}
        form_data.update({
            "function_id": func.id,
            "name": "",
            "description": "",
            "cpu": "",
            "memory_size": "",
            "code_type": "package",
            "entry": "",
        })

        url = reverse('horizon:project:functions:update', args=[func.id])
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        # create expected form data.
        actual_form_data = copy.deepcopy(form_data)

        del actual_form_data['code_type']
        del actual_form_data['cpu']
        del actual_form_data['memory_size']
        del actual_form_data['function_id']

        qclient.functions.update.\
            assert_called_once_with(func.id, **actual_form_data)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_update_package_case(self, mock_qinlingclient):
        """Test update function by package"""
        self._mock_function_version_list(mock_qinlingclient)

        func = self.functions.first()
        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = func
        qclient.functions.update.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        temp_file = self._create_temp_file()

        form_data = {}
        form_data.update({
            "function_id": func.id,
            "name": "test_name",
            "description": "description",
            "cpu": project_fm.CPU_MIN_VALUE,
            "memory_size": project_fm.MEMORY_MIN_VALUE,
            "code_type": "package",
            "entry": "main.main",
            "package_file": temp_file,
        })

        url = reverse('horizon:project:functions:update', args=[func.id])
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        # create expected form data.
        actual_form_data = copy.deepcopy(form_data)

        del actual_form_data['code_type']
        del actual_form_data['package_file']
        del actual_form_data['function_id']
        actual_form_data.update({
            'package': FILE_CONTENT,
            'code': {'source': 'package',
                     'md5sum': calculate_md5(temp_file)}
        })

        qclient.functions.update.\
            assert_called_once_with(func.id, **actual_form_data)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_swift_case_no_runtime_specified(
            self, mock_qinlingclient):
        """Test error case of function creation

        Because no runtime is specified.
        """
        delete_key = ['runtime_swift']
        message = 'You must specify runtime.'
        self._function_create_swift_case_error(mock_qinlingclient,
                                               delete_key,
                                               message)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_swift_case_no_container_specified(
            self, mock_qinlingclient):
        """Test error case of function creation

        Because no swift container is specified.
        """
        delete_key = ['swift_container']
        message = 'You must specify container and object ' \
                  'both in case code type is Swift.'
        self._function_create_swift_case_error(mock_qinlingclient,
                                               delete_key,
                                               message)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_swift_case_no_object_specified(
            self, mock_qinlingclient):
        """Test error case of function creation

        Because no swift object is specified.
        """
        delete_key = ['swift_object']
        message = 'You must specify container and object ' \
                  'both in case code type is Swift.'
        self._function_create_swift_case_error(mock_qinlingclient,
                                               delete_key,
                                               message)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_swift_case_no_container_object_specified(
            self, mock_qinlingclient):
        """Test error case of function creation

        Because both swift container/object are not specified.
        """
        delete_key = ['swift_container', 'swift_object']
        message = 'You must specify container and object ' \
                  'both in case code type is Swift.'
        self._function_create_swift_case_error(mock_qinlingclient,
                                               delete_key,
                                               message)

    def _function_create_swift_case_error(self, mock_qinlingclient,
                                          delete_key=None, message=''):
        """Base function for function creation error test in swift case"""
        if not delete_key:
            delete_key = []

        self._mock_function_version_list(mock_qinlingclient)

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = self.functions.first()
        qclient.functions.create.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        form_data = copy.deepcopy(FULL_FORM)

        swift_container = "dummy_container"
        swift_object = "dummy_object"
        runtime_id = self.runtimes.first().id

        form_data.update({
            "name": "test_name",
            "description": "description",
            "cpu": project_fm.CPU_MIN_VALUE,
            "memory_size": project_fm.MEMORY_MIN_VALUE,
            "code_type": "swift",
            "swift_container": swift_container,
            "swift_object": swift_object,
            "runtime_swift": runtime_id,
        })

        for k in delete_key:
            if k in form_data:
                del form_data[k]

        url = reverse('horizon:project:functions:create')
        res = self.client.post(url, form_data)

        self.assertContains(res, message)
        qclient.functions.create.assert_not_called()

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_swift_case(self, mock_qinlingclient):
        """Test create function by swift container/object"""
        self._mock_function_version_list(mock_qinlingclient)

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = self.functions.first()
        qclient.functions.create.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        form_data = copy.deepcopy(FULL_FORM)

        swift_container = "dummy_container"
        swift_object = "dummy_object"
        runtime_id = self.runtimes.first().id

        form_data.update({
            "name": "test_name",
            "description": "description",
            "cpu": project_fm.CPU_MIN_VALUE,
            "memory_size": project_fm.MEMORY_MIN_VALUE,
            "code_type": "swift",
            "swift_container": swift_container,
            "swift_object": swift_object,
            "runtime_swift": runtime_id,
        })

        url = reverse('horizon:project:functions:create')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        # create expected form data.
        actual_form_data = copy.deepcopy(form_data)

        for k, v in form_data.items():
            if not v:
                del actual_form_data[k]
        del actual_form_data['code_type']
        del actual_form_data['swift_container']
        del actual_form_data['swift_object']

        # PIOST value "runtine_swift" to Horizon
        # will be set as "runtime" in POST value to Qinling.
        tmp_swift_runtime = form_data['runtime_swift']
        del actual_form_data['runtime_swift']
        actual_form_data.update({'runtime': tmp_swift_runtime})

        actual_form_data.update({
            'code': {
                'source': 'swift',
                'swift': {
                    'container': swift_container,
                    'object': swift_object,
                }
            }
        })

        qclient.functions.create.\
            assert_called_once_with(**actual_form_data)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_image_case_error(self, mock_qinlingclient):
        """Test error case of function creation from image.

        Error case because no image is specified.
        """
        self._mock_function_version_list(mock_qinlingclient)

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = self.functions.first()
        qclient.functions.create.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        form_data = copy.deepcopy(FULL_FORM)

        form_data.update({
            "name": "test_name",
            "description": "description",
            "cpu": project_fm.CPU_MIN_VALUE,
            "memory_size": project_fm.MEMORY_MIN_VALUE,
            "code_type": "image",
        })

        url = reverse('horizon:project:functions:create')
        res = self.client.post(url, form_data)

        self.assertContains(res, 'You must specify Docker image.')
        qclient.functions.create.assert_not_called()

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_image_case(self, mock_qinlingclient):
        """Test create function by image"""
        self._mock_function_version_list(mock_qinlingclient)

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = self.functions.first()
        qclient.functions.create.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        form_data = copy.deepcopy(FULL_FORM)

        image = "dummy/image"

        form_data.update({
            "name": "test_name",
            "description": "description",
            "cpu": project_fm.CPU_MIN_VALUE,
            "memory_size": project_fm.MEMORY_MIN_VALUE,
            "code_type": "image",
            "image": image
        })

        url = reverse('horizon:project:functions:create')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        # create expected form data.
        actual_form_data = copy.deepcopy(form_data)
        for k, v in form_data.items():
            if not v:
                del actual_form_data[k]
        del actual_form_data['code_type']
        del actual_form_data['image']
        actual_form_data.update({
            'code': {
                'source': 'image',
                'image': image
            }
        })

        qclient.functions.create.\
            assert_called_once_with(**actual_form_data)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_package_case(self, mock_qinlingclient):
        """Test create function by package"""
        self._mock_function_version_list(mock_qinlingclient)

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = self.functions.first()
        qclient.functions.create.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        runtime = self.runtimes.first()

        temp_file = self._create_temp_file()

        form_data = copy.deepcopy(FULL_FORM)
        form_data.update({
            "name": "test_name",
            "description": "description",
            "cpu": project_fm.CPU_MIN_VALUE,
            "memory_size": project_fm.MEMORY_MIN_VALUE,
            "code_type": "package",
            "runtime": runtime.id,
            "entry": "main.main",
            "package_file": temp_file,
        })

        url = reverse('horizon:project:functions:create')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        # create expected form data.
        actual_form_data = copy.deepcopy(form_data)
        for k, v in form_data.items():
            if not v:
                del actual_form_data[k]
        del actual_form_data['code_type']
        del actual_form_data['package_file']
        actual_form_data.update({
            'package': FILE_CONTENT,
            'code': {'source': 'package',
                     'md5sum': calculate_md5(temp_file)}
        })

        qclient.functions.create.\
            assert_called_once_with(**actual_form_data)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_package_case_with_least_params(
            self, mock_qinlingclient):
        """Test create function by package with least parameters"""
        self._mock_function_version_list(mock_qinlingclient)

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = self.functions.first()
        qclient.functions.create.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        runtime = self.runtimes.first()

        temp_file = self._create_temp_file()

        form_data = copy.deepcopy(FULL_FORM)
        form_data.update({
            "code_type": "package",
            "runtime": runtime.id,
            "package_file": temp_file,
        })

        url = reverse('horizon:project:functions:create')
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        # create expected form data.
        actual_form_data = copy.deepcopy(form_data)
        for k, v in form_data.items():
            if not v:
                del actual_form_data[k]
        del actual_form_data['code_type']
        del actual_form_data['package_file']
        actual_form_data.update({
            'package': FILE_CONTENT,
            'code': {'source': 'package',
                     'md5sum': calculate_md5(temp_file)}
        })

        qclient.functions.create.\
            assert_called_once_with(**actual_form_data)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_package_case_no_package_file_specified(
            self, mock_qinlingclient):
        """Error case of function creation from package

        Because no package_file is specified
        """
        delete_key = ['package_file']
        message = 'You must specify package file.'
        self._function_create_package_case_error(mock_qinlingclient,
                                                 delete_key,
                                                 message)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_create_package_case_no_runtime_specified(
            self, mock_qinlingclient):
        """Error case of function creation from package

        Because no runtime is specified
        """
        delete_key = ['runtime']
        message = 'You must specify runtime.'
        self._function_create_package_case_error(mock_qinlingclient,
                                                 delete_key,
                                                 message)

    def _function_create_package_case_error(
            self, mock_qinlingclient, delete_key=None, message=''):
        """Base function for testing function creation from package"""
        if not delete_key:
            delete_key = []

        self._mock_function_version_list(mock_qinlingclient)

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = self.functions.first()
        qclient.functions.create.return_value = self.functions.first()
        qclient.runtimes.list.return_value = self.runtimes.list()

        temp_file = self._create_temp_file()

        form_data = copy.deepcopy(FULL_FORM)
        form_data.update({
            "name": "test_name",
            "description": "description",
            "cpu": project_fm.CPU_MIN_VALUE,
            "memory_size": project_fm.MEMORY_MIN_VALUE,
            "code_type": "package",
            "entry": "main.main",
            "package_file": temp_file,
        })

        for k in delete_key:
            if k in form_data:
                del form_data[k]

        url = reverse('horizon:project:functions:create')
        res = self.client.post(url, form_data)

        self.assertContains(res, message)
        qclient.functions.create.assert_not_called()

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_version_delete(self, mock_qinlingclient):
        """Test function version delete"""
        function_id = self.functions.first().id
        version_id = self.versions.first().id
        version_number = self.versions.first().version_number

        self._mock_function_version_list(mock_qinlingclient)

        qclient = mock_qinlingclient.return_value
        qclient.function_versions.delete.return_value = None

        url = reverse('horizon:project:functions:detail', args=[function_id])
        url += '?tab=function_details__versions_of_this_function'

        form_data = {'action': 'function_versions__delete__%s' % version_id}
        res = self.client.post(url, form_data)

        self.assertRedirectsNoFollow(res, url)

        qclient.function_versions.delete.\
            assert_called_once_with(function_id, version_number)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_version_create(self, mock_qinlingclient):
        """Test function version create"""
        self._mock_function_version_list(mock_qinlingclient)

        function_id = self.functions.first().id

        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = self.functions.first()

        description_data = 'some description'
        form_data = {'function_id': function_id,
                     'description': description_data}

        url = reverse('horizon:project:functions:create_version',
                      args=[function_id])
        res = self.client.post(url, form_data)

        self.assertNoFormErrors(res)

        create_version_success_url = \
            reverse('horizon:project:functions:detail', args=[function_id])
        create_version_success_url += '?tab=function_details__' \
                                      'versions_of_this_function'
        self.assertRedirectsNoFollow(res, create_version_success_url)

        qclient.function_versions.create.\
            assert_called_once_with(function_id, description_data)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_download(self, mock_qinlingclient):
        """Test function download"""
        self._mock_function_version_list(mock_qinlingclient)

        function_id = self.functions.first().id

        qclient = mock_qinlingclient.return_value

        qclient.functions.get.return_value = \
            response.HttpResponse(content="DUMMY_DOWNLOAD_DATA")

        url = reverse('horizon:project:functions:download', args=[function_id])
        res = self.client.get(url)

        # res._headers[content-disposition] will be set like
        # ('Content-Disposition',
        #  'attachment; filename=qinling-function-<function_id>.zip')
        result_header = res._headers['content-disposition'][1]

        expected_header = \
            'attachment; filename=qinling-function-%s.zip' % function_id
        self.assertEqual(result_header, expected_header)
        qclient.functions.get.assert_called_once_with(function_id,
                                                      download=True)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_function_delete(self, mock_qinlingclient):
        """Test function delete"""
        function_id = self.functions.first().id

        self._mock_function_version_list(mock_qinlingclient)

        qclient = mock_qinlingclient.return_value
        qclient.functions.delete.return_value = None

        form_data = {'action': 'functions__delete__%s' % function_id}
        res = self.client.post(INDEX_URL, form_data)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        qclient.functions.delete.assert_called_once_with(function_id)

    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_index(self, mock_qinlingclient):
        """Test IndexView"""
        qclient = mock_qinlingclient.return_value

        self._mock_function_version_list(mock_qinlingclient)

        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, INDEX_TEMPLATE)
        result_functions = res.context['functions_table'].data
        api_functions = api.qinling.functions_list(self.request)

        calls = [(), ()]  # called twice, without any argument.
        self.assertItemsEqual(result_functions, api_functions)
        qclient.functions.list.assert_has_calls(calls)

    @test.create_mocks({
        api.qinling: [
            'functions_list',
        ]})
    def test_index_functions_list_returns_exception(self):
        """Test IndexView with exception from functions list"""

        self.mock_functions_list.side_effect = self.exceptions.qinling

        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, INDEX_TEMPLATE)

        self.assertEqual(len(res.context['functions_table'].data), 0)
        self.assertMessageCount(res, error=1)

        self.mock_functions_list.assert_has_calls(
            [
                mock.call(test.IsHttpRequest()),
            ])

    # Do not mock function_get directly to call set_code
    # so that function.code is converted into dict correctly.
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_detail(self, mock_qinlingclient):
        """Test DetailView"""
        function_id = self.functions.first().id
        qclient = mock_qinlingclient.return_value
        qclient.functions.get.return_value = self.functions.first()

        url = urlunquote(reverse('horizon:project:functions:detail',
                                 args=[function_id]))
        res = self.client.get(url)

        result_function = res.context['function']

        self.assertEqual(function_id, result_function.id)

        self.assertTemplateUsed(res, 'project/functions/detail.html')
        qclient.functions.get.assert_called_once_with(function_id)

    @test.create_mocks({
        api.qinling: [
            'function_get',
        ]})
    def test_detail_function_get_returns_exception(self):
        """Test DetailView with exception from function get"""
        function_id = self.functions.first().id
        self.mock_function_get.side_effect = self.exceptions.qinling

        url = urlunquote(reverse('horizon:project:functions:detail',
                                 args=[function_id]))

        res = self.client.get(url)

        redir_url = INDEX_URL
        self.assertRedirectsNoFollow(res, redir_url)

        self.mock_function_get.assert_has_calls(
            [
                mock.call(test.IsHttpRequest(), function_id),
            ])

    # Do not mock function_get directly to call set_code
    # so that function.code is converted into dict correctly.
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_detail_executions_tab(self, mock_qinlingclient):
        data_executions = self.executions.list()
        data_function = self.functions.first()
        function_id = data_function.id

        my_executions = [ex for ex in data_executions
                         if ex.function_id == function_id]

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.list.return_value = my_executions
        qclient.functions.get.return_value = data_function

        url_base = 'horizon:project:functions:detail_executions'
        url = urlunquote(reverse(url_base, args=[function_id]))
        res = self.client.get(url)

        result_executions = res.context['function_executions_table'].data

        self.assertTemplateUsed(res, 'project/functions/detail.html')
        self.assertEqual(my_executions, result_executions)

        qclient.functions.get.assert_called_once_with(function_id)

        calls = [mock.call(),
                 mock.call()]
        qclient.function_executions.list.assert_has_calls(calls)

    # Do not mock function_get directly to call set_code
    # so that function.code is converted into dict correctly.
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_detail_executions_tab_executions_list_returns_exception(
            self, mock_qinlingclient):
        data_function = self.functions.first()
        function_id = data_function.id

        qclient = mock_qinlingclient.return_value
        qclient.function_executions.list.side_effect = self.exceptions.qinling
        qclient.functions.get.return_value = data_function

        url_base = 'horizon:project:functions:detail_executions'
        url = urlunquote(reverse(url_base, args=[function_id]))
        res = self.client.get(url)

        result_executions = res.context['function_executions_table'].data

        self.assertTemplateUsed(res, 'project/functions/detail.html')
        self.assertEqual(len(result_executions), 0)

        qclient.functions.get.assert_called_once_with(function_id)

        calls = [mock.call(),
                 mock.call()]
        qclient.function_executions.list.assert_has_calls(calls)

    # Do not mock function_get directly to call set_code
    # so that function.code is converted into dict correctly.
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_detail_versions_tab(self, mock_qinlingclient):
        data_versions = self.versions.list()
        data_function = self.functions.first()
        function_id = data_function.id

        my_versions = [v for v in data_versions
                       if v.function_id == function_id]

        qclient = mock_qinlingclient.return_value
        qclient.function_versions.list.return_value = my_versions
        qclient.functions.get.return_value = data_function

        url_base = 'horizon:project:functions:detail_executions'
        url = urlunquote(reverse(url_base, args=[function_id]))
        res = self.client.get(url)

        result_versions = res.context['function_versions_table'].data

        self.assertTemplateUsed(res, 'project/functions/detail.html')
        self.assertEqual(my_versions, result_versions)

        qclient.functions.get.assert_called_once_with(function_id)

        calls = [mock.call(function_id,),
                 mock.call(function_id,)]
        qclient.function_versions.list.assert_has_calls(calls)

    # Do not mock function_get directly to call set_code
    # so that function.code is converted into dict correctly.
    @mock.patch.object(api.qinling, 'qinlingclient')
    def test_detail_versions_tab_versions_list_returns_exception(
            self, mock_qinlingclient):
        data_function = self.functions.first()
        function_id = data_function.id

        qclient = mock_qinlingclient.return_value
        qclient.function_versions.list.side_effect = self.exceptions.qinling
        qclient.functions.get.return_value = data_function

        url_base = 'horizon:project:functions:detail_executions'
        url = urlunquote(reverse(url_base, args=[function_id]))
        res = self.client.get(url)

        result_versions = res.context['function_versions_table'].data
        self.assertEqual(len(result_versions), 0)

        self.assertTemplateUsed(res, 'project/functions/detail.html')

        qclient.functions.get.assert_called_once_with(function_id)

        calls = [mock.call(function_id,),
                 mock.call(function_id,)]
        qclient.function_versions.list.assert_has_calls(calls)

    @test.create_mocks({
        api.qinling: [
            'version_get',
            'versions_list',
        ]})
    def test_version_detail(self):
        function_id = self.functions.first().id

        data_versions = self.versions.list()
        version_number = 1
        data_version = [v for v in data_versions
                        if v.function_id == function_id and
                        v.version_number == version_number][0]

        self.mock_version_get.return_value = data_version
        self.mock_versions_list.return_value = data_versions

        url = urlunquote(reverse('horizon:project:functions:version_detail',
                                 args=[function_id, version_number]))
        res = self.client.get(url)

        result_version = res.context['version']

        self.assertEqual(version_number, result_version.version_number)

        self.assertTemplateUsed(res, 'project/functions/detail_version.html')

        self.mock_version_get.assert_has_calls(
            [
                mock.call(test.IsHttpRequest(), function_id, version_number),
            ])
