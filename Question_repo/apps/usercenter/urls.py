from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

#TemplateView  ==>  基于类的视图

urlpatterns = [
    url(r'^profile/$',views.ProfileView.as_view(),name='profile'),
    url(r'^change_passwd/$', views.ChangePasswordView.as_view(), name='change_passwd'),
    url(r'^answer/$',views.AnswerView.as_view(),name='answer'),
    url(r'^collect/$',views.CollectView.as_view(),name='collect'),
    url(r'^contribute/$',views.ContributeView.as_view(), name='contribute'),
    url(r'^approval/$', views.ApprovalView.as_view(), name='approval'),
    url(r'^approval/(?P<id>\d+)/$', views.ApprovalPassView.as_view(), name='approval_pass'),
]