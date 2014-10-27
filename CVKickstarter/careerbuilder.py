__author__ = 'Mads'

import requests
from bs4 import BeautifulSoup as soup

class CareerBuilder:
    BASE_URL = 'http://api.careerbuilder.com/v2/jobsearch'
    PARAM_DEV_KEY = 'DeveloperKey'
    PARAM_KEYWORDS = 'keywords'
    PARAM_PER_PAGE = "perpage"

    def __init__(self, developer_key):
        self.developer_key = developer_key

    def find_results_amount(self, keyword=''):
        request_url = self.BASE_URL + \
                      '?' + self.PARAM_DEV_KEY + \
                      '=' + self.developer_key + \
                      '&' + self.PARAM_KEYWORDS + \
                      '=' + keyword

        response = requests.request('GET', request_url)
        data = soup(response.text, features='xml')
        return int(data.ResponseJobSearch.TotalCount.contents[0])

    def find_results(self, keywords=None, amount=25):
        keywordString = ','.join(keywords)

        request_url = self.BASE_URL + \
                      '?' + self.PARAM_DEV_KEY + \
                      '=' + self.developer_key + \
                      '&' + self.PARAM_PER_PAGE + \
                      '=' + str(amount) + \
                      '&' + self.PARAM_KEYWORDS + \
                      '=' + keywordString

        response = requests.request('GET', request_url)
        data = soup(response.text, features='xml')
        return data.ResponseJobSearch
