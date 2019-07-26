from django.conf.urls import url
from . import views

#TemplateView  ==>  基于类的视图

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'question/$',views.questions ,name='questions'),
    #  捕获一个参数  详情页url地址  基于类的视图
    #  参数命名题目id
    url(r'^question_detail/(?P<id>\d+)/$', views.QuestionDetail.as_view(), name='question_detail'),
]