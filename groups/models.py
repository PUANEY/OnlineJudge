from django.db import models
from account.models import User


class Groups(models.Model):
    """
    课程
    """
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher")
    group_name = models.TextField()
    create_time = models.DateTimeField(auto_created=True)
    entry_code = models.CharField(max_length=8, verbose_name="令牌", unique=True)
    student_id_list = models.TextField()
    total = models.PositiveIntegerField(default=0, verbose_name="班级人数")


class HomeWork(models.Model):
    """
    作业
    """
    title = models.TextField()
    begin_time = models.DateTimeField(auto_created=True)
    end_time = models.DateTimeField(null=True)
    problem_id_list = models.TextField()
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name="groups_by")
