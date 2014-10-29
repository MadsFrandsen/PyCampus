from werkzeug import cached_property
from itertools import groupby


class UserCVBuilder(object):

    def __init__(self, campus_net_client):
        self.campus_net_client = campus_net_client

    def build(self):
        return UserCV(
            self.user.first_name,
            self.user.last_name,
            self.grades
        )

    @cached_property
    def user(self):
        return self.campus_net_client.user()

    @property
    def grades(self):
        return self.campus_net_client.grades()


class UserCV(object):
    def __init__(self, first_name, last_name, exam_results):
        self.first_name = first_name
        self.last_name = last_name
        self._exam_results = exam_results

    @property
    def full_name(self):
        return " ".join([self.first_name, self.last_name])

    @cached_property
    def exam_results_grouped_by_programme(self):
        return ExamResultProgrammeGrouper.grouped_by_programme(
            map(UserCVExamResult, self._exam_results)
        )


class ExamResultProgrammeGrouper(object):
    @staticmethod
    def grouped_by_programme(exam_results):
        grouped_exam_results = groupby(
            exam_results,
            lambda x: x.programme
        )
        return [(programme, list(programme_exam_results))
                for programme, programme_exam_results
                in grouped_exam_results]


class UserCVExamResult(object):
    def __init__(self, exam_result):
        self.exam_result = exam_result

    @property
    def course_title(self):
        return self.exam_result.course.title

    @property
    def ects_points(self):
        return self.exam_result.ects_points

    @property
    def grade(self):
        return self.exam_result.grade

    @property
    def url(self):
        return "http://www.kurser.dtu.dk/%s.aspx" % self.course_number

    @property
    def course_number(self):
        return self.exam_result.course.course_number

    @property
    def programme(self):
        return self.exam_result.programme