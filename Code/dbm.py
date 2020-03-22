from pymongo import MongoClient


class DBM(object):

    def __init__(self):
        self.DB_NAME = 'stackexchange_demo'

        self.db = MongoClient()[self.DB_NAME]

    def add_user(self, user):
        self.db.users.insert_one(user)

    def get_user(self, flt={}):
        return self.db.users.find(flt)

    def update_user(self, flt={}, update={}):
        self.db.users.update_one(flt, update)


    def add_post(self, post):
        self.db.posts.insert_one(post)

    def get_post(self, flt={}):
        return self.db.posts.find(flt)

    def update_post(self, flt={}, update={}):
        self.db.posts.update_one(flt, update)


    def add_comment(self, comment):
        self.db.comment.insert_one(comment)

    def get_comment(self, flt={}):
        return self.db.comment.find(flt)

    def update_comment(self, flt={}, update={}):
        self.db.comment.update_one(flt, update)

