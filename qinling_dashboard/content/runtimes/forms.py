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

# from qinling_dashboard.utils import calculate_md5

from qinling_dashboard import validators


class CreateRuntimeForm(forms.SelfHandlingForm):

    image = forms.CharField(max_length=255,
                            label=_("Image"),
                            validators=[validators.validate_one_line_string],
                            required=True)

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

    untrusted = forms.BooleanField(
        label=_("Create as Untrusted Image"),
        required=False,
        help_text=_("Check this item if you would like to "
                    "create untrusted runtime"),
        initial=False
    )

    def __init__(self, request, *args, **kwargs):
        super(CreateRuntimeForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, context):
        params = {}

        # basic parameters
        params.update({'image': context.get('image')})

        if context.get('name'):
            params.update({'name': context.get('name')})

        if context.get('description'):
            params.update({'description': context.get('description')})

        if context.get('untrusted'):
            trusted = not bool(context.get('untrusted'))
            params.update({'trusted': trusted})

        try:
            api.qinling.runtime_create(request, **params)
            message = _('Created runtime "%s"') % params.get('name',
                                                             'unknown name')
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:runtimes:index")
            exceptions.handle(request,
                              _("Unable to create runtime."),
                              redirect=redirect)
