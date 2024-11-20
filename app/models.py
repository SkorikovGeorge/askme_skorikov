from django.db import models
from django.urls import reverse
from django.db.models import Sum, Count
from django.contrib.auth.models import User

# Create your models here.

class QuestionManager(models.Manager):
    # def get_queryset(self):
    #     #.annotate(answers_count=Count('answers', distinct=True))
    #     return super().get_queryset().annotate(likes=Sum('question_likes__like')).prefetch_related('tags')
        
    def get_new(self):
        return self.annotate(likes=Sum('question_likes__like')).prefetch_related('tags').order_by("-created_at")
    
    def get_hot(self):
        return self.annotate(likes=Sum('question_likes__like')).prefetch_related('tags').order_by('-likes')[:100]
    
class TagManager(models.Manager):
    def get_popular_tags(self):
        return self.annotate(rating=Count("questions")).order_by("rating")[:10]
    
class ProfileManager(models.Manager):
    def get_best_members(self, count=10):
        return self.annotate(answer_likes_count=Count('answers__answer_likes')).order_by('-answer_likes_count')[:count]
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True)
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
        return self.answers.annotate(likes=Count("answer_likes__id")).order_by("-likes")
    
    def count_answers(self):
        return self.answers.count()
    
    def sum_likes(self):
        return self.question_likes.aggregate(likes = Sum('like'))["likes"]
    
class Answer(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    content = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

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
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="answer_likes")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="answer_likes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    class Meta:
        unique_together = ("profile", "answer") 
    