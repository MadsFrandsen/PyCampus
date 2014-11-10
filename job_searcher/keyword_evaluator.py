from __future__ import division
from careerbuilder import CareerBuilder
from go_jobs import GoJobs

__author__ = 'Mads'

class KeywordEvaluator:
    """ This class is used to evaluate keywords with a given job searcher """

    def __init__(self, job_searcher):
        self.job_searcher = job_searcher

    def evaluate_keyword(self, keyword):
        """ Evaluates a keyword for the given job searcher
        :param keyword: The keyword to evaluate
        :return: The percentage of jobs, that contain the given keyword
        """
        totalJobs = self.job_searcher.find_results_amount()
        keywordJobs = self.job_searcher.find_results_amount(keyword)
        return keywordJobs / totalJobs * 100