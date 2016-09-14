#!/usr/bin/env python
import os
from wine import app
from wine.models import User
from flask_script import Manager, Server, Shell
from werkzeug.security import generate_password_hash

manager = Manager(app)
manager.add_command("run", Server(host="0.0.0.0", port=80, use_debugger=True))

@manager.option('-u', '--name', dest='username', default='admin')
@manager.option('-p', '--password', dest='password', default='123456')
@manager.option('-e', '--email', dest='email', default='default@abc.com')
def create_admin(username, password, email):
    admin = User(username=username, password=generate_password_hash(password), email=email)
    admin.save()

if __name__ == '__main__':
	from werkzeug.contrib.fixers import ProxyFix
	app.wsgi_app = ProxyFix(app.wsgi_app)
	manager.run()
