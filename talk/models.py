from django.db import models
from account.models import User


class TalkModel(models.Model):
    """
    讨论帖子
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_pub')
    title = models.TextField()
    desc = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'talk'


class TalkCommentModel(models.Model):
    """
    讨论区评论
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment")
    talk = models.ForeignKey(TalkModel, on_delete=models.CASCADE, related_name='talk_comment')
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'talk_comment'
