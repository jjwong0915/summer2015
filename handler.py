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

from fbuser import *


template_dir = os.path.join(os.path.dirname(__file__), 'Summer/template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

FACEBOOK_APP_ID = "1101523553197452"
FACEBOOK_APP_SECRET = "46f35b95eb1710680d16d39d78a86b05"

# FACEBOOK_APP_ID = "1101405939875880"
# FACEBOOK_APP_SECRET = "c0aba9ad62a0148f8bb1ae119a9eb3a7"

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    @property
    def fb_user(self):
        """Returns the logged in Facebook user, or None if unconnected."""
        if not hasattr(self, "_fb_user"):
            self._fb_user = None
            user_id = parse_cookie(self.request.cookies.get("fb_user"))
            if user_id:
                self._fb_user = FBUser.get_by_key_name(user_id)
        return self._fb_user

def escape_input_show(text):  
    text = text.replace('<br>','\n')
    text = text.replace('&quot;','"')
    text = text.replace('&gt;', '>')
    text = text.replace('&lt;', '<')
    text = text.replace('&amp;', '&')
    return text

def escape_show(text):
    # text = text.replace('&quot;','"')
    # text = text.replace('&gt;', '>')
    # text = text.replace('&lt;', '<')
    # text = text.replace('&amp;', '&')
    return text

def escape_input_save(text):
    text = text.replace('&', '&amp;')
    text = text.replace('"','&quot;')
    text = text.replace('>', '&gt;')
    text = text.replace('<', '&lt;')
    text = text.replace('\n','<br>')
    return text

#FB Cookie
def set_cookie(response, fbname, value, domain=None, path="/", expires=None):
    """Generates and signs a cookie for the give name/value"""
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(value, timestamp)
    cookie = Cookie.BaseCookie()
    cookie[fbname] = "|".join([value, timestamp, signature])
    cookie[fbname]["path"] = path
    if domain:
        cookie[fbname]["domain"] = domain
    if expires:
        cookie[fbname]["expires"] = email.utils.formatdate(
            expires, localtime=False, usegmt=True)
    response.headers.add("Set-Cookie", cookie.output()[12:])

def parse_cookie(value):
    """Parses and verifies a cookie value from set_cookie"""
    if not value:
        return None
    parts = value.split("|")
    if len(parts) != 3:
        return None
    if cookie_signature(parts[0], parts[1]) != parts[2]:
        logging.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 30 * 86400:
        logging.warning("Expired cookie %r", value)
        return None
    try:
        return base64.b64decode(parts[0]).strip()
    except:
        return None


def cookie_signature(*parts):
    """Generates a cookie signature.

    We use the Facebook app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(FACEBOOK_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts:
        hash.update(part)
    return hash.hexdigest()

# NAME_RE  = re.compile(r'^[/u4e00-/u9fa5]{1,3}$')
def valid_name(name):
    if name:
        return True
#     return not name or NAME_RE.match(name)

def valid_gender(gender):
    if(gender==u'男' or gender==u'女'):
        return True

def valid_birthdate(birthdate):
    return not birthdate

IDENTIFICATION_RE  = re.compile(r'^[A-Z]{1}[0-9]{10}$')
def valid_identification(identification):
    return not identification or IDENTIFICATION_RE.match(identification)

# SCHOOL_RE = re.compile(r'^[/u4e00-/u9fa5]{1,10}$')
def valid_school(school):
    if school:
        return True
    # return not school or SCHOOL_RE.match(school)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

PHONE_RE  = re.compile(r'^09\d{8}$')
def valid_phone(phone):
    return not phone or PHONE_RE.match(phone)

def valid_address(address):
    if address:
        return True

# def valid_meal(meal):
#     if(meal==u'葷'or meal==u'素'):
#         return True

def valid_tshirt(tshirt):
    if(tshirt==u'大'or tshirt==u'中' or tshirt==u'小'):
        return True

def valid_emergency_contact(emergency_contact):
    if emergency_contact:
        return True

def valid_emergency_contact_phone(emergency_contact_phone):
    if emergency_contact_phone:
        return True