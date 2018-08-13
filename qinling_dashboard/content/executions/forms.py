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

"""
Views for managing volumes.
"""

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from qinling_dashboard import api
from qinling_dashboard import utils as q_utils
from qinling_dashboard import validators


class CreateExecutionForm(forms.SelfHandlingForm):

    func = forms.ChoiceField(
        label=_("Function"),
        help_text=_("Function to execute."),
        required=True)

    version = forms.IntegerField(
        label=_("Version"),
        required=False,
        initial=0
    )

    sync = forms.BooleanField(
        label=_("Sync"),
        required=False,
        help_text=_("Check this item if you would like sync execution."),
        initial=True
    )

    input_params = forms.CharField(
        label=_('Input'),
        help_text=_('Specify input parmeters like name1=value2. '
                    'One line is equivalent of one input parameter.'),
        validators=[validators.validate_key_value_pairs],
        widget=forms.widgets.Textarea(),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateExecutionForm, self).__init__(request, *args, **kwargs)
        self.fields['func'].choices = self.get_func_choices(request)

        try:
            if 'function_id' in request.GET and 'version' in request.GET:
                self.prepare_source_fields_if_function_specified(request)
        except Exception:
            pass

    def prepare_source_fields_if_function_specified(self, request):
        try:
            function_id = request.GET['function_id']
            func = api.qinling.function_get(request, function_id)

            self.fields['func'].choices = [(function_id, func.name or func.id)]
            self.fields['func'].initial = function_id

            self.fields['version'].initial = request.GET['version']
        except Exception:
            msg = _('Unable to load the specified function. %s')
            exceptions.handle(request, msg % request.GET['function_id'])

    def clean(self):
        cleaned = super(CreateExecutionForm, self).clean()
        version_number = cleaned.get('version')

        # version number is not specified or specified as zero.
        if not version_number:
            return cleaned

        function_id = cleaned.get('func')

        versions = api.qinling.versions_list(self.request, function_id)

        # in case versions are returned as empty array.
        if not versions and not version_number:
            return cleaned

        available_versions = [v.version_number for v in versions]
        if version_number not in available_versions:
            msg = _('This function does not '
                    'have specified version number: %s') % version_number
            raise forms.ValidationError(msg)

        return cleaned

    def get_func_choices(self, request):
        try:
            functions = api.qinling.functions_list(request)
        except Exception:
            functions = []

        function_choices = [(f.id, f.name or f.id) for f in functions]
        if len(function_choices) == 0:
            function_choices = [('', _('No functions available.'))]
        return function_choices

    def handle(self, request, data):
        try:
            function_id = data['func']
            version = int(data['version'])
            sync = data['sync']
            inp = \
                q_utils.convert_raw_input_to_api_format(data['input_params'])
            api.qinling.execution_create(request, function_id, version,
                                         sync, inp)
            message = _('Created execution of "%s"') % function_id
            messages.success(request, message)
            return True
        except Exception as e:
            redirect = reverse("horizon:project:executions:index")
            exceptions.handle(request,
                              _("Unable to create execution. %s") % e,
                              redirect=redirect)
