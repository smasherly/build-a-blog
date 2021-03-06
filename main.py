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
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment (loader = jinja2.FileSystemLoader (template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str (self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render (self, template, **kw):
    self.write(self.render_str(template, **kw))

class Post(db.Model):  #creates an intity
  title = db.StringProperty(required = True) #constraint, won't let you not enter a title
  words = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True) #set created at current time when art is created
  #all this in google docs for datastore

class MainPage(Handler):
  def render_front(self, title="", words="", error=""):

    posts = db.GqlQuery("SELECT * FROM Post \
                        ORDER BY created DESC LIMIT 5")

    self.render("base.html", title=title, words=words, error=error, posts=posts)



  def get (self):
    self.render_front()

  # def post (self):
  #   title = self.request.get("title")
  #   words = self.request.get("words")
  #
  #   if title and words:
  #     a = Post(title = title, words = words) #creates new instence of art
  #     a.put() #stores new art object in database
  #
  #     self.redirect("/" )
  #   else:
  #     error = "we need both a title and some text"
  #     self.render_front(title, words, error)

class NewPost(Handler):

    def render_newpost (self, title="", words="", error=""):
        self.render("newpost.html", title=title, words=words, error=error)



    def get (self):
        self.render_newpost()

    def post (self):
        title = self.request.get("title")
        words = self.request.get("words")

        if title and words:
            a = Post(title = title, words = words) #creates new instence of art
            a.put() #stores new art object in database
            self.redirect("/blog/%s" % str(a.key().id()))
        else:
            error = "we need both a title and some text"
            self.render_newpost(title, words, error)

class ViewPost(Handler):
    # post_id = self.request.get("post")
    # post_link = Post.get_by_id( int(post_id) )
    #
    # def render_viewpost (self, title="", words="", error="", id):
    #     self.render("viewpost.html", title=title, words=words, error=error, id=post_link )

    def get(self, id):
        post = Post.get_by_id( int(id) )
        # self.response.write ("I have {0}".format(id))
        if post:
            self.render("viewpost.html", title = post.title, words = post.words)
        else:
            error= "Sorry! That blog post doe not exsist."
            self.render("viewpost.html", error = error)



app = webapp2.WSGIApplication([('/', MainPage),
                                ("/newpost/", NewPost),
                                webapp2.Route('/blog/<id:\d+>', ViewPost)], debug =True)
