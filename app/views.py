from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import Question, Tag, Profile
from django.db.models import Count

# QUESTIONS = list(Question.objects.get_new())

def get_base_stats():    
    popular_tags = list(Tag.objects.get_popular_tags())
    best_members = list(Profile.objects.get_best_members())
    return (popular_tags, best_members)

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_num = request.GET.get('page', 1)
    try:
        page = paginator.page(page_num)
    except(PageNotAnInteger, EmptyPage):
        page = paginator.page(1)
    return page

def index(request):
    questions = Question.objects.get_new()
    page = paginate(questions, request, 10)
    tags, members = get_base_stats()
    return render(request, "index.html", context={"questions": page.object_list, "page_obj": page, "popular_tags": tags, "best_members": members})

def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answers = question.get_answers()
    page = paginate(answers, request, 8)
    tags, members = get_base_stats()
    return render(request, "question.html", context={"question": question, "answers": page.object_list, "page_obj": page, "show_answers": True, "popular_tags": tags, "best_members": members})

def hot(request):
    questions = Question.objects.get_hot()
    page = paginate(questions, request, 10)
    tags, members = get_base_stats()
    return render(request, "hot.html", context={"questions": page.object_list, "page_obj": page, "popular_tags": tags, "best_members": members})

def bytag(request, tag_name):
    tag = get_object_or_404(Tag, title=tag_name)
    questions = tag.get_questions()  
    page = paginate(questions, request, 10)
    tags, members = get_base_stats()
    return render(request, "bytag.html", context={"questions": page.object_list, "page_obj": page, "tag": tag, "popular_tags": tags, "best_members": members})

def login(request):
    tags, members = get_base_stats()
    return render(request, "login.html", context={"popular_tags": tags, "best_members": members})

def signup(request):
    tags, members = get_base_stats()
    return render(request, "signup.html", context={"popular_tags": tags, "best_members": members})

def ask(request):
    tags, members = get_base_stats()
    return render(request, "ask.html", context={"popular_tags": tags, "best_members": members})

def settings(request):
    tags, members = get_base_stats()
    return render(request, "settings.html", context={"popular_tags": tags, "best_members": members})