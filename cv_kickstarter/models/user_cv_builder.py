from werkzeug import cached_property
from user_cv import UserCV
from campus_net_exam_result_mapper import CampusNetExamResultMapper
from xml_course_base_repo_builder import XmlCourseBaseRepoBuilder
from dtu_skill_set import DtuSkillSet


class UserCVBuilder(object):

    def __init__(self, campus_net_client):
        self.campus_net_client = campus_net_client

    def build(self):
        return UserCV(
            self.user.first_name,
            self.user.last_name,
            self.grades,
            self._keywords
        )

    @cached_property
    def user(self):
        return self.campus_net_client.user()

    @cached_property
    def grades(self):
        return list(map(
            self._map_exam_result_programme,
            self.campus_net_client.grades()
        ))

    @property
    def _keywords(self):
        return DtuSkillSet(
            self.grades,
            self._course_base_repo()
        ).skill_set()

    def _course_base_repo(self):
        return XmlCourseBaseRepoBuilder('courses.xml').course_base_repo()

    def _map_exam_result_programme(self, exam_result):
        return CampusNetExamResultMapper(
            exam_result
        ).mapped_exam_result()
