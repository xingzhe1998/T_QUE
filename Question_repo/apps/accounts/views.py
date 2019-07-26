from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.views.generic.base import View
from .forms import RegisterForm,LoginForm
from .models import User
import logging
from django.core.cache import cache
logger = logging.getLogger('account')


def index(request):
    return render(request, 'accounts/index.html')


class Register(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'accounts/register.html',{"form":form})

    #Ajax提交表单
    def post(self,request):
        # request.POST ==> 获取前端页面上一post方式提交的表单中的信息
        form = RegisterForm(request.POST)
        ret = {}
        if form.is_valid():
            username = form.cleaned_data["username"]
            password= form.cleaned_data["password"]
            mobile = form.cleaned_data["mobile"]
            mobile_capcha = form.cleaned_data["mobile_captcha"]
            mobile_capcha_redis = cache.get(mobile)
            if mobile_capcha == mobile_capcha_redis:
                user = User.objects.create(username=username, password=make_password(password))
                user.save()
                ret['status'] = 200
                ret['msg'] = '注册成功'
                #############################
                return redirect(reverse("accounts:login"))
    ##########################################################
            else:
                ret["status"] = 300
                ret["msg"] = "验证码输入有误"
        else:
            ret["status"] = 400
            ret["msg"] = "填入的用户名或者密码不符合标准"
        return render(request,"accounts/register.html",{"form":form,"msg":ret})

class Login(View):
    def get(self, request):
        # 如果用户已经登录 ==> 跳转到index页面即可
        if request.user.is_authenticated:
            return redirect(reverse('repo:index'))
        form = LoginForm()
        request.session["next"] = request.GET.get('next',reverse('repo:index'))
        return render(request, "accounts/login.html", {"form":form})

    def post(self, request):
        # 表单数据绑定
        form = LoginForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        captcha = request.POST.get("captcha")
        session_captcha_code = request.session.get("captcha_code","")
        logger.debug(f"登录提交验证码:{captcha}-{session_captcha_code}")
        # if captcha.lower() == session_captcha_code.lower():
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            logger.info(f"{username}登录成功")
            msg = '登录成功'
            # 跳转到next
            return redirect(request.session.get("next",'/'))
        msg = "用户名或密码错误"
            # logger.error(f"{username}登录失败, 用户名或密码错误")
        # else:
        #     msg = "验证码错误"
        #     logger.error(f"{username}登录失败, 验证码错误")
        return render(request, "accounts/login.html", {"form": form, "msg":msg})


def logout(request):
    username = request.POST.get('username')
    logger.info('{}登录成功'.format(username))
    auth.logout(request)
    return redirect(reverse('accounts:login'))




from .models import FindPassword
import random,string
class PasswordForget(View):
    def get(self, request):
        return render(request, 'accounts/uc_findpassword.html')

    def post(self, request):
        print('xxxxxxxxxxxx')
        email = request.POST.get('email')
        if email and User.objects.filter(email=email):
            verify_code = "".join(random.choices(string.ascii_lowercase+string.digits,k=128))
            url = '{0}://{1}/accounts/password/reset/{2}?email={3}'.format(request.scheme,request.META['HTTP_HOST'], verify_code, email)
            print(url)
            '''
            >>> FindPassword.objects.get_or_create(email=email)
            (<FindPassword: FindPassword object>, False)
            '''
            ret = FindPassword.objects.get_or_create(email=email)
            print(ret[0].verify_code)
            # 第一次发送邮件时ret[0].verify_code 是没有值的
            ret[0].verify_code = verify_code
            ret[0].status = False
            ret[0].save()
            # print('发邮件')
            send_mail("注册用户验证",url, None, [email])
            return HttpResponse("邮件发送成功")
        else:
            msg = "输入的邮箱不存在"
            return render(request, "accounts/uc_findpassword.html",{"msg":msg})




class PasswordReset(View):
    # url上面的数据 verify_code
    def get(self, request, verify_code):
        import datetime
        # 零时区减去三十分钟 ==> 三十分钟之前零时区的时间 ==> 数据库添加数据默认是以零时区为标准计时的
        create_time_newer = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        print(create_time_newer, verify_code)
        email = request.GET.get("email")
        # find_password = FindPassword.objects.filter(status=False, verify_code=verify_code, creat_time__gte=create_time_newer, email=email)
        # 邮箱、verify_code、status=False、时间近30分钟
        # status ==> 是否被重置 False ==> 没有被重置
        # gte ==> 大于等于
        find_password = FindPassword.objects.filter(status=False, verify_code=verify_code, email=email,creat_time__gte=create_time_newer)
        if verify_code and find_password:
            # 这里是要先验证链接是否有效，有效的话就跳转到重置密码页面 ==> 之后用户输入密码之后 ==> 传递到后端 ==> 用此时图函数的post方法来判断数据
            return render(request, "accounts/uc_resetpassword.html")
        else:
            return HttpResponse("链接失效或有误")

    def post(self, request, verify_code):
        pass