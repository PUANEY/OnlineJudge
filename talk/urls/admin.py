from django.conf.urls import url

from ..views.admin import TalkAdminAPI, TalkAdminCommentAPI


urlpatterns = [
    url(r"^talk_manage/?$", TalkAdminAPI.as_view(), name="talk_manage_api"),
    url(r"^talk_comment_manage/?$", TalkAdminCommentAPI.as_view(), name="talk_comment_manage_api"),
]