from . import admin
from flask import redirect
from flask_login import login_required, current_user
from flask_admin.contrib.mongoengine import ModelView
from .models import *

class ModelView(ModelView):

    column_display_pk = True

    def is_accessible(self):

        if current_user.is_anonymous == True:
            return False
        else:
            return True

    def inaccessible_callback(self, name):
        return redirect('/auth/login')

class UserAdmin(ModelView):
    can_delete = False
    column_searchable_list = ['username', 'email']
    column_exclude_list = ['password']

class StoreAdmin(ModelView):
    can_create = False
    can_delete = False
    can_edit = False
    column_searchable_list = ['name', 'city', 'sys_store_id']
    column_exclude_list = ['created_at', 'updated_at']

admin.add_view(UserAdmin(User))
admin.add_view(StoreAdmin(Store))
