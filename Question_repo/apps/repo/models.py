from django.core.exceptions import ValidationError
from django.db import models
from apps.accounts.models import User
from .validator import valid_difficulty
from ckeditor_uploader.fields import RichTextUploadingField
# 含文件上传
# Create your models here.
"""题库"""


class Category(models.Model):
    """分类"""
    name = models.CharField("分类名称", max_length=64)

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"


class Tag(models.Model):
    """标签"""
    name = models.CharField("标签名", max_length=64)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"


class Questions(models.Model):
    """题库"""
    DIF_CHOICES = (
        (1, "入门"),
        (2, "简单"),
        (3, "中等"),
        (4, "困难"),
        (5, "超难"),
    )
    grade = models.IntegerField("题目难度", choices=DIF_CHOICES, validators=[valid_difficulty], null=True)
    category = models.ForeignKey(Category, verbose_name="所属分类", null=True)
    title = models.CharField("题目标题", unique=True, max_length=256)
    # 富文本编辑器
    content = RichTextUploadingField("题目详情", null=True)
    # 富文本编辑器
    answer = RichTextUploadingField("题目答案", null=True, blank=True)
    '''
    from django.db.models.fields.related import (  # isort:skip
    ForeignKey, ForeignObject, OneToOneField, ManyToManyField,
    ManyToOneRel, ManyToManyRel, OneToOneRel,
    )
    '''
    contributor = models.ForeignKey(User, verbose_name="贡献者", null=True)
    pub_time = models.DateTimeField("入库时间", auto_now_add=True, null=True)
    # 审核状态
    status = models.BooleanField("审核状态", default=False)
    # 数组....(会产生一个中间表)
    tag = models.ManyToManyField(Tag, verbose_name="题目标签")


    class Meta:
        verbose_name = "题库"
        verbose_name_plural = verbose_name
        permissions = (
                        ('can_change_question', "可以修改题目信息"),
                       ('can_add_question', "可以添加题目信息"),
                       )

    def __str__(self):
        return f"{self.id}:{self.title}"


from django.db.models import Count


class AnswersManager(models.Manager):
    def hot_question(self):
        import datetime
        today_30 = datetime.date.today() + datetime.timedelta(days=-30)
        question = self.filter(last_modify__gte=today_30).values("question_id","question__title").annotate(Count("user")).order_by("-user__count")[:10]
        # question = self.raw("select repo_answers.id as answer_id, repo_questions.id as id, count(repo_answers.id) as answer_num, repo_questions.title, repo_questions.grade from repo_answers left join repo_questions on repo_answers.question_id = repo_questions.id GROUP BY repo_questions.title ORDER BY answer_num desc limit 5;")
        '''
        <QuerySet [{'question_id': 1941, 'user__count': 2}, {'question_id': 1942, 'user__count': 2}, 
        {'question_id': 1944, 'user__count': 2}, {'question_id': 1945, 'user__count': 1}, 
        {'question_id': 1946, 'user__count': 1}, {'question_id': 1953, 'user__count': 1}, 
        {'question_id': 1956, 'user__count': 1}, {'question_id': 1957, 'user__count': 1}, 
        {'question_id': 1961, 'user__count': 1}, {'question_id': 1965, 'user__count': 1}, 
        {'question_id': 2400, 'user__count': 1}]>
        '''
        return question

    def hot_user(self):
        import datetime
        '''
        >>> today_30 = datetime.date.today()
        >>> today_30
        datetime.date(2019, 5, 12)
        相当于在今天的日期上减去三十天
        >>> today_30 = datetime.date.today() + datetime.timedelta(days=-30)
        >>> today_30
        datetime.date(2019, 4, 12)
        '''
        today_30 = datetime.date.today() + datetime.timedelta(days=-30)
        user_rank = self.filter(last_modify__gte=today_30).values('user__username').annotate(Count('id')).order_by("-id__count")[:5]
        return user_rank

'''
>>> Answers.objects.values_list('user__username')
<QuerySet [('xyz',), ('xyz',), ('xyz',), ('xyz',), ('xyz',), ('xyz',), ('xyz',), ('user01',), ('user01',), ('user01',), ('user01',), ('user01',), ('user01',), ('user01',)]>
>>> Answers.objects.values('user__username')
<QuerySet [{'user__username': 'xyz'}, {'user__username': 'xyz'}, {'user__username': 'xyz'}, {'user__username': 'xyz'}, {'user__username': 'xyz'}, {'user__username': 'xyz'}, {'user__username': 'xyz'}, {'user__username': 'user01'}, {'user__username': 'user01'}, {'user__username': 'user01'}, {'user__username': 'user01'}, {'user__username': 'user01'}, {'user__username': 'user01'}, {'user__username': 'user01'}]>
>>> Answers.objects.values('user__username').annotate(Count("id")).order_by("-id__count")[:5]
<QuerySet [{'user__username': 'user01', 'id__count': 7}, {'user__username': 'xyz', 'id__count': 7}]>

'''


class Answers(models.Model):
    """答题记录"""
    # Answers.objects = AnswersManger  继承了该类 不需要makemigrations
    # 但是这样做的目的何在？
    objects = AnswersManager()
    # exam = models.ForeignKey(ExamQuestions, verbose_name="所属试卷", null=True, blank=True)

    question = models.ForeignKey(Questions, verbose_name="题目")
    answer = models.TextField(verbose_name="学生答案")
    user = models.ForeignKey(User, verbose_name="答题人")
    create_time = models.DateTimeField(auto_now_add=True)
    last_modify = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "答题记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user}-{self.question.title}"


class QuestionsCollection(models.Model):
    """收藏问题
    ForeignKey外健，继承自class ForeignKey(ForeignObject)类
    里面定义了一些属性
    def __init__(self, to, on_delete=None, related_name=None, related_query_name=None,
        limit_choices_to=None, parent_link=False, to_field=None,
        db_constraint=True, **kwargs):
    """
    '设置外健的目的是为了能够在本类中(表)调用其它字段--> 从而生成自己的列？？？'
    question = models.ForeignKey(Questions, verbose_name="问题", related_name='questions_collection_set')
    user = models.ForeignKey(User, verbose_name="收藏者", related_name='questions_collection_set')
    create_time = models.DateTimeField("收藏/取消时间", auto_now=True)
    # True表示收藏 ,False表示未收藏
    status = models.BooleanField("收藏状态", default=True)

    class Meta:
        verbose_name = "收藏记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        if self.status: ret="收藏"
        else: ret="取消收藏"
        return f"{self.user}:{ret}:{self.question.title}"


class AnswersCollection(models.Model):
    """收藏答案"""
    answer = models.ForeignKey(Answers, verbose_name="答题记录", related_name='answers_collection_set')
    user = models.ForeignKey(User, verbose_name="收藏者", related_name='answers_collection_set')
    create_time = models.DateTimeField("收藏/取消时间", auto_now=True)
    # True表示收藏 ,False表示未收藏
    status = models.BooleanField("收藏状态", default=True)

    class Meta:
        verbose_name = "收藏记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        if self.status: ret="收藏"
        else: ret="取消收藏"
        return f"{self.user}:{ret}:{self.answer}"


import logging
logger = logging.getLogger("repo")
class UserLog(models.Model):
    """用户行为日志"""
    OPERATE = ((1,"收藏"),(2,"取消收藏"),(3,"回答"))
    user = models.ForeignKey(User,verbose_name="用户")
    operate = models.CharField(choices=OPERATE, max_length=1 ,verbose_name="操作")
    question = models.ForeignKey(Questions, verbose_name="题目", null=True, blank=True)
    answer = models.ForeignKey(Answers, verbose_name="回答", null=True, blank=True)
    update_time = models.DateTimeField(verbose_name="回答时间",auto_now_add=True)
    class Meta:
        verbose_name = "日志"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        #检查question和answer两者不能全为空
        #self => 当前用户日志
        if self.question or self.answer:
            super().save()
        else:
            msg = "日志必须选择一个操作对象"
            logger.error(msg)
            raise ValidationError(msg)

    def __str__(self):
        msg = ""
        if self.question:
            msg = self.question.title
        elif self.answer:
            msg = self.answer
        return f"{self.user}{self.operate}{msg}"