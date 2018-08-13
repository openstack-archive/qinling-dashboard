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

from django.conf.urls import url

from qinling_dashboard.content.functions import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create', views.CreateFunctionView.as_view(), name='create'),
    url(r'^(?P<function_id>[^/]+)/update',
        views.UpdateFunctionView.as_view(), name='update'),
    url(r'^(?P<function_id>[^/]+)/download/$',
        views.download_function, name='download'),
    url(r'^(?P<function_id>[^/]+)/versions/create',
        views.CreateFunctionVersionView.as_view(), name='create_version'),
    url(r'^(?P<function_id>[^/]+)/versions/(?P<version_number>[^/]+)/$',
        views.VersionDetailView.as_view(), name='version_detail'),
    url(r'^(?P<function_id>[^/]+)/functions/create_execution',
        views.CreateFunctionExecutionView.as_view(), name='create_execution'),
    # detail
    url(r'^(?P<function_id>[^/]+)/$',
        views.DetailView.as_view(), name='detail'),
    # detail(tab=executions)
    url(r'^(?P<function_id>[^/]+)/'
        r'\?tab=function_details_executions_of_this_function$',
        views.DetailView.as_view(), name='detail_executions'),
    # detail(tab=versions)
    url(r'^(?P<function_id>[^/]+)/'
        r'\?tab=function_details_versions_of_this_function$',
        views.DetailView.as_view(), name='detail_versions'),
]
