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

import re

from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _


STRING_VALIDATE_PATTERN = \
    """[a-zA-Z0-9\$\[\]\(\)\{\}\*\+\?\^\s\|\.\-\\\\!#%&'",/:;=<>@_`~]"""

MAX_LENGTH = 255


def validate_1st_space(value):
    """Raise execption if 1st character is blank(space)"""
    if re.match('^\s', value):
        raise ValidationError(_("1st character is not valid."))


def validate_last_space(value):
    """Raise execption if last character is blank(space)"""
    if re.search('\s$', value):
        raise ValidationError(_("Last character is not valid."))


def validate_one_line_string(value):
    """Validate if invalid charcter is included in value.

    Followings are regarded as valid.
    - length <= 255
    - consist of
         abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456789"
         !#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    """
    base_pattern = STRING_VALIDATE_PATTERN
    pattern = '^%s{1,%s}$' % (base_pattern, MAX_LENGTH)
    if not re.match(pattern, value):
        raise ValidationError(_('Invalid character is used '
                                'or exceeding maximum length.'))
    validate_1st_space(value)
    validate_last_space(value)


def validate_key_value_pairs(value):
    """Validation logic for execution input.

    Check if value has u'A=B\r\nC=D...' format.
    """
    value = value.replace('\r\n', '\n')
    data = value.split('\n')
    pattern = '^[^=]+=[^=]+$'

    for datum in data:
        # Skip validation if value is blank
        if datum == '':
            continue

        if re.match(pattern, datum) is None:
            raise ValidationError(_('Not key-value pair.'))

        metadata_key, metadata_value = datum.split('=')

        # Check key, value both by using validation logic for one line string.
        validate_one_line_string(metadata_key)
        validate_one_line_string(metadata_value)
