
import itertools

from flask import Flask, render_template, redirect, url_for, request, flash
from flask import make_response, Markup, jsonify, json
from flask.ext.login import logout_user, current_user


class HtmlRenderer(object):
    def render_index(self, data):
        resp = make_response(
            render_template('index.t.html',
                            show_deleted=data['show_deleted'],
                            show_done=data['show_done'],
                            show_hierarchy=data['show_hierarchy'],
                            cycle=itertools.cycle,
                            user=current_user,
                            tasks_h=data['tasks_h'],
                            tags=data['all_tags']))
        return resp

    def render_deadlines(self, data):
        return make_response(
            render_template(
                'deadlines.t.html',
                cycle=itertools.cycle,
                deadline_tasks=data['deadline_tasks']))

    def render_task(self, data):
        return render_template('task.t.html', task=data['task'],
                               descendants=data['descendants'],
                               cycle=itertools.cycle,
                               show_deleted=data['show_deleted'],
                               show_done=data['show_done'],
                               show_hierarchy=data['show_hierarchy'])

    def render_list_users(self, users):
        return render_template('list_users.t.html', users=users,
                               cycle=itertools.cycle)

    def render_user(self, user):
        return render_template('view_user.t.html', user=user)

    def render_options(self, data):
        return render_template('options.t.html', options=data)

    def render_list_tags(self, tags):
        return render_template('list_tags.t.html', tags=tags,
                               cycle=itertools.cycle)

    def render_tag(self, data):
        return render_template('tag.t.html', tag=data['tag'],
                               tasks=data['tasks'], cycle=itertools.cycle)
