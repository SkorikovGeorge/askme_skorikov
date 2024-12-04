from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.forms import AnswerForm, LoginForm, SignUpForm, SettingsForm, AskForm
from app.models import Question, Tag, Profile
from django.db.models import Count
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.decorators import login_required

QUESTIONS = list(Question.objects.get_new())


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
    # questions = Question.objects.get_new()
    questions = QUESTIONS
    page = paginate(questions, request, 10)
    tags, members = get_base_stats()
    return render(request, "index.html", context={"questions": page.object_list, "page_obj": page, "popular_tags": tags, "best_members": members})

def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    form = AnswerForm()
    if request.method == "POST":
        form = AnswerForm(request.POST, user=request.user, question=question)
        if form.is_valid():
            answer = form.save()
            answers = question.get_answers()
            page_number = question.get_page_by_answer(answer)
            return redirect(reverse("question", kwargs={"question_id": question.id}) + f"?page={page_number}#{answer.id}")
    answers = question.get_answers()
    page = paginate(answers, request, 8)
    tags, members = get_base_stats()
    return render(request, "question.html", context={"question": question, "answers": page.object_list, "page_obj": page, "form": form, "show_answers": True, "popular_tags": tags, "best_members": members})

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
    form = LoginForm
    redirect_url = request.GET.get("continue", "")
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                if redirect_url:
                    return redirect(redirect_url)
                return redirect(reverse("index"))
            form.add_error("password", error="Invalid username or password.")
    tags, members = get_base_stats()
    return render(request, "login.html", context={"form": form, "popular_tags": tags, "best_members": members})


@login_required
def logout(request):
    redirect_url = request.GET.get("continue", "")
    auth.logout(request)
    if redirect_url:
        return redirect(redirect_url)
    return redirect(reverse("login"))


def signup(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            user = auth.authenticate(request, **form.cleaned_data)
            auth.login(request, user)
            return redirect(reverse("index"))
    tags, members = get_base_stats()
    return render(request, "signup.html", context={"form": form, "popular_tags": tags, "best_members": members})


@login_required
def ask(request):
    form = AskForm()
    if request.method == "POST":
        form = AskForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save()
            return redirect(reverse("question", kwargs={"question_id": question.id}))
    tags, members = get_base_stats()
    return render(request, "ask.html", context={"form": form, "popular_tags": tags, "best_members": members})


@login_required
def settings(request):
    user = request.user
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse("settings"))
    else:
        form = SettingsForm(instance=user)
    tags, members = get_base_stats()
    return render(request, "settings.html", context={"form": form, "popular_tags": tags, "best_members": members})

