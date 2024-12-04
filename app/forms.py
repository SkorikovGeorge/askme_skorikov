from django import forms
from django.core.files.storage import default_storage
from app.models import Answer, Profile, Question, Tag, User
import re

class LoginForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=35) 
    password = forms.CharField(widget=forms.PasswordInput, min_length=4, max_length=35)
    
    def clean_username(self):
        return self.cleaned_data.get("username").strip()
    

class SignUpForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=4, max_length=35)
    repeat_password = forms.CharField(widget=forms.PasswordInput, min_length=4, max_length=35)
    avatar = forms.ImageField(required=False)
    
    def clean(self):
        data = super().clean()
        if data["password"] != data["repeat_password"]:
            raise forms.ValidationError("Passwords do not match.")
        return data
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.save()
        profile = Profile(user=user, avatar=self.cleaned_data.get('avatar'))
        profile.save()
        return user
        
    class Meta:
        model = User
        fields = ("username", "email", "password")
        
        
class SettingsForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        if self.instance.email != email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    
    def save(self):
        user = super().save(commit=False)
        profile = user.profile
        
        new_avatar = self.cleaned_data["avatar"]
        if profile.avatar:
            current_path = profile.avatar.path
            if default_storage.exists(current_path):
                default_storage.delete(current_path)
        profile.avatar = new_avatar if new_avatar else None
        user.save()
        profile.save()
        return user
            
    
    class Meta:
        model = User
        fields = ("username", "email")
        
        
class AskForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, max_length=2000)
    tags = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_tags(self):
        tags = self.cleaned_data["tags"]
        tags = re.split(r'[,\s]+', tags)
        tags = [tag.strip() for tag in tags if tag.strip()]
        if len(tags) < 2:
            raise forms.ValidationError("Field must contain at least 2 words, separated by space or comma.")
        return tags
            
    def save(self):
        question = super().save(commit=False)
        question.profile = self.user.profile
        question.save()
        for tag in self.cleaned_data["tags"]:
            new_tag, created = Tag.objects.get_or_create(title=tag)
            question.tags.add(new_tag)
        return question
        
        
    class Meta:
        model = Question
        fields = ("title", "content")
    
    
class AnswerForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, max_length=2000)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        
    # def clean(self):
    #     data = super().clean()
    #     data["content"] = data["content"].strip()
    #     if not data["content"]:
    #         raise forms.ValidationError("Answer text required.")
    #     return data    
    
            
    def save(self, question=None):
        answer = super().save(commit=False)
        answer.profile = self.user.profile
        answer.question = self.question
        answer.save()
        return answer
        
    class Meta:
        model = Answer
        fields = ("content", )