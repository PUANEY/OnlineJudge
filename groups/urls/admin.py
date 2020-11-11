from django.conf.urls import url

from ..views.admin import (GroupAdminAPI,
                           HomeWorkAdminAPI,
                           AddProblemToHWAPI,
                           RemoveProblemFromHWAPI,
                           StudentListByPassingProblemID,
                           CodeDuplicationCheck)

urlpatterns = [
    url(r"^groups/?$", GroupAdminAPI.as_view(), name="group_admin_api"),
    url(r"^homework/?$", HomeWorkAdminAPI.as_view(), name="homework_admin_api"),
    url(r"^add_problem_hw/?$", AddProblemToHWAPI.as_view(), name="add_problem_to_hw_api"),
    url(r"^remove_problem_hw/?$", RemoveProblemFromHWAPI.as_view(), name="remove_problem_from_hw_api"),
    url(r"^pass_student_list/?$", StudentListByPassingProblemID.as_view(), name="pass_student_list_api"),
    url(r"^code_check/?$", CodeDuplicationCheck.as_view(), name="code_duplication_check_api"),
]