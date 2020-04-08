from django.contrib import admin

# Register your models here.
from django.contrib import admin

from vote.forms import UserForm
from vote.models import Subject, Teacher, User


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'creat_date', 'is_hot')
    ordering = ('no',)


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'good_count', 'bad_count', 'subject', 'detail')
    ordering = ('subject', 'no')


class UserAdmin(admin.ModelAdmin):
    list_display = ('no', 'username', 'password')
    ordering = ('no', )
    form = UserForm
    list_per_page = 10


admin.site.register(User, UserAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Teacher, TeacherAdmin)
