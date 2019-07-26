from django.db import models
from django.contrib.auth.models import AbstractUser
from easy_thumbnails.fields import ThumbnailerImageField
from django.db.models.fields.files import ImageFieldFile
import os
from question_repo.settings import MEDIA_ROOT,THUMB_SIZE
from libs.make_thumb import make_thumb

# Create your models here.

#继承自AbstractUser
class User(AbstractUser):
    realname = models.CharField(max_length=8, verbose_name="真实姓名")
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    qq = models.CharField(max_length=11, verbose_name="QQ号")
    # avator_sor = ThumbnailerImageField(upload_to="avator/%Y%m%d/", default="avator/default.jpg", verbose_name="头像")
    avator_sor = ThumbnailerImageField(upload_to="avator/%Y%m%d/", default="avator/girls_02.jpg", verbose_name="头像")
    avator_sm = models.ImageField("头像缩略图", upload_to="avator/%Y%m%d/", default='avator/girls_02.jpg.50x50_q85_crop.jpg')

    def save(self, *args, **kwargs):
        # print('abcdefgxxxs')
        super().save()

        if self.avator_sor.name == 'avator/girls_02.jpg':
            return

        # /Users/apple/PycharmProjects/T_question_repo/media
        if not os.path.exists(os.path.join(MEDIA_ROOT,self.avator_sor.name)):
            return

        '''
        >>> base,ext = os.path.splitext(user.avator_sor.name)
        >>> base,ext
        ('avator/girls_02', '.jpg')
        '''

        base, ext = os.path.splitext(self.avator_sor.name)
        thumb_pixbuf = make_thumb(os.path.join(MEDIA_ROOT, self.avator_sor.name),size=THUMB_SIZE)
        if thumb_pixbuf:
            # 缩略图文件的保存路径
            thumb_path = os.path.join(MEDIA_ROOT, base+f".{THUMB_SIZE}x{THUMB_SIZE}"+ext)
            # 缩略图相对路径
            relate_thumb_path = base+f'.{THUMB_SIZE}x{THUMB_SIZE}'+ext
            # avator/20190513/bg_02.70x70.jpg
            print(relate_thumb_path)

            thumb_pixbuf.save(thumb_path)
            #保存字段的值
            self.avator_sm = ImageFieldFile(self, self.avator_sm,relate_thumb_path)
            super().save()


class FindPassword(models.Model):
    verify_code = models.CharField(max_length=128, verbose_name="验证码")
    email = models.EmailField(verbose_name="邮箱",unique=True)
    creat_time = models.DateTimeField(auto_now=True, verbose_name="重置时间")
    status = models.BooleanField(default=False, verbose_name="是否已重置")