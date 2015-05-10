# -*- coding: utf-8 -*-
import os
import re
import random
import hashlib
import hmac
from string import letters
from time import strftime
import codecs 
from google.appengine.ext import db
from datetime import datetime, timedelta

import webapp2
import jinja2


from handler import *
from fbuser import *

#participant
def participants_key(group = 'default'):
    return db.Key.from_path('participants', group)

class Participant(db.Model):
    name = db.StringProperty(required = True)
    gender = db.StringProperty(required = True)
    birthdate = db.StringProperty(required = True)
    identification = db.StringProperty(required = True)
    school = db.StringProperty(required = True)
    tshirt = db.StringProperty(required = True)
    phone = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    emergency_contact = db.StringProperty(required = True)
    emergency_contact_phone = db.StringProperty(required = True)
    meal = db.StringProperty(required = True)
    disease = db.StringProperty(required = True)
    prefix = db.StringProperty(required = True)
    fb_name = db.StringProperty(required = True)
    fb_url = db.StringProperty(required = True)
    show = db.BooleanProperty(required=True)
    post_created = db.DateTimeProperty(required=True , auto_now_add = True)

    def render(self):
        return render_str("console_participant_post.html", participant = self)

    def per_render(self):
        self.prefix  = escape_show(self.prefix)
        return render_str("console_participant_per_post.html", participant = self)

    @classmethod
    def add_participant(cls, name, gender, birthdate, identification, school, tshirt, phone, email,
        emergency_contact, emergency_contact_phone, meal, disease, prefix, fb_name, fb_url, show):
        return Participant(parent = participants_key(),
                    name = name,
                    gender = gender,
                    birthdate = birthdate,
                    identification = identification,
                    school = school,
                    tshirt = tshirt,
                    phone = phone,
                    email = email,
                    emergency_contact = emergency_contact,
                    emergency_contact_phone = emergency_contact_phone,
                    meal = meal,
                    disease = disease,
                    prefix = prefix,
                    fb_name = fb_name,
                    fb_url = fb_url,
                    show = show)

    