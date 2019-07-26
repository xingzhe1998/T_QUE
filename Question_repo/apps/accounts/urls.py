from django.conf.urls import url
from . import views

#TemplateView  ==>  基于类的视图

urlpatterns = [
    # url(r'register/$', TemplateView.as_view(template_name="accounts/register.html")),
    # url(r'register/$', views.register, name="register"),
    url(r'^register/$', views.Register.as_view(), name='register'),
    # url(r'^login/$',TemplateView.as_view(template_name='accounts/login.html'),name='login'),
    #基于类的url
    url(r'^login/$',views.Login.as_view(),name='login'),
    #基于函数的url
    url(r'^logout/$',views.logout,name='logout'),
    url(r'^password/forget/$',views.PasswordForget.as_view(), name='password_forget'),
    url(r'password/reset/(\w+)$', views.PasswordReset.as_view(), name="password_reset"),
]