from ..serializers import TalkSerializers, TalkCommentSerializers
from ..models import TalkModel, TalkCommentModel
from utils.api import APIView
from account.decorators import admin_role_required
# from notification.models import NotifyModel


class TalkAPI(APIView):
    """
    讨论区帖子api
    """
    @admin_role_required
    def post(self, request):
        title = request.data['title']
        desc = request.data['desc']
        talk = TalkModel()
        talk.user_id = request.user.id
        talk.title = title
        talk.desc = desc
        talk.save()
        return self.success(TalkSerializers(talk).data)

    @admin_role_required
    def get(self, request):
        talk_id = request.GET.get('id')
        if talk_id:
            try:
                talk = TalkModel.objects.get(id=talk_id)
            except TalkModel.DoesNotExist:
                return self.error("Talk does not exist")
            return self.success(TalkSerializers(talk).data)
        # 讨论帖子列表
        talk = TalkModel.objects.all().order_by('-create_time')
        return self.success(TalkSerializers(talk, many=True).data)

    @admin_role_required
    def delete(self, request):
        talk_id = request.GET.get('id')
        if talk_id:
            try:
                talk = TalkModel.objects.get(id=talk_id, user_id=request.user.id)
            except TalkModel.DoesNotExist:
                return self.error("no permission")
            comments = TalkCommentModel.objects.filter(talk=talk)
            if comments.exist():
                for comment in comments:
                    comment.delete()
            talk.delete()
            return self.success()
        return self.error("talk_id does not exist")


class TalkCommentAPI(APIView):
    """
    讨论区帖子评论
    """
    @admin_role_required
    def get(self, request):
        talk_id = request.GET.get('id')
        if talk_id:
            comments = TalkCommentModel.objects.filter(talk_id=talk_id).order_by("pub_time")
            if not comments.exists():
                return self.success([])
            return self.success(TalkCommentSerializers(comments, many=True).data)
        return self.error("talk_id does not exist")

    @admin_role_required
    def post(self, request):
        talk_id = request.data['talk_id']
        content = request.data['content']
        TalkCommentModel.objects.create(user_id=request.user.id, talk_id=talk_id, content=content)
        return self.success()

    @admin_role_required
    def delete(self, request):
        comment_id = request.GET.get('id')
        if comment_id:
            try:
                comment = TalkCommentModel.objects.get(id=comment_id, user_id=request.user.id)
            except TalkCommentModel.DoesNotExist:
                return self.error("Comment does not exist")
            comment.delete()
            return self.success()
        return self.error("comment_id does not exist")


class UserPubTalkAPI(APIView):
    @admin_role_required
    def get(self, request):
        return self.success(TalkSerializers(TalkModel.objects.filter(user_id=request.user.id).order_by('-create_time').data, many=True))
