from django.contrib import admin
from .models import users,organizations,approval

admin.site.register(users)
admin.site.register(organizations)
admin.site.register(approval)