from ..serializers import TalkSerializers, TalkCommentSerializers
from ..models import TalkModel, TalkCommentModel
from utils.api import APIView
from account.decorators import super_admin_required


class TalkAdminAPI(APIView):
    @super_admin_required
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

    @super_admin_required
    def delete(self, request):
        talk_id = request.GET.get('id')
        if talk_id:
            try:
                talk = TalkModel.objects.get(id=talk_id)
            except TalkModel.DoesNotExist:
                return self.error("Talk does not exist")
            comments = TalkCommentModel.objects.filter(talk=talk)
            if comments.exist():
                for comment in comments:
                    comment.delete()
            talk.delete()
            return self.success()
        return self.error("talk_id does not exist")


class TalkAdminCommentAPI(APIView):
    @super_admin_required
    def get(self, request):
        talk_id = request.GET.get('id')
        if talk_id:
            comments = TalkCommentModel.objects.filter(talk_id=talk_id).order_by("pub_time")
            if not comments.exists():
                return self.success([])
            return self.success(TalkCommentSerializers(comments, many=True).data)
        return self.error("talk_id does not exist")

    @super_admin_required
    def delete(self, request):
        comment_id = request.GET.get('id')
        if comment_id:
            try:
                comment = TalkCommentModel.objects.get(id=comment_id)
            except TalkCommentModel.DoesNotExist:
                return self.error("Comment does not exist")
            comment.delete()
            return self.success()
        return self.error("comment_id does not exist")
