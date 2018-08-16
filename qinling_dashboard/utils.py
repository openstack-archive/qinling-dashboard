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

# This file is to be included for configuring application which relates
# to orchestration(Heat) functions.

import hashlib
import json

from django.utils.translation import pgettext_lazy


def calculate_md5(target):
    if not target:
        return ''

    md5 = hashlib.md5()
    for chunk in target.chunks():
        md5.update(chunk)

    return md5.hexdigest()


def convert_raw_input_to_api_format(value):
    if value == '':
        return None

    value = value.replace('\r\n', '\n')
    data = value.split('\n')
    input_dict = {}
    for datum in data:
        if datum == "":
            continue
        k, v = datum.split('=')
        input_dict.update({k: v})
    inp = json.dumps(input_dict)
    return inp


FUNCTION_ENGINE_STATUS_CHOICES = (
    ("Creating", None),
    ("Available", True),
    ("Upgrading", True),
    ("Error", False),
    ("Deleting", None),
    ("Running", None),
    ("Done", True),
    ("Paused", True),
    ("Cancelled", True),
    ("Success", True),
    ("Failed", False),
)


FUNCTION_ENGINE_STATUS_DISPLAY_CHOICES = (
    ("creating", pgettext_lazy("current status of runtime", u"Creating")),
    ("available",
     pgettext_lazy("current status of runtime", u"Available")),
    ("upgrading",
     pgettext_lazy("current status of runtime", u"Upgrading")),
    ("error", pgettext_lazy("current status of runtime", u"Error")),
    ("deleting", pgettext_lazy("current status of runtime", u"Deleting")),
    ("running", pgettext_lazy("current status of runtime", u"Running")),
    ("done", pgettext_lazy("current status of runtime", u"Done")),
    ("paused", pgettext_lazy("current status of runtime", u"Paused")),
    ("cancelled",
     pgettext_lazy("current status of runtime", u"Cancelled")),
    ("success", pgettext_lazy("current status of runtime", u"Success")),
    ("failed", pgettext_lazy("current status of runtime", u"Failed")),
)
