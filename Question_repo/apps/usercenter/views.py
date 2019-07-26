from django.shortcuts import render, HttpResponse, redirect
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import View
from django.views.generic import ListView
from .forms import FindPwd
import logging
from apps.repo.models import Answers,QuestionsCollection,AnswersCollection,Questions
logger = logging.getLogger("account")
# Create your views here.
# def profile(request):
#     return render(request,'accounts/uc_profile.html')


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/uc_profile.html')

    def post(self, request):
        ret_info = {'code':200, 'msg':'修改成功'}

        try:
            if request.POST.get("email"):
                print("change email")
                request.user.email = request.POST.get("email")

            if request.POST.get("mobile"):
                print('change mobile')
                # 有点不太清楚 ==> 这个request里面包含的时表格中的数据吧
                # ==> 但是它为什么又可以调用user这个实例呢？？
                request.user.mobile = request.POST.get("mobile")
            if request.POST.get("realname"):
                print("change realname")
                request.user.realname = request.POST.get("realname")
            if request.POST.get("qq"):
                print("change qq")
                request.user.qq = request.POST.get("qq")
            request.user.save()

        except Exception as ex:
            ret_info = {'code':200, 'msg':'修改失败'}
        return render(request, 'accounts/uc_profile.html', {'ret_info':ret_info})


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/uc_change_passwd.html')

    def post(self, request):
        ret_info = {
            'code':200,
            'msg':'修改成功',
        }
        try:
            oldpassword = request.POST.get('oldpassword')
            newpassword1 = request.POST.get('newpassword1')
            newpassword2 = request.POST.get('newpassword2')

            if newpassword1 != newpassword2:
                ret_info = {
                    'code':500,
                    'msg':'密码修改失败'
                }

            else:
                # authenticate验证的返回结果是True 或者 False
                user = auth.authenticate(request, username=request.user.username,password=oldpassword)
                if user:
                    user.set_password(newpassword1)
                    user.save()
                    auth.logout(request)

                else:
                    ret_info = {
                        'code': 500,
                        'msg': '旧密码输入有误'
                    }

        except Exception as ex:
            ret_info = {
                'code': 500,
                'msg': '出现意外错误'
            }

        return render(request,'accounts/uc_change_passwd.html',{'ret_info':ret_info})




class AnswerView(LoginRequiredMixin, ListView):
    context_object_name = "my_answers"
    template_name = "accounts/uc_answer.html"

    # 自定义查询
    # self.request.user ==> 这是啥？
    def get_queryset(self):
        return Answers.objects.filter(user=self.request.user)


class CollectView(LoginRequiredMixin, ListView):
    context_object_name = "my_collections"
    template_name = "accounts/uc_collect.html"

    def get_queryset(self):
        my_question_collections = QuestionsCollection.objects.filter(user=self.request.user)
        my_answer_collections = AnswersCollection.objects.filter(user=self.request.user)
        return my_answer_collections,my_question_collections
######################返回的是一个元组类型，切记切记


class ContributeView(LoginRequiredMixin, ListView):
    context_object_name = 'my_contribute'
    template_name = 'accounts/uc_contribut.html'

    def get_queryset(self):
        return Questions.objects.filter(contributor=self.request.user)



from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
class ApprovalView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # 'app.权限'
    permission_required = ('repo.can_change_question_status',)
    # 如果权限不够,是做跳转还是403, True=>403(默认False)
    raise_exception = True

    def get(self, request):
        # print(request.user.get_all_permissions())
        # 排除所有审核已经通过的题目信息 ==> 得到暂未通过的以及未提交的
        questions = Questions.objects.exclude(status=True)
        return render(request, "accounts/uc_approval.html", {"questions": questions})  # 这个字典的key就是传递到前端的变量


class ApprovalPassView(LoginRequiredMixin, PermissionRequiredMixin,View):
    # 'app.权限'
    permission_required = ('repo.can_change_question_status',)
    # 如果权限不够,是做跳转还是403, True=>403(默认False)
    raise_exception = True

    def get(self, request, id):
        try:
            Questions.objects.filter(id=id).update(status=True)
            ret = {"code": 200, "msg": "成功"}
        except:
            ret = {"code": 500, "msg": "失败"}
        return JsonResponse(ret)

