#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self, subject="", content="", error=""):
        posts = db.GqlQuery("SELECT * FROM  Post "
                           "ORDER BY created DESC "
                           "LIMIT 5 ")

        self.render("home.html", subject=subject, content=content, error=error, posts=posts)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Post(subject = subject, content = content)
            p.put()

            self.redirect("/")
        else:
            error = "Subject and Blog cannot be blank"
            self.render_front(subject, content, error)

class BlogHome(Handler):
    def render_home(self, subject="", content="", error=""):
        posts = db.GqlQuery("SELECT * FROM  Post "
                           "ORDER BY created DESC "
                           "LIMIT 5 ")

        self.render("home.html", subject=subject, content=content, error=error, posts=posts)

    def get(self):
        self.render_home()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Post(subject = subject, content = content)
            p.put()

            self.redirect("/")
        else:
            error = "Subject and Blog cannot be blank"
            self.render_front(subject, content, error)

class Newpost(Handler):
    def render_blog(self, subject="", content="", error=""):
        self.render("newpost.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_blog()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Post(subject = subject, content = content)
            p.put()

            #self.redirect("/blog")
            key = db.Key.from_path('Post', p.key().id())
            post = db.get(key)
            self.render("linkpage.html", post = post)
        else:
            error = "Header and Blog cannot be blank"
            self.render_blog(subject, content, error)

class ViewPostHandler(Handler):
    def get(self, id):
        key = db.Key.from_path('Post', int(id))
        post = db.get(key)
        subject = self.request.get("subject")
        content = self.request.get("content")
        if not post:
            self.error(404)
            return
        else:
            self.render("linkpage.html", post = post)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogHome),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ('/blog/newpost', Newpost)


], debug=True)
