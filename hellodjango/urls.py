"""hellodjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from vote import views

# 响应请求时，从以下找出匹配项，调用对应的函数（或者引用其他url），同时传入 HttpRequest对象作为第一个参数。
urlpatterns = [
    path('admin/', admin.site.urls),  # admin.site.urls 是默认（自带）的后台管理view 函数
    path('', views.show_subjects),
    path('teachers/', views.show_teachers, name='teachers'),
    path('praise/', views.prise_or_criticize, name='praise'),
    path('criticize/', views.prise_or_criticize, name='criticize'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('captcha/', views.get_captcha, name='get_captcha'),
    path('logout/', views.logout, name='logout'),
    path('excel/', views.export_teachers_excel, name='excel'),

]

if settings.DEBUG:

    import debug_toolbar

    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))