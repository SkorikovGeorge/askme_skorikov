from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.db.models import Sum, Count, Value
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
# Create your models here.

class QuestionManager(models.Manager):
    # def get_queryset(self):
    #     #.annotate(answers_count=Count('answers', distinct=True))
    #     return super().get_queryset().annotate(likes=Sum('question_likes__like')).prefetch_related('tags')
        
    def get_new(self):
        return self.annotate(likes=Coalesce(Sum('question_likes__like'), Value(0))).prefetch_related('tags').order_by("-created_at")
    
    def get_hot(self):
        return self.annotate(likes=Coalesce(Sum('question_likes__like'), Value(0))).prefetch_related('tags').order_by('-likes')[:100]
    
class TagManager(models.Manager):
    def get_popular_tags(self):
        three_months = timezone.now() - timezone.timedelta(days=90)
        return self.filter(questions__created_at__gte=three_months).annotate(rating=Count("questions")).order_by("-rating")[:10]

class ProfileManager(models.Manager):
    def get_best_members(self, count=10):
        week = timezone.now() - timezone.timedelta(days=7)
        return self.filter(answers__created_at__gte=week, questions__created_at__gte=week).annotate(
            rating=Count('answers__answer_likes') + Count('questions__question_likes')).order_by('-rating')[:count]
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    objects = ProfileManager()
    
class Tag(models.Model):
    title = models.CharField(max_length=20, unique=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TagManager()
    
    def get_questions(self):
        return self.questions.annotate(likes=Sum('question_likes__like')).prefetch_related('tags').order_by("-created_at")
    
    
class Question(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=100, null=False, blank=False)
    content = models.TextField( null=False, blank=False)
    tags = models.ManyToManyField(Tag, related_name="questions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    objects = QuestionManager()
    
    def get_answers(self):
        return self.answers.annotate(likes=Coalesce(Sum('answer_likes__like'), Value(0))).order_by("-likes", "created_at")
    
    def count_answers(self):
        return self.answers.count()
    
    def sum_likes(self):
        res = self.question_likes.aggregate(likes = Sum('like'))["likes"]
        return res if res else 0
    
    def get_page_by_answer(self, answer):
        answers = self.get_answers()
        for i in range(len(answers)):
            if answers[i].id == answer.id:
                return i // 8 + 1
        return 1
    
    def get_like_by_profile(self, profile):
        question_likes = self.question_likes
        try:
            obj = question_likes.get(profile=profile)
        except QuestionLike.DoesNotExist:
            obj = None
        return obj

    def get_absolute_url(self):
       return reverse('question', kwargs={'question_id': self.pk})  
            
    
class Answer(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    content = models.TextField(null=False, blank=False)
    correct = models.BooleanField(null=True, blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def sum_likes(self):
        res = self.answer_likes.aggregate(likes = Sum('like'))["likes"]
        return res if res else 0
    
    def get_like_by_profile(self, profile):
        answer_likes = self.answer_likes
        try:
            obj = answer_likes.get(profile=profile)
        except AnswerLike.DoesNotExist:
            obj = None
        return obj
        

class QuestionLike(models.Model):
    like_choices = [
        (1, "Like"),
        (-1, "Dislike"),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="question_likes")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_likes")
    like = models.IntegerField(choices=like_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ("profile", "question")

class AnswerLike(models.Model):
    like_choices = [
        (1, "Like"),
        (-1, "Dislike"),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="answer_likes")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="answer_likes")
    like = models.IntegerField(choices=like_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    class Meta:
        unique_together = ("profile", "answer") 
    