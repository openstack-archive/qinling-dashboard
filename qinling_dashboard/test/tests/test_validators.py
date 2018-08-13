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

import unittest

from django.core.exceptions import ValidationError

from qinling_dashboard import validators


def provider_validate_key_value_pairs():
    provider = list()

    # blank check
    empty_row = [
        # blank string
        {'d': u'', 'raise': False},
        # multiple lines consist of blank string
        {'d': u'\n\n\n\n\n\n\n\n\n\n\n', 'raise': False},
        # multiple lines consist of blank string + valid row
        {'d': u'\n\n\n\n\n\n\n\n\n\n\nkey=value', 'raise': False},
        # multiple lines consist of blank string + valid row
        #  + multiple lines consist of blank string
        {'d': u'\n\n\n\n\n\n\n\n\n\n\nkey=value\n\n', 'raise': False},
    ]
    provider += empty_row

    # key part check

    # consist of valid character case
    key_check_normal = [
        # lower limit
        {'d': u'k=v', 'raise': False},
        # upper limit
        {'d': u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
              u'6789!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstu'
              u'vwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;'
              u'<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQR'
              u'STUVWXYZ0123456789!"#$%=v', 'raise': False},
        # upper limit +1
        {'d': u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567'
              u'89!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxy'
              u'zABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@'
              u'[\]^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWX'
              u'YZ0123456789!"#$%A=v', 'raise': True},
    ]
    provider += key_check_normal

    # key has initial blank string
    key_check_starts_space = [
        {'d': u' =v', 'raise': True},
        # upper limit
        {'d': u' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567'
              u'89!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzA'
              u'BCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]^'
              u'_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123'
              u'456789!"#$=v', 'raise': True},
        # upper limit + 1
        {'d': u' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345678'
              u'9!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzAB'
              u'CDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]^_'
              u'`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234'
              u'56789!"#$A=v', 'raise': True},
    ]
    provider += key_check_starts_space

    # key has last blank string
    key_check_normal = [
        # upper limit
        {'d': u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345678'
              u'9!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzA'
              u'BCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]'
              u'^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01'
              u'23456789!"#$ =v', 'raise': True},
        # upper limit + 1
        {'d': u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345678'
              u'9!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzA'
              u'BCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]'
              u'^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01'
              u'23456789!"#$% =v', 'raise': True},
    ]
    provider += key_check_normal

    # key has blank string in the middle of it
    key_check_middle_space = [
        # upper limit
        {'d': u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345678'
              u'9 !"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyz'
              u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]'
              u'^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012'
              u'3456789!"#$=v', 'raise': False},
        # upper limit + 1
        {'d': u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
              u' !"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzAB'
              u'CDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]^_'
              u'`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234'
              u'56789!"#$A=v', 'raise': True},
    ]
    provider += key_check_middle_space

    # check for key part
    no_key = [
        {'d': u'=v', 'raise': True},
    ]
    provider += no_key

    # equal part check
    equal_check = [
        # no equal
        {'d': 'key1value1', 'raise': True},
        # multiple equal in it
        {'d': 'key=value=key\n', 'raise': True},
    ]
    provider += equal_check

    # check for value part

    # consist of valid charcters
    value_check_normal = [
        # upper limit
        {'d': u'k=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567'
              u'89!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzA'
              u'BCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]^'
              u'_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123'
              u'456789!"#$%', 'raise': False},
        # upper limit + 1
        {'d': u'k=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567'
              u'89!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzA'
              u'BCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]^'
              u'_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123'
              u'456789!"#$%A', 'raise': True},
    ]
    provider += value_check_normal

    # value has initial blank
    value_check_starts_space = [
        {'d': u'k= ', 'raise': True},
        # upper limit
        {'d': u'k= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456'
              u'789!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyz'
              u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]'
              u'^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012'
              u'3456789!"#$', 'raise': True},
        # upper limit + 1
        {'d': u'k= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456'
              u'789!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyz'
              u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@[\]'
              u'^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012'
              u'3456789!"#$A', 'raise': True},
    ]
    provider += value_check_starts_space

    # value has last blank
    value_check_normal = [
        # upper limit
        {'d': u'k=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456'
              u'789!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxy'
              u'zABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@'
              u'[\]^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWX'
              u'YZ0123456789!"#$ ', 'raise': True},
        # upper limit + 1
        {'d': u'k=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456'
              u'789!"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxy'
              u'zABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F>?@'
              u'[\]^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWX'
              u'YZ0123456789!"#$% ', 'raise': True},
    ]
    provider += value_check_normal

    # value has middle blank
    value_check_middle_space = [
        # upper limit
        {'d': u'k=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
              u'6789 !"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuv'
              u'wxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F'
              u'>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTU'
              u'VWXYZ0123456789!"#$', 'raise': False},
        # upper limit + 1
        {'d': u'k=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
              u'6789 !"#$%&\'()*+,-./:;<F>?@[\]^_`{|}~abcdefghijklmnopqrstuv'
              u'wxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<F'
              u'>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTU'
              u'VWXYZ0123456789!"#$A', 'raise': True},
    ]
    provider += value_check_middle_space

    # no value is specified
    no_value = [
        {'d': u'k=', 'raise': True},
    ]
    provider += no_value

    return provider


def provider_validate_one_line_string():
    return [

        # Threshold check for number of charaters

        # lower limit - 1
        {'d': u'', 'raise': True},
        # lower limit
        {'d': u'a', 'raise': False},
        # upper limit
        {'d': u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ012345"
              u"6789!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ abcdefghijklmnopqrst"
              u"uvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456789!\"#$%&'()*+,-./:"
              u";<=>?@[\]^_`{|}~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOP"
              u"QRSTUVwXYZ0123456789!\"#",
         'raise': False},
        # upper limit + 1
        {'d': u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ012345"
              u"6789!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ abcdefghijklmnopqrst"
              u"uvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456789!\"#$%&'()*+,-./"
              u":;<=>?@[\]^_`{|}~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN"
              u"OPQRSTUVwXYZ0123456789!\"#$",
         'raise': True},

        # initial character is blank

        # lower limit
        {'d': u' ', 'raise': True},
        # upper limit
        {'d': u" bcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ01234567"
              u"89!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ abcdefghijklmnopqrstuvwx"
              u"yzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456789!\"#$%&'()*+,-./:;<=>?"
              u"@[\]^_`{|}~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV"
              u"wXYZ0123456789!\"#",
         'raise': True},
        # upper limit + 1
        {'d': u" bcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456"
              u"789!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ abcdefghijklmnopqrstuv"
              u"wxyzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456789!\"#$%&'()*+,-./:;<"
              u"=>?@[\]^_`{|}~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQR"
              u"STUVwXYZ0123456789!\"#a",
         'raise': True},

        # last character is blank

        # upper limit
        {'d': u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456"
              u"789!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ abcdefghijklmnopqrstuv"
              u"wxyzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456789!\"#$%&'()*+,-./:;<"
              u"=>?@[\]^_`{|}~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQR"
              u"STUVwXYZ0123456789!\" """,
         'raise': True},
        # upper limit + 1
        {'d': u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456"
              u"789!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ abcdefghijklmnopqrstuv"
              u"wxyzABCDEFGHIJKLMNOPQRSTUVwXYZ0123456789!\"#$%&'()*+,-./:;<"
              u"=>?@[\]^_`{|}~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQR"
              u"STUVwXYZ0123456789!\"# """,
         'raise': True},

    ]


class ValidatorsTests(unittest.TestCase):

    def test_validate_metadata(self, data=provider_validate_key_value_pairs()):
        for datum in data:

            d = datum.get('d')
            raise_expected = datum.get('raise')

            if raise_expected:
                self.assertRaises(ValidationError,
                                  validators.validate_key_value_pairs, d)
            else:
                self.assertIsNone(validators.validate_key_value_pairs(d))

    def test_validate_openstack_string(
            self, data=provider_validate_one_line_string()):
        for datum in data:

            d = datum.get('d')
            raise_expected = datum.get('raise')

            if raise_expected:
                self.assertRaises(ValidationError,
                                  validators.validate_one_line_string, d)
            else:
                self.assertIsNone(validators.validate_one_line_string(d))
