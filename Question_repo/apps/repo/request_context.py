from question_repo.settings import WEB_NAME
from apps.repo.models import Category,Answers
from libs.repo_data import user_answer_data
def global_data(request):
    no = 1
    site = {}
    site["WEB_NAME"] = WEB_NAME
    # return {"no":1, "site":{"WEB_NAME":settings.WEB_NAME}}
    # {{ site.WEB_NAME }}
    #{{ }}
    if request.user.is_authenticated:
        hot_user = Answers.objects.hot_user()
        hot_question = Answers.objects.hot_question()
        user_data = user_answer_data(request.user)
    cate = Category.objects.all()
    return locals()