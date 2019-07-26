from django.contrib import admin
from .models import Category,Tag,Questions,User
# Register your models here.

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Questions)
admin.site.register(User)