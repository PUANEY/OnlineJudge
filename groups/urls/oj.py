from django.conf.urls import url

from ..views.oj import (SearchGroupByKeyWordAPI,
                        JoinGroupBySearchAPI,
                        GroupListAndDetailAPI,
                        HomeWorkListAndDetailAPI
                        )

urlpatterns = [
    url(r"^search_group/?$", SearchGroupByKeyWordAPI.as_view(), name="search_group_api"),
    url(r"^join_group/?$", JoinGroupBySearchAPI.as_view(), name="join_group_api"),
    url(r"^groups/?$", GroupListAndDetailAPI.as_view(), name="group_api"),
    url(r"^homework/?$", HomeWorkListAndDetailAPI.as_view(), name="homework_api"),
]