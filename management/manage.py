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
def create_admin(username, password):
    admin = User(email='asd', username=username, password=generate_password_hash(password), is_active=True)
    admin.save()

if __name__ == '__main__':
	from werkzeug.contrib.fixers import ProxyFix
	app.wsgi_app = ProxyFix(app.wsgi_app)
	manager.run()
