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

import six

from django.conf import settings

from horizon.utils.memoized import memoized

from openstack_dashboard.api import base

from openstack_dashboard.contrib.developer.profiler import api as profiler

from qinlingclient import client as qinling_client


@memoized
def qinlingclient(request, password=None):
    api_version = "1"
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    endpoint = base.url_for(request, 'function-engine')
    kwargs = {
        'token': request.user.token.id,
        'insecure': insecure,
        'ca_file': cacert,
        'username': request.user.username,
        'password': password
    }
    client = qinling_client.Client(api_version, endpoint, **kwargs)
    return client


@profiler.trace
def runtimes_list(request):
    return qinlingclient(request).runtimes.list()


@profiler.trace
def runtime_get(request, runtime_id):
    return qinlingclient(request).runtimes.get(runtime_id)


def runtime_create(request, **params):
    resource = qinlingclient(request).runtimes.create(**params)
    return resource


def set_code(datum):
    if isinstance(datum.code, six.string_types):
        code_dict = json.loads(datum.code)
        setattr(datum, "code", code_dict)


@profiler.trace
def functions_list(request, with_version=False):
    functions = qinlingclient(request).functions.list()
    for f in functions:
        set_code(f)

    if with_version:
        for f in functions:
            function_id = f.id
            my_versions = \
                qinlingclient(request).function_versions.list(function_id)
            setattr(f, 'versions', my_versions)
    return functions


@profiler.trace
def function_get(request, function_id):
    function = qinlingclient(request).functions.get(function_id)
    set_code(function)
    return function


@profiler.trace
def function_create(request, **params):
    resource = qinlingclient(request).functions.create(**params)
    return resource


@profiler.trace
def function_update(request, function_id, **params):
    resource = qinlingclient(request).functions.update(function_id, **params)
    return resource


@profiler.trace
def function_delete(request, function_id):
    qinlingclient(request).functions.delete(function_id)


@profiler.trace
def function_download(request, function_id):
    function = qinlingclient(request).functions.get(function_id,
                                                    download=True)
    return function


def set_result(datum):
    if isinstance(datum.result, six.string_types):
        result_dict = json.loads(datum.result)
        setattr(datum, "result", result_dict)


@profiler.trace
def executions_list(request, function_id=None):
    executions = qinlingclient(request).function_executions.list()

    for e in executions:
        set_result(e)

    if function_id:
        executions = [e for e in executions
                      if e.function_id == function_id]
    return executions


@profiler.trace
def execution_get(request, execution_id):
    execution = qinlingclient(request).function_executions.get(execution_id)
    set_result(execution)
    return execution


@profiler.trace
def execution_create(request, function_id, version=0,
                     sync=True, input=None):
    execution = qinlingclient(request).function_executions.\
        create(function_id, version, sync, input)
    return execution


@profiler.trace
def execution_delete(request, execution_id):
    qinlingclient(request).function_executions.delete(execution_id)


@profiler.trace
def execution_log_get(request, execution_id):
    try:
        jr = qinlingclient(request).\
            function_executions.http_client.json_request
        resp, body = jr('/v1/executions/%s/log' % execution_id, 'GET')
        raw_logs = resp._content
    except Exception:
        raw_logs = ""
    return raw_logs


@profiler.trace
def versions_list(request, function_id):
    versions = qinlingclient(request).function_versions.list(function_id)
    return versions


@profiler.trace
def version_get(request, function_id, version_number):
    version = qinlingclient(request).function_versions.get(function_id,
                                                           version_number)
    return version


@profiler.trace
def version_create(request, function_id, description=""):
    version = qinlingclient(request).function_versions.create(function_id,
                                                              description)
    return version


@profiler.trace
def version_delete(request, function_id, version_number):
    qinlingclient(request).function_versions.delete(function_id,
                                                    version_number)
