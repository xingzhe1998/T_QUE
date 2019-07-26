from django.conf.urls import url
from . import views


urlpatterns = [
    #   获取手机验证码
    url(r'^get_mobile_captcha/$', views.get_mobile_captcha, name='get_mobile_captcha'),
    #   获取图形验证码
    url(r'^get_captcha/$', views.get_captcha, name='get_captcha'),
    #   检查图形验证码
    url(r'^check_capcha/$', views.check_captcha, name='check_captcha'),
    #datable所有问题
    url(r'^questions/$', views.questions, name='questions'),
    # 参考答案的接口
    url(r'^answer/(?P<id>\d+)/$', views.AnswerView.as_view(), name='answer'),
    # 某题所有人作答情况接口
    url(r'^other_answer/(?P<id>\d+)/$', views.OtherAnswerView.as_view(),name='other_answer'),
    # 答案收藏接口
    url(r'^answer/collection/(?P<id>\d+)/$', views.AnswerCollectionView.as_view(), name='answer_collection'),
    # 问题收藏接口
    url(r'^question/collection/(?P<id>\d+)/$',views.QuestionCollectionView.as_view(), name='question_collection'),
    url(r'^change_avator/$', views.ChangeAvator.as_view(), name='change_avator'),
    url(r'^question/contribute/$', views.QuestionsContributeView.as_view(), name='question_contribute'),
]