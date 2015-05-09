# -*- coding: utf-8 -*-
import os
import re
import random
import hashlib
import hmac
from string import letters
from time import strftime
import codecs 
from datetime import datetime, timedelta

import webapp2
import jinja2   

import base64
import cgi
import Cookie
import email.utils
import logging
import os.path
import time
import urllib
import wsgiref.handlers

import json
#from django.utils import simplejson as json
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from handler import *
from fbuser import *

class MainPage(Handler):
    def get(self):
        self.redirect('/index')

class Index(Handler):
    def get(self):
      self.render('home.html')

class FBLogin(Handler):
    def get(self):
        verification_code = self.request.get("code")
        args = dict(client_id=FACEBOOK_APP_ID,
                    redirect_uri=self.request.path_url)
        if verification_code:
            args["client_secret"] = FACEBOOK_APP_SECRET
            args["code"] = verification_code
            response = cgi.parse_qs(urllib.urlopen(
                "https://graph.facebook.com/oauth/access_token?" +
                urllib.urlencode(args)).read())
            access_token = response["access_token"][-1]

            # Download the user profile and cache a local instance of the
            # basic profile info
            profile = json.load(urllib.urlopen(
                "https://graph.facebook.com/me?" +
                urllib.urlencode(dict(access_token=access_token))))
            user_find = db.GqlQuery("SELECT * FROM FBUser WHERE id = :id " ,id = str(profile["id"]) ).fetch(None,0)
            if user_find:
                user = FBUser(key_name=str(profile["id"]), id=str(profile["id"]),
                            fbname=profile["name"], access_token=access_token,
                            profile_url=profile["link"],stop=user_find[0].stop,admin=user_find[0].admin)
            else:
                user = FBUser(key_name=str(profile["id"]), id=str(profile["id"]),
                            fbname=profile["name"], access_token=access_token,
                            profile_url=profile["link"],stop=False,admin=False)
            user.put()
            set_cookie(self.response, "fb_user", str(profile["id"]),
                       expires=time.time() + 30 * 86400)
            self.redirect("/")
        else:
            self.redirect(
                "https://graph.facebook.com/oauth/authorize?" +
                urllib.urlencode(args))


class FBLogout(Handler):
    def get(self):
        set_cookie(self.response, "fb_user", "", expires=time.time() - 86400)
        self.redirect("/")

class NoLogin(Handler):
    def get(self):
        self.render('nologin.html')

class NoPermission(Handler):
    def get(self):
        if not self.user and not self.fb_user:
            self.render('nopermission.html')
        elif self.fb_user:
            fb_user = dict(fb_user=self.fb_user)
            self.render('nopermission.html',**fb_user)
        elif self.user:
            user = dict(user = self.user)
            self.render('nopermission.html', **user)

class Stop(Handler):
    def get(self):
        self.error(500)
        return

class Content(Handler):
    def get(self):
        self.render('content.html')

class Signup(Handler):
    def get(self):
        if not self.fb_user:
            self.redirect('/fblogin')
        else:
            if self.fb_user.stop:
                self.redirect('/stop')
            else:
                fbname = self.fb_user.fbname
                self.render('signup.html',fbname=fbname)

    def post(self):
        if not self.fb_user:
            self.redirect('/fblogin')
        else:
            if self.fb_user.stop:
                self.redirect('/stop')
            else:
                name = self.request.get('name')
                gender = self.request.get('gender')
                birthdate = self.request.get('birthdate')
                identification = self.request.get('identification')
                school = self.request.get('school')
                tshirt = self.request.get('tshirt')
                phone = self.request.get('phone')
                email = self.request.get('email')
                emergency_contact = self.request.get('emergency_contact')
                emergency_contact_phone = self.request.get('emergency_contact_phone')
                meal = self.request.get('meal')
                disease = self.request.get('disease')
                prefix = self.request.get('prefix')
                fb_name = self.fb_user.fbname
                fb_url = 'https://www.facebook.com/'+ self.fb_user.id


class Contact(Handler):
    def get(self):
        self.render('contact.html')
        
class Picture(Handler):
    def get(self):
        self.render('picture.html')
        
app = webapp2.WSGIApplication([('/', MainPage),
                                ('/index' , Index),
                                ('/fblogin',FBLogin),
                                ('/fblogout',FBLogout),                                
                                ('/nologin' , NoLogin),
                                ('/nopermission' , NoPermission),
                                ('/stop' , Stop),
                                ('/content',Content),
                                ('/signup',Signup),
                                ('/contact',Contact), 
                                ('/picture', Picture)
                                ],
                                debug=True)