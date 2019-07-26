from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from apps.accounts.models import User
from django.contrib.auth.hashers import check_password as auth_check_password

class FindPwd(forms.Form):
    email = forms.CharField(label='邮箱号码',max_length=20,widget=widgets.TextInput(attrs={"class":"form-control", "placeholder": "请输入邮箱地址"}))

    def clean_email(self):
        ret = User.objects.filter(email=self.cleaned_data.get('email'))
        if not ret:
            return self.cleaned_data.get("email")

        else:
            raise ValidationError('该邮箱未绑定')



