# Copyright 2012 Nebula, Inc.
# All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.urls import reverse

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from qinling_dashboard import api

from qinling_dashboard.utils import calculate_md5

from qinling_dashboard import validators


CPU_MIN_VALUE = 100
CPU_MAX_VALUE = 300
MEMORY_MIN_VALUE = 33554432
MEMORY_MAX_VALUE = 134217728


CPU_HELP_TEXT = _("Limit of cpu resource(unit: millicpu). Range: {0} ~ {1}").\
    format(CPU_MIN_VALUE, CPU_MAX_VALUE)

MEMORY_HELP_TEXT = _("Limit of memory resource(unit: bytes). "
                     "Range: {0} ~ {1} (bytes).").format(MEMORY_MIN_VALUE,
                                                         MEMORY_MAX_VALUE)

UPLOAD_PACKAGE_LABEL = _('Package')
UPLOAD_SWIFT_CONTAINER_LABEL = _('Swift Container')
UPLOAD_SWIFT_OBJECT_LABEL = _('Swift Object')
UPLOAD_IMAGE_LABEL = _('Image')

CODE_TYPE_CHOICES = [('package', UPLOAD_PACKAGE_LABEL),
                     ('swift', UPLOAD_SWIFT_OBJECT_LABEL),
                     ('image', UPLOAD_IMAGE_LABEL)]


class CreateFunctionForm(forms.SelfHandlingForm):

    name = forms.CharField(max_length=255,
                           label=_("Name"),
                           validators=[validators.validate_one_line_string],
                           required=False)

    description = forms.CharField(
        max_length=255,
        widget=forms.Textarea(
            attrs={'class': 'modal-body-fixed-width',
                   'rows': 3}),
        label=_("Description"),
        required=False)

    cpu = forms.IntegerField(label=_("CPU"),
                             help_text=CPU_HELP_TEXT,
                             min_value=CPU_MIN_VALUE,
                             max_value=CPU_MAX_VALUE,
                             required=False)

    memory_size = forms.IntegerField(label=_("Memory Size"),
                                     help_text=MEMORY_HELP_TEXT,
                                     min_value=MEMORY_MIN_VALUE,
                                     max_value=MEMORY_MAX_VALUE,
                                     required=False)

    code_type = forms.ThemableChoiceField(
        label=_("Code Type"),
        help_text=_("Select Your Code Type."),
        widget=forms.ThemableSelectWidget(
            attrs={'class': 'switchable',
                   'data-slug': 'code_type'}
        ),
        choices=CODE_TYPE_CHOICES,
        required=True)

    package_file = forms.FileField(
        label=UPLOAD_PACKAGE_LABEL,
        help_text=_('Code package zip file path.'),
        widget=forms.FileInput(
            attrs={
                'class': 'switched',
                'data-switch-on': 'code_type',
                'data-code_type-package': UPLOAD_PACKAGE_LABEL,
            },
        ),
        required=False)

    entry = forms.CharField(
        label=_("Entry"),
        help_text=_('Function entry in the format of '
                    '<module_name>.<method_name>'),
        validators=[validators.validate_one_line_string],
        widget=forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'code_type',
            'data-code_type-package': _("Entry")
        }),
        required=False)

    runtime = forms.ThemableChoiceField(
        label=_("Runtime"),
        widget=forms.SelectWidget(attrs={
            'class': 'switched',
            'data-switch-on': 'code_type',
            'data-code_type-package': _("Runtime")
        }),
        required=False)

    swift_container = forms.CharField(
        label=UPLOAD_SWIFT_CONTAINER_LABEL,
        help_text=_('Container name in Swift.'),
        validators=[validators.validate_one_line_string],
        widget=forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'code_type',
            'data-code_type-swift': UPLOAD_SWIFT_CONTAINER_LABEL
        }),
        required=False)

    swift_object = forms.CharField(
        label=UPLOAD_SWIFT_OBJECT_LABEL,
        help_text=_('Object name in Swift.'),
        validators=[validators.validate_one_line_string],
        widget=forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'code_type',
            'data-code_type-swift': UPLOAD_SWIFT_OBJECT_LABEL
        }),
        required=False)

    entry_swift = forms.CharField(
        label=_("Entry"),
        help_text=_('Function entry in the format of '
                    '<module_name>.<method_name>'),
        validators=[validators.validate_one_line_string],
        widget=forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'code_type',
            'data-code_type-swift': _("Entry")
        }),
        required=False)

    runtime_swift = forms.ThemableChoiceField(
        label=_("Runtime"),
        widget=forms.SelectWidget(attrs={
            'class': 'switched',
            'data-switch-on': 'code_type',
            'data-code_type-swift': _("Runtime")
        }),
        required=False)

    image = forms.CharField(
        label=UPLOAD_IMAGE_LABEL,
        help_text=_('Image name in Docker hub.'),
        validators=[validators.validate_one_line_string],
        widget=forms.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'code_type',
            'data-code_type-image': UPLOAD_IMAGE_LABEL
        }),
        required=False)

    def get_runtime_choices(self, request):
        try:
            runtimes = api.qinling.runtimes_list(request)
        except Exception:
            runtimes = []
            exceptions.handle(request, _('Unable to retrieve runtimes.'))

        runtime_list = [(runtime.id, runtime.name) for runtime in runtimes
                        if runtime.status == 'available']

        runtime_list.sort()

        if not runtime_list:
            runtime_list.insert(0, ("", _("No runtimes found")))
        return runtime_list

    def __init__(self, request, *args, **kwargs):
        super(CreateFunctionForm, self).__init__(request, *args, **kwargs)
        runtime_choices = self.get_runtime_choices(request)
        self.fields['runtime'].choices = runtime_choices
        self.fields['runtime_swift'].choices = runtime_choices

    def _validation_for_swift_case(self, cleaned):
        swift_container = cleaned.get('swift_container', None)
        swift_object = cleaned.get('swift_object', None)
        if not all([swift_container, swift_object]):
            msg = _('You must specify container and object '
                    'both in case code type is Swift.')
            raise forms.ValidationError(msg)

        runtime = cleaned.get('runtime_swift', None)
        if not runtime:
            msg = _('You must specify runtime.')
            raise forms.ValidationError(msg)

    def _validation_for_image_case(self, cleaned):
        image = cleaned.get('image', None)
        if not image:
            msg = _('You must specify Docker image.')
            raise forms.ValidationError(msg)

    def _get_package_file(self, cleaned):
        package_file = cleaned.get('package_file', None)
        return package_file

    def _validation_for_package_case(self, cleaned):
        package_file = self._get_package_file(cleaned)

        if not package_file:
            msg = _('You must specify package file.')
            raise forms.ValidationError(msg)

        runtime = cleaned.get('runtime', None)
        if not runtime:
            msg = _('You must specify runtime.')
            raise forms.ValidationError(msg)

    def clean(self):
        cleaned = super(CreateFunctionForm, self).clean()

        code_type = cleaned['code_type']

        if code_type == 'package':
            self._validation_for_package_case(cleaned)

        if code_type == 'swift':
            self._validation_for_swift_case(cleaned)

        if code_type == 'image':
            self._validation_for_image_case(cleaned)

        return cleaned

    def handle_package_case(self, params, context, update=False):
        upload_files = self.request.FILES

        package = upload_files.get('package_file')
        md5sum = calculate_md5(package)
        code = {'source': 'package', 'md5sum': md5sum}

        # case1: creation case.
        #     Package upload is required in creation case.
        # case2: update case.
        #     In case update, package/code are only added
        #     when user specify them.
        if not update or (update and package):
            package = [ck for ck in package.chunks()][0]
            params.update({
                'package': package,
                'code': code,
            })

        if not update and context.get('runtime'):
            params.update({'runtime': context.get('runtime')})

        self._handle_entry_for_package(params, context, update)

    def _handle_entry_for_package(self, params, context, update=False):
        if update:
            params.update({'entry': context.get('entry')})
        else:
            if context.get('entry'):
                params.update({'entry': context.get('entry')})

    def handle_swift_case(self, params, context, update=False):
        swift_container = context.get('swift_container')
        swift_object = context.get('swift_object')

        if not update or all([not update, swift_container, swift_object]):
            code = {
                'source': 'swift',
                'swift': {
                    'container': swift_container,
                    'object': swift_object
                }
            }
            params.update({'code': code})

        if not update and context.get('runtime_swift'):
            params.update({'runtime': context.get('runtime_swift')})

        if not update and context.get('entry_swift'):
            params.update({'entry': context.get('entry_swift')})

    def handle_image_case(self, params, context, update=False):
        if not update or all([not update, context.get('image')]):
            code = {
                'source': 'image',
                'image': context.get('image')
            }
            params.update({'code': code})

    def handle(self, request, context):
        params = {}

        # basic parameters
        if context.get('name'):
            params.update({'name': context.get('name')})

        if context.get('description'):
            params.update({'description': context.get('description')})

        if context.get('cpu'):
            params.update({'cpu': int(context.get('cpu'))})

        if context.get('memory_size'):
            params.update({'memory_size': int(context.get('memory_size'))})

        code_type = context.get('code_type')

        if code_type == 'package':
            self.handle_package_case(params, context)

        elif code_type == 'swift':
            self.handle_swift_case(params, context)

        elif code_type == 'image':
            self.handle_image_case(params, context)

        try:
            api.qinling.function_create(request, **params)
            message = _('Created function "%s"') % params.get('name',
                                                              'unknown name')
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:functions:index")
            exceptions.handle(request,
                              _("Unable to create function."),
                              redirect=redirect)


class UpdateFunctionForm(CreateFunctionForm):

    function_id = forms.CharField(widget=forms.HiddenInput(),
                                  required=False)

    code_type = forms.ThemableChoiceField(
        label=_("Code Type"),
        help_text=_("Code Type can not be changed when you update function."),
        widget=forms.TextInput(
            attrs={'readonly': 'readonly'}
        ),
        choices=CODE_TYPE_CHOICES,
        required=True)

    # override this to skip
    def clean(self):
        cleaned = super(forms.SelfHandlingForm, self).clean()
        return cleaned

    def __init__(self, request, *args, **kwargs):
        super(UpdateFunctionForm, self).__init__(request, *args, **kwargs)

        code_type = self.initial.get('code_type')

        # written field names here will be regarded as updatable
        common_fields = ['name', 'description',
                         'code_type', 'function_id']
        available_fields = {
            'package': ['package_file', 'entry', 'cpu', 'memory_size'],
            'swift': [],
            'image': [],
        }
        available_fields = available_fields[code_type] + common_fields
        field_names = [fn for fn in self.fields.keys()]
        for field_name in field_names:
            if field_name not in available_fields:
                del self.fields[field_name]

    def handle(self, request, context):
        # basic parameters
        params = {
            'name': context.get('name', ''),
            'description': context.get('description', '')
        }

        if context.get('cpu'):
            params.update({'cpu': int(context.get('cpu'))})

        if context.get('memory_size'):
            params.update({'memory_size': int(context.get('memory_size'))})

        code_type = context.get('code_type')

        if code_type == 'package':
            self.handle_package_case(params, context, update=True)

        elif code_type == 'swift':
            self.handle_swift_case(params, context, update=True)

        elif code_type == 'image':
            self.handle_image_case(params, context, update=True)

        function_id = context['function_id']
        try:
            api.qinling.function_update(request, function_id, **params)
            message = _('Updated function "%s"') % params.get('name',
                                                              'unknown name')
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:functions:index")
            exceptions.handle(request,
                              _("Unable to update function %s") % function_id,
                              redirect=redirect)


class CreateFunctionVersionForm(forms.SelfHandlingForm):

    function_id = forms.CharField(
        label=_("Function ID"),
        help_text=_("Function which new version will be created."),
        widget=forms.TextInput(
            attrs={'readonly': 'readonly'}
        ),
        required=False)

    description = forms.CharField(
        max_length=255,
        widget=forms.Textarea(
            attrs={'class': 'modal-body-fixed-width',
                   'rows': 3}),
        label=_("Description"),
        required=False)

    def handle(self, request, data):
        try:
            function_id = data['function_id']
            description = data['description']
            api.qinling.version_create(request, function_id, description)
            message = _('Created new version of "%s"') % function_id
            messages.success(request, message)
            return True
        except Exception as e:
            redirect = reverse("horizon:project:functions:index")
            if hasattr(e, 'details'):
                msg = _("Unable to create execution. %s") % e.details
            else:
                msg = _("Unable to create execution")
            exceptions.handle(request, msg, redirect=redirect)
