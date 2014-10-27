from werkzeug import cached_property


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
    def __init__(self, first_name, last_name, grades):
        self.first_name = first_name
        self.last_name = last_name
        self.grades = grades

    @property
    def full_name(self):
        return " ".join([self.first_name, self.last_name])
