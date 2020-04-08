from django.http import JsonResponse
from django.shortcuts import redirect

LOGIN_REQUIRED_URLS = {
    '/praise/', '/criticize/'
}


class check_login_middleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # 配置和初始化

    def __call__(self, request):

        if request.path in LOGIN_REQUIRED_URLS and not request.session.get('is_login', None):
            if request.is_ajax():
                return JsonResponse({'code': 10003, 'hint': '请先登录'})
            else:
                backurl = request.get_full_path()
                return redirect(f'/login/?backurl={backurl}')

        # 在这里编写视图和后面的中间件被调用之前需要执行的代码
        # 这里其实就是旧的process_request()方法的代码

        response = self.get_response(request)

        # 在这里编写视图调用后需要执行的代码
        # 这里其实就是旧的process_response()方法的代码

        return response
