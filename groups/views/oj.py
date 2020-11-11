from groups.models import (HomeWork,
                           Groups)
from groups.serializers import (HomeWorkSerializer,
                                GroupsSerializer)
from account.decorators import login_required
from account.models import User
from utils.api import APIView
from problem.models import Problem
from problem.serializers import ProblemSerializer
from submission.models import Submission


class SearchGroupByKeyWordAPI(APIView):
    """
    根据keyword搜索课程
    """
    @login_required
    def get(self, request):
        keyword = request.GET.get("keyword")
        if keyword:
            try:
                groups = Groups.objects.filter(group_name__icontains=keyword).order_by("-create_time")
            except Groups.DoesNotExist:
                return self.error("Groups does not exist")
            group_str = request.user.group_id_list
            if group_str is None:
                return self.success(GroupsSerializer(groups, many=True).data)
            group_id_list = group_str.split(',')
            group_id_list.pop()
            for group_id in group_id_list:
                for group in groups:
                    if group_id == str(group.id):
                        groups = groups.exclude(id__exact=group_id)
            return self.success(GroupsSerializer(groups, many=True).data)


class JoinGroupBySearchAPI(APIView):
    """
    根据上一步搜索结果确定加入课程
    """
    @login_required
    def post(self, request):
        group_id = request.data['group_id']
        entry_code = request.data['entry_code']
        try:
            group = Groups.objects.get(id=group_id, entry_code=entry_code)
        except Groups.DoesNotExist:
            return self.error("EntryCode Error")
        if request.user.admin_type == "Super Admin":
            return self.error("You are teacher, Only Create the Course")
        group.student_id_list += str(request.user.id) + ","
        group.total += 1
        group.save()
        user = User.objects.get(id=request.user.id)
        if user.group_id_list is None:
            user.group_id_list = ""
        user.group_id_list += str(group_id) + ","
        user.save()
        return self.success(GroupsSerializer(group).data)


class GroupListAndDetailAPI(APIView):
    """
    课程列表和详情页面
    """
    @login_required
    def get(self, request):
        group_id = request.GET.get('id')
        # 获取课程详情
        if group_id:
            try:
                group = Groups.objects.get(id=group_id)
            except Groups.DoesNotExist:
                return self.error("Group does not exist")
            return self.success(GroupsSerializer(group).data)
        user_id = request.user.id
        # 根据用户id获取对应课程id列表
        user = User.objects.get(id=user_id)
        group_str = user.group_id_list
        if group_str is None:
            return self.success([])
        group_id_list = group_str.split(",")
        group_id_list.pop()
        group_list = []
        for group_id in group_id_list:
            group_list.append(GroupsSerializer(Groups.objects.get(id=group_id)).data)
        return self.success(group_list)


class HomeWorkListAndDetailAPI(APIView):
    """
    学生端作业列表和详情(只能看到自己是否完成这次作业）
    """
    @login_required
    def get(self, request):
        group_id = request.GET.get('group_id')
        homework_id = request.GET.get('homework_id')
        if homework_id:
            # 获取作业详情
            try:
                homework = HomeWork.objects.get(id=homework_id)
            except HomeWork.DoesNotExist:
                return self.error("HomeWork does not exist")
            # 获取问题id
            problem_str = homework.problem_id_list
            # 分解id
            problem_id_list = problem_str.split(',')
            problem_id_list.pop()
            problem_list = []
            # 记录已完成的题目数目
            achieve_num = 0
            is_achieve = False
            for problem_id in problem_id_list:
                problem_list.append(ProblemSerializer(Problem.objects.get(_id=problem_id)).data)
            for problem_id in problem_id_list:
                # 判断该题目当前用户是否完成
                submissions = Submission.objects.filter(problem=Problem.objects.get(_id=problem_id), user_id=request.user.id).order_by("-create_time")
                if not submissions.exists():
                    break
                for submission in submissions:
                    if submission.result == 0 and homework.begin_time < submission.create_time < homework.end_time:
                        achieve_num += 1
                        break
            if achieve_num == len(problem_id_list):
                is_achieve = True
            data = []
            homework_detail = HomeWorkSerializer(homework).data
            data.append({"homework_detail": homework_detail})
            data.append({"problem_list": problem_list})
            data.append({"is_achieve": is_achieve})
            return self.success(data)
        if group_id:
            # 获取作业列表
            try:
                group = Groups.objects.get(id=group_id)
            except Groups.DoesNotExist:
                return self.error('Group does not exist')
            homework = HomeWork.objects.filter(group=group).order_by('begin_time')
            data = []
            for hw in homework:
                data.append(HomeWorkSerializer(hw).data)
            return self.success(data)
