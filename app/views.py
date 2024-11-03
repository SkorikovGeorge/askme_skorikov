from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

QUESTIONS = [
    {
        "title": f"Question title {i}",
        "id": i,
        "text": f" Question text {i}"
    } for i in range(1, 30)
]

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_num = request.GET.get('page', 1)
    try:
        page = paginator.page(page_num)
    except(PageNotAnInteger, EmptyPage):
        page = paginator.page(1)
    return page

def index(request):
    page = paginate(QUESTIONS, request, 5)
    return render(request, "index.html", context={"questions": page.object_list, "page_obj": page})

def question(request, question_id):
    item = QUESTIONS[question_id-1]
    answers = [
    {
        "text": f"Answer text {i}"
    } for i in range(1, 10)
    ]
    page = paginate(answers, request, 3)
    return render(request, "question.html", context={"question": item, "answers": page.object_list, "page_obj": page, "show_answers": True})

def hot(request):
    page = paginate(QUESTIONS[::-1], request, 5)
    return render(request, "hot.html", context={"questions": page.object_list, "page_obj": page})

def bytag(request, tag_name):
    page = paginate(QUESTIONS[:11], request, 5)
    return render(request, "bytag.html", context={"questions": page.object_list, "page_obj": page, "tag_name": tag_name})

def login(request):
    return render(request, "login.html")

def signup(request):
    return render(request, "signup.html")

def ask(request):
    return render(request, "ask.html")

def settings(request):
    return render(request, "settings.html")