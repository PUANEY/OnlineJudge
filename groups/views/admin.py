from groups.models import (HomeWork,
                           Groups)
from groups.serializers import (HomeWorkSerializer,
                                GroupsSerializer)
from account.decorators import admin_role_required
from utils.api import APIView
from datetime import datetime
from submission.models import Submission
from submission.serializers import SubmissionModelSerializer
from account.models import User
from account.serializers import UserSerializer
import dateutil.parser
from problem.models import Problem
from problem.serializers import ProblemSerializer
import jieba


class GroupAdminAPI(APIView):
    @admin_role_required
    def get(self, request):
        """
        管理员（老师）获取课程列表, 课程详情
        """
        group_id = request.GET.get('id')
        # 获取课程详情
        if group_id:
            try:
                group = Groups.objects.get(id=group_id, teacher=request.user)
            except Groups.DoesNotExist:
                return self.error("Group does not exist")
            return self.success(GroupsSerializer(group).data)

        # 获取课程列表
        groups = Groups.objects.filter(teacher=request.user).order_by('-create_time')
        data = []
        group_info = {}
        for group in groups:
            # group每一个课程
            ser = GroupsSerializer(group).data
            group_info['id'] = ser.get('id')
            group_info['group_name'] = ser.get('group_name')
            group_info['create_time'] = ser.get('create_time')
            group_info['total'] = ser.get('total')
            data.append(group_info)
            group_info = {}
        return self.success(data)

    @admin_role_required
    def post(self, request):
        """
        管理员（老师）创建课程
        """
        group_name = request.data['group_name']
        entry_code = request.data['entry_code']
        if Groups.objects.filter(entry_code=entry_code).exists():
            return self.error("This EntryCode is already existed")
        Groups.objects.create(teacher=request.user, group_name=group_name, entry_code=entry_code,
                              create_time=datetime.now())
        return self.success()

    @admin_role_required
    def put(self, request):
        """
        管理员（老师）修改课程信息
        """
        group_id = request.data['group_id']
        group_name = request.data['group_name']
        group = Groups.objects.get(id=group_id)
        group.group_name = group_name
        group.save()
        return self.success(GroupsSerializer(group).data)

    @admin_role_required
    def delete(self, request):
        """
        管理员（老师）删除课程
        """
        group_id = request.GET.get('id')
        try:
            group = Groups.objects.get(id=group_id)
        except Groups.DoesNotExist:
            return self.error("Group does not exist")
        # 这个课程布置的所有作业
        homework_list = HomeWork.objects.filter(group=group)
        for homework in homework_list:
            homework.delete()
        # 删除所有加入该课程学生 gourp_id_list中的此课程group_id
        student_str = group.student_id_list
        student_id_list = student_str.split(",")
        student_id_list.pop()
        # student_id_list所有加入该课程的学生id列表
        for student_id in student_id_list:
            user = User.objects.get(id=student_id)
            user_group_id_str = user.group_id_list
            user_group_id_list = user_group_id_str.split(",")
            user_group_id_list.pop()
            # user_group_id_list所有该学生加入课程的id
            for user_group_id in user_group_id_list:
                if user_group_id == group_id:
                    user_group_id_list.remove(user_group_id)
                    break
            user_group_id_str = ""
            for user_group_id in user_group_id_list:
                user_group_id_str += str(user_group_id) + ","
            user.group_id_list = user_group_id_str
            user.save()
        group.delete()
        return self.success()


class HomeWorkAdminAPI(APIView):
    """
    老师端作业列表和详情
    """

    @admin_role_required
    def post(self, request):
        title = request.data['title']
        end_time = dateutil.parser.parse(request.data["end_time"])
        group_id = request.data['group_id']
        homework = HomeWork.objects.create(title=title, end_time=end_time, begin_time=datetime.now(), group_id=group_id)
        return self.success(HomeWorkSerializer(homework).data)

    @admin_role_required
    def get(self, request):
        # 可查看作业信息
        group_id = request.GET.get('group_id')
        homework_id = request.GET.get('homework_id')
        # 获取作业详情，问题列表, 作业完成情况
        if homework_id:
            try:
                homework = HomeWork.objects.get(id=homework_id)
            except HomeWork.DoesNotExist:
                return self.error("HomeWork does not exist")
            # 获取哪些人完成了作业
            # 先获取参与课程的人数列表
            if group_id:
                al_achieve = []
                no_achieve = []
                problem_list = []
                data = []
                group = Groups.objects.get(id=group_id)
                student_str = group.student_id_list
                student_id_list = student_str.split(',')
                student_id_list.pop()
                problem_str = homework.problem_id_list
                problem_id_list = problem_str.split(',')
                problem_id_list.pop()
                if len(problem_id_list) == 0:
                    # 这个作业没有题目
                    data.append({"homework_detail": HomeWorkSerializer(homework).data})
                    data.append({"problem_list": problem_list})
                    data.append({"al_achieve": al_achieve})
                    data.append({"no_achieve": no_achieve})
                    return self.success(data)
                for problem_id in problem_id_list:
                    problem_list.append(ProblemSerializer(Problem.objects.get(_id=problem_id)).data)
                for student_id in student_id_list:
                    achieve_num = 0
                    for problem_id in problem_id_list:
                        submissions = Submission.objects.filter(problem=Problem.objects.get(_id=problem_id),
                                                                user_id=student_id).order_by("-create_time")
                        if not submissions.exists():
                            no_achieve.append(UserSerializer(User.objects.get(id=student_id)).data)
                            break
                        for submission in submissions:
                            # 判断提交记录是否在该次作业的开始日期和截止日期之间
                            if submission.result == 0 and homework.begin_time < submission.create_time < homework.end_time:
                                achieve_num += 1
                                break
                            if submission.result != 0:
                                no_achieve.append(UserSerializer(User.objects.get(id=student_id)).data)
                                break
                    if achieve_num == len(problem_id_list):
                        al_achieve.append(UserSerializer(User.objects.get(id=student_id)).data)
                data.append({"homework_detail": HomeWorkSerializer(homework).data})
                data.append({"problem_list": problem_list})
                data.append({"al_achieve": al_achieve})
                data.append({"no_achieve": no_achieve})
                return self.success(data)
        if group_id:
            # 获取作业列表
            group = Groups.objects.get(id=group_id, teacher=request.user)
            homework_list = HomeWork.objects.filter(group=group).order_by('begin_time')
            data = []
            for homework in homework_list:
                data.append(HomeWorkSerializer(homework).data)
            return self.success(data)

    @admin_role_required
    def put(self, request):
        homework_id = request.data['homework_id']
        title = request.data['title']
        end_time = dateutil.parser.parse(request.data["end_time"])
        homework = HomeWork.objects.get(id=homework_id)
        homework.title = title
        homework.end_time = end_time
        return self.success(HomeWorkSerializer(homework).data)

    @admin_role_required
    def delete(self, request):
        """
        管理员（老师）删除作业
        """
        homework_id = request.GET.get('id')
        if homework_id:
            HomeWork.objects.get(id=homework_id).delete()
            return self.success()
        return self.error("HomeWork does not exist")


class AddProblemToHWAPI(APIView):
    @admin_role_required
    def post(self, request):
        homework_id = request.data['homework_id']
        problem_id = request.data['problem_id']
        homework = HomeWork.objects.get(id=homework_id)
        homework.problem_id_list += str(problem_id) + ","
        homework.save()
        return self.success()


class RemoveProblemFromHWAPI(APIView):
    @admin_role_required
    def post(self, request):
        homework_id = request.data['homework_id']
        problem_id = request.data['problem_id']
        homework = HomeWork.objects.get(id=homework_id)
        problem_id_str = homework.problem_id_list
        problem_id_list = problem_id_str.split(",")
        problem_id_list.pop()
        for pid in problem_id_list:
            if pid == str(problem_id):
                problem_id_list.remove(pid)
                break
        pid_list = ""
        for pid in problem_id_list:
            pid_list += str(pid) + ','
        homework.problem_id_list = pid_list
        homework.save()
        return self.success()


class StudentListByPassingProblemID(APIView):
    """
    :arg
    1. homework_id： 作业id->获取此次作业的开始日期和截止日期
    2. problem_id： 问题display_id
    3. group_id:   课程id->获取加入该课程的学生列表
    """

    def post(self, request):
        group_id = request.data['group_id']
        homework_id = request.data['homework_id']
        problem_id = request.data['problem_id']

        group = Groups.objects.get(id=group_id)
        homework = HomeWork.objects.get(id=homework_id)
        problem = Problem.objects.get(_id=problem_id)
        # 根据group获取加入该课程的学生student_id_list
        student_str = group.student_id_list
        student_id_list = student_str.split(',')
        student_id_list.pop()

        al_achieve_students = []
        for student_id in student_id_list:
            submissions = Submission.objects.filter(problem=problem,
                                                    user_id=student_id).order_by("-create_time")
            if not submissions.exists():
                break
            for submission in submissions:
                # 判断提交记录是否在该次作业的开始日期和截止日期之间
                if submission.result == 0 and homework.begin_time < submission.create_time < homework.end_time:
                    al_achieve_students.append(UserSerializer(User.objects.get(id=student_id)).data)
                    break
                if submission.result != 0:
                    continue
        return self.success(al_achieve_students)


class CodeDuplicationCheck(APIView):
    def codeCheck(self, check_student_submission, other_student_submission, rate):
        """
        :return
        data = {"雷同率": "", "被检查学生的username": "被检查学生的提交文本", "相比较的学生的username": "相比较的学生的提交文本", "疑似抄袭":""}
        data = {"SimilarityRate": "", "CheckStudent": "CheckStudentSubmission", "CheckStudentSubTime": "","CompareStudent": "CompareStudentSubmission", "CompareStudentSubTime": "", "isCopy": ""}
        :arg
        submission.code: 代码
        submission.username: 提交用户的用户名
        """
        c1 = check_student_submission.code
        c2 = other_student_submission.code
        code1 = jieba.lcut(c1)
        code2 = jieba.lcut(c2)
        time1 = SubmissionModelSerializer(check_student_submission).data.get('create_time')
        time2 = SubmissionModelSerializer(other_student_submission).data.get('create_time')
        for code in code1:
            if code == "\n" or code == " ":
                code1.remove(code)

        for code in code2:
            if code == "\n" or code == " ":
                code2.remove(code)

        count = 0
        length = len(code1) if len(code1) < len(code2) else len(code2)
        for i in range(length):
            if code1[i] == code2[i]:
                count += 1
        num = (count / length) * 100
        percent = str(round(num)) + "%"
        isCopy = False
        if num >= rate:
            isCopy = True
        return {"SimilarityRate": percent,
                "CheckStudent": check_student_submission.username,
                "CheckStudentSubmission": c1,
                "CheckStudentSubTime": time1,
                "CompareStudent": other_student_submission.username,
                "CompareStudentSubmission": c2,
                "CompareStudentSubTime": time2,
                "isCopy": isCopy}

    def post(self, request):
        """
        :arg
        1. al_achieve_students: 已完成该问题的学生列表
        2. problem_id: 该问题的_id
        3. check_student_id: 要对某位学生查重的学生id
        4. homework_id: 课程id
        """
        al_achieve_students = request.data['al_achieve_students']
        if len(al_achieve_students) == 1:
            return self.error("当前只有一个学生完成该题目")
        problem_id = request.data['problem_id']
        problem = Problem.objects.get(_id=problem_id)
        check_student_id = request.data['check_student_id']
        homework_id = request.data['homework_id']
        rate = request.data['codecheckrate']
        homework = HomeWork.objects.get(id=homework_id)
        check_student_submissions = Submission.objects.filter(problem=problem, user_id=check_student_id).order_by(
            '-create_time')
        data = []
        for submission in check_student_submissions:
            # 只取在作业时间内完成的最后一次做比较
            if homework.begin_time < submission.create_time < homework.end_time:
                check_student_submission = submission
                break
            else:
                continue
        for student in al_achieve_students:
            if student['id'] == check_student_id:
                continue
            submissions = Submission.objects.filter(problem=problem, user_id=student['id']).order_by('-create_time')
            # 其他学生也只取在作业时间内完成的最后一次做比较
            for submission in submissions:
                if homework.begin_time < submission.create_time < homework.end_time:
                    info = self.codeCheck(check_student_submission, submission, rate)
                    if info["isCopy"]:
                        data.append(info)
                    break
                else:
                    continue
        return self.success(data)
