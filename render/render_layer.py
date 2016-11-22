
from flask import Flask, render_template, redirect, url_for, request, flash
import werkzeug.exceptions


class RenderLayer(object):
    def __init__(self, html, json):
        self.html = html
        self.json = json

    def get_accept_type(self):
        best = request.accept_mimetypes.best_match(['text/html',
                                                    'application/json'])
        if (best == 'text/html' and request.accept_mimetypes[best] >=
                request.accept_mimetypes['application/json']):
            return 'html'
        elif (best == 'application/json' and request.accept_mimetypes[best] >=
                request.accept_mimetypes['text/html']):
            return 'json'
        else:
            raise werkzeug.exceptions.NotAcceptable()

    def render_index(self, data, accept=None):
        if not accept:
            accept = self.get_accept_type()

        if accept == 'html':
            return self.html.render_index(data)
        else:
            return self.json.render_index(data)

    def render_deadlines(self, data, accept=None):
        if not accept:
            accept = self.get_accept_type()

        if accept == 'html':
            return self.html.render_deadlines(data)
        else:
            return self.json.render_deadlines(data)

    def render_task(self, data, accept=None):
        if not accept:
            accept = self.get_accept_type()

        if accept == 'html':
            return self.html.render_task(data)
        else:
            return self.json.render_task(data)

    def render_list_users(self, users, accept=None):
        if not accept:
            accept = self.get_accept_type()

        if accept == 'html':
            return self.html.render_list_users(users)
        else:
            return self.json.render_list_users(users)

    def render_user(self, user, accept=None):
        if not accept:
            accept = self.get_accept_type()

        if accept == 'html':
            return self.html.render_user(user)
        else:
            return self.json.render_user(user)

    def render_options(self, data, accept=None):
        if not accept:
            accept = self.get_accept_type()

        if accept == 'html':
            return self.html.render_options(data)
        else:
            return self.json.render_options(data)

    def render_list_tags(self, data, accept=None):
        if not accept:
            accept = self.get_accept_type()

        if accept == 'html':
            return self.html.render_list_tags(data)
        else:
            return self.json.render_list_tags(data)

    def render_tag(self, data, accept=None):
        if not accept:
            accept = self.get_accept_type()

        if accept == 'html':
            return self.html.render_tag(data)
        else:
            return self.json.render_tag(data)
