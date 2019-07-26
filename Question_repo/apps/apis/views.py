from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from io import BytesIO
from django.db.models import Q
import base64,random
from libs.sms import send_sms
from libs import patcha
from apps.repo.models import Questions, Answers, AnswersCollection, QuestionsCollection, UserLog
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.template import loader, Context
import logging
from django.forms.models import model_to_dict
logger = logging.getLogger("repo")
from django.db import transaction
from question_repo.settings import MEDIA_ROOT,MEDIA_URL
# Create your views here.

def get_mobile_captcha(request):
    # ret => 'josn' {'code':200. 'msg':'success/failed/connection erro', 'data':[1.2.3.4]}
    mobile = request.GET.get("mobile")
    if not mobile:
        #  400 表示用户填写有误
        ret = {"code":400, "msg":"手机号输入有误"}
    else:
        mobile_captcha = "".join(random.choices('0123456789', k=6))
        # 将验证码写入cacha => redis  '300' => 验证码过期时间
        # cache.set(mobile,mobile_captcha,300)
        #send info
        if send_sms(mobile, mobile_captcha):
            ret = {"code":200,"msg":"发送成功"}
        else:
            ret = {"code":500,"msg":"发送短信失败"}
    return JsonResponse(ret)


def get_captcha(request):
    # PIL 创建图片
    # 图形非常小、非常多、临时使用
    # 存放到内存 => data:
    # 直接在内存开辟一点空间存放临时生成的图片
    f = BytesIO()
    # 调用check_code生成照片和验证码
    img, code = patcha.create_validate_code()
    # 将验证码存在服务器的session中，用于校验
    request.session['captcha_code'] = code
    # 生成的图片放置于开辟的内存中
    img.save(f, 'PNG')
    # 将内存的数据读取出来，并以HttpResponse返回
    # return HttpResponse(f.getvalue())
    ret_type = "data:image/jpg;base64,".encode()
    # 图片的真实信息
    ret = ret_type+base64.encodebytes(f.getvalue())
    del f
    return HttpResponse(ret)

def check_captcha(request):
    pass

def questions(request):
    # 获取参数
    pagesize = int(request.GET.get("limit", 10))
    # offset 表示距离第一条数据的距离
    offset = int(request.GET.get("offset", 0))
    page = int(request.GET.get("page", 1))
    grade = int(request.GET.get("grade", 0))
    status = int(request.GET.get("status", 2))
    # 2: 不筛选， 1，已刷，0，待刷
    category = int(request.GET.get("category", 0))
    # print(category) ==> 默认为0
    # 这里的数据提交为什么是GET方法
    search = request.GET.get("search", "")

    # print(type(pagesize), type(offset))    'str'  'int'
    # 取出所有数据
    questions_list = Questions.objects.all()
    # 根据搜索内容进行查询
    if search:
        if search.isdigit():
            questions_list = questions_list.filter(
                Q(id=search) | Q(content__icontains=search) | Q(title__icontains=search))
        else:
            questions_list = questions_list.filter(Q(content__icontains=search) | Q(title__icontains=search))

    if grade: questions_list = questions_list.filter(grade=grade)
    if category: questions_list = questions_list.filter(category__id=category)

    questions_list = questions_list.values('id','title','grade','answer') #不能给不存在的字段
    total = len(questions_list)
    # 计算当前页面的数据
    questions_list = questions_list[offset:offset+pagesize]    #切片操作时下标必须为整数
    for question in questions_list:

        if QuestionsCollection.objects.filter(question__id=question["id"], user=request.user, status=True):
            question["collect_status"] = 1
        # question.collect_nums = question.answers_collection_set.filter(status=True).count()
    # for items in questions_list:
    #     print(items)
    # html = loader.get_template('accounts/question_detail_other_answer.html').render({"total":total,"question_list": questions_list})
    questions_dict = {'total':total, 'rows':questions_list}
# 这里返回的dict格式数据是否就是浏览器xhr下的questions文件？？？
    return JsonResponse(questions_dict)


# 调用参考答案表
class AnswerView(LoginRequiredMixin, View):
    """参考答案"""
    def get(self, request, id):
        # answer = Questions.objects.get(id=id)
        print('HELLO this is -> AnswerView -> apis')
        my_answer = Answers.objects.filter(question=id, user=request.user)
        if not my_answer:
            question = {"answer": "请回答后再查看参考答案"}
            return JsonResponse(question, safe=False)

        try:
            # model_to_dict适合Model-Object
            # serializers适合queryset
            # question = model_to_dict(Questions.objects.get(id=id))
            # question = serializers.serialize('json', Questions.objects.filter(id=id))
            # question = serializers.serialize('json', Questions.objects.filter(id=id))
            question = Questions.objects.filter(id=id).values()[0]
        except Exception as ex:
            print(ex)
            question = None
        return JsonResponse(question, safe=False)


# 调用某一问题全部作答情况表
class OtherAnswerView(LoginRequiredMixin, View):
    def get(self, request, id):
        # other_answer = list(Answers.objects.filter(question=id).values())
        # other_answer = serializers.serialize('json', Answers.objects.filter(question=id))
        # return JsonResponse(other_answer, safe=False)
        # question = id 表示问题详情页下的问题

        # 个人的作答情况
        my_answer = Answers.objects.filter(question=id, user=request.user)
        if not my_answer:
            html = "请回答后再查看其他答案"
            return HttpResponse(html)

        # other_answer = Answers.objects.filter(question=id).exclude(user=request.user)

        '''他人的作答情况，与my_answer比起来少个了user的查询限制'''
        other_answer = Answers.objects.filter(question=id)
        print('HELLO this is -> OtherAnswerView -> api')

        if other_answer:
            for answer in other_answer:
                # 如果AnswersCollection表中能查询到  ==>当前用户，回答了当前的问题且收藏状态为真的话
                if AnswersCollection.objects.filter(answer=answer, user=request.user, status=True):
                    # 这个状态是自定义的  ==> 前端根据这个数值来判断答案收藏是实心还是空心的
                    answer.collect_status = 1
                answer.collect_nums = answer.answers_collection_set.filter(status=True).count()
                # answer.answers_collection_set
            # 通过后端渲染出HTML
            html = loader.get_template('accounts/question_detail_other_answer.html').render({"other_answer": other_answer})
            # print(html)
        else:
            html = "暂无回答"
        return HttpResponse(html)


# 调用答案收藏表
class AnswerCollectionView(LoginRequiredMixin, View):
    def get(self, request, id):
        try:
            answer = Answers.objects.get(id=id)
            with transaction.atomic():
                result = AnswersCollection.objects.get_or_create(user=self.request.user, answer=answer)
                '''
                print(result)
                # 这个数据是要传递给前端 所以前端提取数据要根据这里的数据格式
                # (<AnswersCollection: xyz:取消收藏:xyz-单向链表如何使用快速排序算法进行排序；>, False)
                # 因为这个是get_or_create方法 ==> 默认True表示新创建,False表示老数据   
                # 而底下的answer_collection.status = True/Flase 与这个不同
                '''
                answer_collection = result[0]
                print('HELLO this is -> AnswerCollectionView -> apis')
                # print(result[1])
                if not result[1]:
                    # 老数据
                    # print('x',answer_collection.status)
                    # True改False , False改True
                    # todo 至于这里为什么可以取status 可以取看哪个answercollection表单，里面有个字段叫做ststus
                    if answer_collection.status:
                        answer_collection.status = False
                    else:
                        answer_collection.status = True
                answer_collection.save()
                # raise ValueError("出错了！")
                msg = model_to_dict(answer_collection)
                print(type(msg))

                # UserLog.objects.create(user=self.request.user, answer=answer, operate=1 or 2)
                # logger.info(msg)
                msg["collections"] = answer.answers_collection_set.filter(status=True).count()
                ret_info = {"code": 200, "msg": msg}
                print(ret_info)
                return JsonResponse(ret_info)
        except Exception as ex:
            logger.error(ex)
            code=500
            info ="收藏答案失败"
            msg = []
            ret_info = {"code":code, "info":info, 'msg':msg}
            return JsonResponse(ret_info)



# 调用问题收藏表
class QuestionCollectionView(LoginRequiredMixin,View):
    def get(self, request, id):
        try:
            question = Questions.objects.get(id=id)
            with transaction.atomic():
                '当前题目'
                # category = int(request.GET.get("category", 0))
                result = QuestionsCollection.objects.get_or_create(user=request.user,question=question)
                question_collection = result[0]
                if not result[1]:
                    # 老数据
                    # print('x',answer_collection.status)
                    # True改False , False改True
                    if question_collection.status:
                        question_collection.status = False
                    else:
                        question_collection.status = True
                question_collection.save()
                # raise ValueError("出错了！")
                msg = model_to_dict(question_collection)
                print(msg)
                # logger.info(msg)
                msg["collections"] = question.questions_collection_set.filter(status=True).count()
                ret_info = {"code":200,"msg":msg}
                return JsonResponse(ret_info)
        except Exception as ex:
            logger.error(ex)
            info = "收藏问题失败"
            msg = []
            code = 500
            ret_info = {"code":code, "info":info, "msg":msg}
            return JsonResponse(ret_info)

import datetime,time,os
class ChangeAvator(LoginRequiredMixin, View):
    def post(self, request):

        today = datetime.date.today().strftime("%Y%m%d")
        # 需要弄清楚这个image信息是从哪里获取传递过来的
        #/media/avator/20190513/bg_02.jpg
        img_src_str = request.POST.get("image")
        # print(img_src_str)

        img_str = img_src_str.split(',')[1]
        # print(img_str)    ==> 很长一串字符
        # 取出格式
        img_type = img_src_str.split(';')[0].split('/')[1]

        # 取出数据
        img_data = base64.b64decode(img_str)

        # 相对上传路径
        avator_path = os.path.join("avator",today)

        # 绝对上传路径
        avator_path_full = os.path.join(MEDIA_ROOT, avator_path)

        if not os.path.exists(avator_path_full):
            os.mkdir(avator_path_full)

        filename = str(time.time())+"."+img_type
        # 绝对文件路径，用于保存图片
        # print('step four')
        filename_full = os.path.join(avator_path_full, filename)
        # 相对MEDIA_URL路径，用于展示数据
        img_url = f'{MEDIA_URL}{avator_path}/{filename}'

        try:
            with open(filename_full, 'wb') as fp:
                fp.write(img_data)
            ret = {
                'resule':'ok',
                'file':img_url,
            }
        except Exception as ex:
            ret = {
                'result':'error',
                'file':'upload fail',
            }
        # print('check erro')
        request.user.avator_sor = os.path.join(avator_path,filename)
        request.user.save()
        return JsonResponse(ret)

class QuestionsContributeView(LoginRequiredMixin, View):
    def post(self, request):
        question_title = request.POST.get('title')
        category = request.POST.get('category')
        question_content = request.POST.get('content')
        try:
            if category:
                # 为什么这里的catogory是个数字 ==> 前端页面上这里对应的是个下拉框 ==>
                Questions.objects.create(title=question_title, category_id=category, content=question_content, contributor=request.user)
            else:
                Questions.objects.create(title=question_title, content=question_content, contributor=request.user)
        except Exception as ex:
            logger.error(ex)
            return HttpResponse('提交失败')

        return HttpResponse('提交成功')