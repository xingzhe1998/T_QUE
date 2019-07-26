from django.shortcuts import render,HttpResponse
from django.http.response import JsonResponse
from django.views.generic import DetailView
from django.views.generic.base import View
from apps.repo.models import Category, Questions, Answers, AnswersCollection,QuestionsCollection,UserLog
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.template import loader
import json
from django.db import transaction
import logging
from libs.dynamic_user import recent_answer,recent_user
from django.contrib.auth.decorators import login_required
logger = logging.getLogger("apis")
# Create your views here.


def login(request):
    return  render(request, "accounts/login.html")

'''
# 排序
# '-' => 逆序
# 'last_modify'  => Answers表中的字段(class Answers)
# 传数据到前端 => 在前端显示
# order_by("-last_modify")
'''


###########################################################################

'''
将一些全局信息返回到前端的index页面
'''
@login_required
def index(request):
    kwgs = {
        'recent_user':recent_user,
        'recent_answer':recent_answer,
        'hot_question':Answers.objects.hot_question,
        'hot_user':Answers.objects.hot_user,
    }
    # recent_answer = Answers.objects.all().order_by("-last_modify")[:10]
    # kwgs = {'recent_answer':recent_answer}
    return  render(request, "accounts/index.html", kwgs)

###########################################################################

def register(request):
    return render(request,"accounts/register.html")



def questions(request):
    category = Category.objects.all()
    grades = Questions.DIF_CHOICES
    search = request.GET.get("search", "")
    # dict_keys(['search'])
    # print(request.GET.keys())
    # print(request.GET.get("search",""))
    # value="{{ search_key }}"  将base页面下的search_key的值替换成search
    kwgs = {"category":category, "grades":grades, 'search_key':search}
    "{'category': <QuerySet [<Category: python>, <Category: linux>, <Category: 数据结构>]>, " \
    "'grades': ((1, '入门'), (2, '简单'), (3, '中等'), (4, '困难'), (5, '超难')), 'search_key': ''}"
    # 将参数传递给html
    return  render(request, "accounts/questions.html", kwgs)




class QuestionDetail(LoginRequiredMixin,DetailView):
    # DetailView类需要这么配置
    model = Questions  #必须配资
    pk_url_kwarg = 'id'
    template_name = "accounts/question_detail.html"  #必须配置
    #  默认名：object
    context_object_name = "object"

    #额外传递my_answer

    def get_context_data(self, **kwargs):

        # Answers.objects.get(user=request.user) =>   AnswerObject =>  只适合取出有且只有一条的数据
        # Answers.objects.filter(user=request.user) => querySet => 能取出0~N条数据
        # kwargs：字典、字典中的数据返回给html页面
        # self.get_object() => 获取当前id的数据（问题）
        # question = self.get_object()  # 当前这道题目
        kwargs["my_answer"] = Answers.objects.filter(question=self.get_object(), user=self.request.user)
        kwargs["other_answer"] = Answers.objects.filter(question=self.get_object())
        # 调用父类的方法
        return super().get_context_data(**kwargs)

    # url 匹配时需要传递一个参数
    def post(self, request, id):
        try:
        # 元组：第一个元素获取/创建的对象
        # new_answer = Answers.objects.get_or_create(question=self.get_object(),user=self.request.user)
        # new_answer[0].answer
            try:
                with transaction.atomic():
                    # data_answer: 用户提交的数据
                    data_answer = request.POST.get('answer', "没有回答")

                    # 如何查询
                    new_answer = Answers.objects.get_or_create(question=self.get_object(), user=request.user)
                    new_answer[0].answer = data_answer
                    new_answer[0].save()
                    # raise ValueError('出错了')
                    # print(new_answer)
                    # '''(< Answers: xyz-手写：一个长度n的无序数字元素列表，如何求中位数，如何尽快的估算中位数，你的算法复杂度是多少； >, True)'''

                    #没有json.loads之前是一个json格式的字符串 ==> 需要转变为python对象才能进行后续操作
                    # user=self.request.user ==> 获取当前用户    question=self.get_object() ==> 获取当前问题
                    # UserLog.objects.create(user=self.request.user, question=self.get_object(),operate=3)
                    my_answer = json.loads(serializers.serialize("json", [new_answer[0]]))[0]

                    msg = "提交成功"
                    code = 200
                    result = {'code':code, 'msg':msg, 'my_answer':my_answer}
                    return JsonResponse(result)
                    # OPERATE = ((1, "收藏"), (2, "取消收藏"), (3, "回答"))
                    # raise  TypeError
                    # UserLog.objects.create(user=request.user, operate=3, question=self.get_object(), answer=new_answer[0])
            except Exception as ex:
                logger.error(ex)
                my_answer={}
                msg = "提交失败"
                code = 500
                result = {'code':code, 'msg':msg, 'my_answer': my_answer}
                return JsonResponse(result)
                # todo: 做一些判断=》 提交失败或其他异常情况
        except Exception as ex:
            print('some error')
            return JsonResponse({'status':0, 'msg':'some error'})



class AnswerCollectionView(LoginRequiredMixin, View):
    def get(self, request ,id):
        other_answer = Answers.objects.filter(question=id)
        if other_answer:
            for answer in other_answer:
                if AnswersCollection.objects.filter(answer=answer, user=request.user, status=True):
                    answer.collect_status = 1  # => 控制爱心=>空心/实心
                # 外键 AnswersCollectionObject.answer=>related_name
                # answer被收藏哪些人收藏了
                # answer.answers_collection_set.filter(status=True)
                answer.collect_nums = answer.answers_collection_set.filter(status=True).count()
                # answer.answers_collection_set
            # 通过后端渲染出HTML
            # html = loader.render_to_string('question_detail_other_answer.html', {"other_answer": other_answer})
            html = loader.get_template('accounts/question_detail_other_answer.html').render({"other_answer": other_answer})
            # print(html)
        else:
            html = "暂无回答"



class QuestionCollectionView(LoginRequiredMixin, View):
    def get(self ,request, id):
        # print(id)
        questions_list = Questions.objects.filter(title=id)
        if questions_list:
            for question in questions_list:
                if QuestionsCollection.objects.filter(question=question, user=request.user, status=True).count():
                    question.collect_status = 1
                # question.collec_nums = question.questions_collection_set.filter(status=True).count()
                html = loader.get_template('accounts/questions.html').render({"question_list":questions_list})
                # print(html)
            else:
                html = None

import random
def custom_403(request):
    return render(request, "accounts/403_custom.html", {'data':random.randint(1,100)}, status=403)

def custom_404(request):
    # return render(request, "accounts/404_custom.html", {'data': random.randint(1, 100)}, status=404)
    return render(request, "accounts/404.html", status=404)

def custom_500(request):
    return render(request, "accounts/500.html", status=500)