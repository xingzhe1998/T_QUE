from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from .models import User
from django.contrib.auth.hashers import check_password as auth_check_password

"""

注册表单：
        表单：用户名，手机号，两个密码，验证码
        - 添加用户名检查：用户名不能重复
        - 添加手机号检查： 手机号不能重复
        - 添加密码检查： 两次密码要相同
        - 添加密码复杂度检查： 不能为纯数字
"""


# Create your models here.

#继承自AbstractUser
# 用户注册
class RegisterForm(forms.Form):
    username = forms.CharField(label="用户名", max_length="24", widget=widgets.TextInput(attrs={"class":"form-control", "placeholder": "请输入用户名"}))
    mobile = forms.CharField(label="手机号", max_length="24",widget=widgets.TextInput(attrs={"class":"form-control", "placeholder": "请输入手机号"}))
    password = forms.CharField(label="密 码", widget=widgets.PasswordInput(attrs={"class":"form-control", "placeholder": "请输入密码"}))
    password2 = forms.CharField(label="密 码2", widget=widgets.PasswordInput(attrs={"class":"form-control", "placeholder": "请再输入密码"}))
    mobile_captcha = forms.CharField(label="验证码", widget=widgets.TextInput(attrs={"style":"width: 160px;padding: 10px", "placeholder":"验证码", "error_messages": {"invalid": "验证码错误"}}))


    "cleaned_data 就是读取表单返回的值，返回类型为字典dict型email=cleaned_data['email']  读取name为 ‘email’的表单提交值，并赋予 email变量"
    def clean_username(self):
        ret = User.objects.filter(username=self.cleaned_data.get("username"))
        if not ret:
            return self.cleaned_data.get("username")
        else:
            raise ValidationError("用户名已注册")

    def clean_mobile(self):
        ret = User.objects.filter(mobile=self.cleaned_data.get("mobile"))
        if not ret:
            return self.cleaned_data.get("mobile")
        else:
            raise ValidationError("手机号已绑定")

    def clean_password(self):
        data = self.cleaned_data.get("password")
        if not data.isdigit():
            return self.cleaned_data.get("password")
        else:
            raise ValidationError("密码不能全是数字")

    def clean(self):
        if self.cleaned_data.get("password") == self.cleaned_data.get("password2"):
            print(self.cleaned_data)
            return self.cleaned_data
        else:
            raise ValidationError("两次密码不一致")


class LoginForm(forms.ModelForm):
    captcha = forms.CharField(label="验证码", widget=widgets.TextInput(attrs=
                {"style":"width: 160px;padding: 10px", "placeholder":"验证码", "onblur":"check_captcha()", "error_messages": {"invalid": "验证码错误"}}))

    class Meta:
        model = User
        fields = ['username','password']
        widgets = {'username': widgets.TextInput(attrs={"class": "form-control", "placeholder":"用户名"}),"password": widgets.PasswordInput(attrs={"class": "form-control","placeholder": "密 码"})}

    def check_password(self):
        print('check password')
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        try:
            user = User.objects.get(username=username)
            return user, auth_check_password(password, user.password)
        except:
            return None, False