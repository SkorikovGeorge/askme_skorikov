import json
from django.forms import model_to_dict
import jwt
import time
from cent import Client, PublishRequest
from django.conf import settings as settingsdj
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.forms import AnswerForm, LoginForm, SignUpForm, SettingsForm, AskForm
from app.models import Question, Tag, Profile, QuestionLike, Answer, AnswerLike
from django.db.models import Count
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.contrib.postgres.search import SearchVector, SearchQuery

# QUESTIONS = list(Question.objects.get_new())
# TAGS = list(Tag.objects.get_popular_tags())
# MEMBERS = list(Profile.objects.get_best_members())


def get_base_stats():  
    popular_tags = cache.get("popular_tags")
    best_members = cache.get("best_members")
    return (popular_tags, best_members)
    # return (TAGS, MEMBERS)

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
    # questions = QUESTIONS
    page = paginate(questions, request, 10)
    tags, members = get_base_stats()
    return render(request, "index.html", context={"questions": page.object_list, "page_obj": page, "popular_tags": tags, "best_members": members})

def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    form = AnswerForm()
    ws_channel_name = f"channel_{question_id}"
    if request.method == "POST":
        form = AnswerForm(request.POST, user=request.user, question=question)
        if form.is_valid():
            answer = form.save()
            

            api_url = settingsdj.CENTRIFUGO_API_URL
            api_key = settingsdj.CENTRIFUGO_API_KEY

            client = Client(api_url, api_key)
            avatar_url = answer.profile.avatar.url if answer.profile.avatar else "None"
            data = {**model_to_dict(answer), "avatar_url": avatar_url}
            request = PublishRequest(channel=ws_channel_name, data=data)
            client.publish(request)
                        
            answers = question.get_answers()
            page_number = question.get_page_by_answer(answer)
            return redirect(reverse("question", kwargs={"question_id": question.id}) + f"?page={page_number}#{answer.id}")
    answers = question.get_answers()
    page = paginate(answers, request, 8)
    tags, members = get_base_stats()
    return render(request, "question.html", context={"question": question, "answers": page.object_list, "page_obj": page, "form": form, "show_answers": True, "ws_channel_name": ws_channel_name, "popular_tags": tags, "best_members": members, **get_centrifugo_data(request.user)})

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


@require_POST
@login_required
def question_like(request, question_id):
    try:
        body = json.loads(request.body)
        type = body.get("type")
        
        profile = request.user.profile
        question = Question.objects.get(pk=question_id)
        cur = question.get_like_by_profile(profile=profile)
        if not cur:
            QuestionLike.objects.create(profile=profile, question=question, like=type)
        elif cur.like == type:
            info = cur.delete()
        else:
            info = cur.delete()
            QuestionLike.objects.create(profile=profile, question=question, like=type)
        return JsonResponse({ 
            'likes_count': question.sum_likes(),
            'code': 200,
        })
    except:
        return JsonResponse({ 
            'likes_count': question.sum_likes(),
            'code': 400,
        })
        

@require_POST
@login_required
def answer_like(request, answer_id):
    try:
        body = json.loads(request.body)
        type = body.get("type")
        
        profile = request.user.profile
        answer = Answer.objects.get(pk=answer_id)
        cur = answer.get_like_by_profile(profile=profile)
        if not cur:
            AnswerLike.objects.create(profile=profile, answer=answer, like=type)
        elif cur.like == type:
            info = cur.delete()
        else:
            info = cur.delete()
            AnswerLike.objects.create(profile=profile, answer=answer, like=type)
        return JsonResponse({ 
            'likes_count': answer.sum_likes(),
            'code': 200,
        })
    except:
        return JsonResponse({ 
            'likes_count': answer.sum_likes(),
            'code': 400,
        })
        

@require_POST
@login_required
def correct_answer(request, answer_id):
    profile = request.user.profile
    answer = Answer.objects.get(pk=answer_id)
    if answer.question.profile == profile:
        answer.correct = not(answer.correct)
        answer.save()
    return JsonResponse({ 
        'is_correct': answer.correct,
    })
    
    
def get_centrifugo_data(user_id):
    ws_url = settingsdj.CENTRIFUGO_WS_URL
    secret = settingsdj.CENTRIFUGO_SECRET
    token = jwt.encode({"sub": str(user_id), "exp": int(time.time()) + 10 * 60}, secret, algorithm="HS256")
    
    return {"centrifugo": {"token": token, "url": ws_url}}


def search_questions(request):
    search = request.GET.get('q', '')
    if not search or len(search) < 3:
        return JsonResponse({'results': []})

    queryset = Question.objects.annotate(
        search_vector=SearchVector('title', 'content')
    ).filter(search_vector=SearchQuery(search))[:10] 
    
    results = [{'title': q.title, 'url': q.get_absolute_url()} for q in queryset]
    return JsonResponse({'results': results})