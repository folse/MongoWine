# -*- coding:utf-8 -*-
import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask_security import Security, UserMixin, login_required
from mongoengine import *
from wine import db, login_manager

class User(db.Document):
    email = StringField(max_length=64)
    username = StringField(max_length=64)
    password = StringField(max_length=256)
    created_at = DateTimeField(default=datetime.utcnow)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # TypeError: ObjectId('552f41e56a85f00dd043406b') is not JSON serializable
    def get_id(self):
        return str(self.id)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        if self.username is not None:
            return u'{name}'.format(name=self.username)
        return u'{name}'.format(name=self.username)

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

class Wine(db.Document):
    name = StringField(max_length=256)
    sales_start = StringField(max_length=256)
    alcohol = StringField(max_length=64)
    color = StringField(max_length=256)
    fragrance = StringField(max_length=256)
    ingredient = StringField(max_length=256)
    sugar = StringField(max_length=256)
    producer = StringField(max_length=256)
    supplier = StringField(max_length=256)
    url = StringField(max_length=256)
    number = StringField(max_length=64)
    category = StringField(max_length=64)
    sys_wine_id = StringField(max_length=64)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

class Store(db.Document):
    name = StringField(max_length=256)
    city = StringField(max_length=256)
    sys_store_id = StringField(max_length=64)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


