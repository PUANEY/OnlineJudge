from django.conf.urls import url

from ..views.oj import TalkAPI, TalkCommentAPI, UserPubTalkAPI


urlpatterns = [
    url(r"^talk/?$", TalkAPI.as_view(), name="talk_api"),
    url(r"^talk_comment/?$", TalkCommentAPI.as_view(), name="talk_comment_api"),
    url(r"^user_pub_talk/?$", UserPubTalkAPI.as_view(), name="user_pub_talk_api"),
]