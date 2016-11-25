
from flask import json, url_for

class JsonApi(object):

    def __init__(self, jr, ll):
        self.jr = jr
        self.ll = ll

    def index(self):
        return {}, 200