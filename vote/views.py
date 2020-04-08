# Create your views here.
"""
往往是创建 app 后第一个要写的视图。
存放着要显示在页面（模板）上的数据的交互逻辑
会接受 HttpRequest 以接收页面要求
"""
import random
from io import BytesIO
from urllib.parse import quote

import xlwt as xlwt
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from vote.forms import RegisterForm, LoginForm
from vote.models import Subject, Teacher, User
from django.http import JsonResponse, HttpResponse

from vote.captcha import Captcha


@cache_page(60 * 15, cache="page")
@vary_on_cookie
def show_subjects(request):
    subjects = Subject.objects.all()
    return render(request, 'subject.html', {'subjects': subjects})
    # render 函数作用：载入模板，填充上下文，再返回由它生成的 HttpResponse 对象


@cache_page(60 * 15, cache="page")
@vary_on_cookie
def show_teachers(request):
    try:
        sno = int(request.GET['sno'])
        subject = Subject.objects.get(no=sno)
        teacher = subject.teacher_set.all()
        return render(request, 'teacher.html', {'subject': subject, 'teachers': teacher})
    except (KeyError, ValueError, Subject.DoesNotExist):
        return redirect('/')


def prise_or_criticize(request):
    code, hint = 10002, '无效的老师编号'
    try:
        tno = int(request.GET['tno'])
        teacher = Teacher.objects.get(no=tno)
        if teacher:
            if request.path.startswith('/praise'):
                teacher.good_count += 1
            else:
                teacher.bad_count += 1
            teacher.save()
            code, hint = 10001, '操作成功'
    except (KeyError, ValueError, Teacher.DoesNotExist):
        pass
    return JsonResponse({'code': code, 'hint': hint})


def register(request):
    page, hint = 'register.html', ''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            page = 'login.html'
            hint = '注册成功，请登录'
        else:
            hint = '请输入有效的注册信息'
    return render(request, page, {'hint': hint})


def login(request):
    hint = ''
    if request.method == 'POST':
        if request.session.test_cookie_worked():  # 设置用于测试的 cookies
            request.session.delete_test_cookie()  # 删除用于测试的 cookies
            if request.session.get('is_login', None):  # 不允许重复登录
                return redirect('/')
            form = LoginForm(request.POST)
            if form.is_valid():
                captcha_from_user = form.cleaned_data['captcha']
                captcha_from_sess = request.session.get('captcha', '')  # 字典 get 若为空，返回''
                if captcha_from_sess.lower() != captcha_from_user.lower():  # lower 即把大写字符转化成小写
                    hint = '请输入正确的验证码'
                else:
                    username = form.cleaned_data['username']
                    password = form.cleaned_data['password']
                    user = User.objects.filter(username=username, password=password).first()  # 从数据库中查是否有匹配的账号密码
                    if user:  # 登录成功则将用户编号和用户名保存在 session 中
                        request.session['userid'] = user.no
                        request.session['username'] = user.username
                        request.session['is_login'] = True
                        return redirect('/')
                    else:
                        hint = '用户名或密码错误'
            else:
                hint = '请输入有效的登录信息'
        else:
            return HttpResponse("Please enable cookies and try again.")
    request.session.set_test_cookie()  # 由于 cookies 工作机制，只有下次客户请求的时候才能测试，所以最后放，等下次用。
    return render(request, 'login.html', {'hint': hint})


ALL_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def get_captcha_text(length=4):
    selected_chars = random.choices(ALL_CHARS, k=length)
    return ''.join(selected_chars)


def get_captcha(request):
    """获得验证码"""
    captcha_text = get_captcha_text()
    request.session['captcha'] = captcha_text
    image = Captcha.instance().generate(captcha_text)
    return HttpResponse(image, content_type='image/png')


def logout(request):
    """注销"""
    request.session.flush()
    return redirect('/')


def export_teachers_excel(request):
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('老师信息表')
    queryset = Teacher.objects.all().select_related('subject')

    colnames = ('姓名', '介绍', '好评数', '差评数', '学科')
    for index, name in enumerate(colnames):
        sheet.write(0, index, name)

    props = ('name', 'detail', 'good_count', 'bad_count', 'subject')
    for row, teacher in enumerate(queryset):
        for col, prop in enumerate(props):
            value = getattr(teacher, prop, '')
            if isinstance(value, Subject):  # subject 是个继承了 Subject 的类，所以要取 .name
                value = value.name
            sheet.write(row + 1, col, value)

    buffer = BytesIO()
    wb.save(buffer)

    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
    filename = quote('老师.xls')

    resp['content-disposition'] = f'attachment; filename = "{filename}"'
    return resp
