"""Builds a User CV to display on the frontend."""
from werkzeug import cached_property
import re
from cv_kickstarter.models.user_cv import UserCV
from cv_kickstarter.course_repository import CourseRepository
from cv_kickstarter.dtu_skill_set import DtuSkillSet
from cv_kickstarter.models.exam_result_programme import ExamResultProgramme


class UserCVBuilder(object):

    """Builds a User CV to display on the frontend."""

    def __init__(self, campus_net_client, mongo_store):
        """Initialize with campus_net_client and mongo_store.

        The campus_net_client client need to be authenticated. It works out of
        the box with the cnapi library.

        The mongo_store is for storing the courses.
        """
        self.campus_net_client = campus_net_client
        self.mongo_store = mongo_store

    def build(self):
        """Return a UserCV."""
        return UserCV(
            self.user.first_name,
            self.user.last_name,
            self.grades,
            self._keywords
        )

    @cached_property
    def user(self):
        """Return a user with information from the campus_net_client."""
        return self.campus_net_client.user()

    @cached_property
    def grades(self):
        """Return grades from campus_net_client."""
        exam_result_programmes = map(
            self._map_exam_result_programme,
            self.campus_net_client.grades()
        )
        return [programme for programme
                in exam_result_programmes if programme is not None]

    @property
    def _keywords(self):
        return DtuSkillSet(
            self.grades,
            self._course_base_repo()
        ).skill_set()

    def _course_base_repo(self):
        return CourseRepository(self.mongo_store)

    def _map_exam_result_programme(self, exam_result):
        return CampusNetExamResultMapper(
            exam_result
        ).mapped_exam_result()


class CampusNetExamResultMapper(object):

    """Maps an exam result programme to an object ready for frontend."""

    def __init__(self, cn_exam_result_programme):
        """Initialize with cn_exam_result_programme."""
        self.cn_exam_result_programme = cn_exam_result_programme

    def mapped_exam_result(self):
        """Return mapped exam result."""
        if self._is_without_education_programme():
            return None
        return ExamResultProgramme(
            self.cn_exam_result_programme.name,
            self.cn_exam_result_programme.passed_ects_points,
            self._total_programme_ects(),
            self.cn_exam_result_programme.exam_results
        )

    def _total_programme_ects(self):
        if re.search(r"Bachelor", self.cn_exam_result_programme.name):
            return 180.0
        elif re.search(r"Master|Kandidat", self.cn_exam_result_programme.name):
            return 120.0

    def _is_without_education_programme(self):
        return self.cn_exam_result_programme.name == "Uden uddannelse"
