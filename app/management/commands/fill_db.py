from django.core.management.base import BaseCommand, CommandError
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from faker import Faker
from faker.exceptions import UniquenessException
import random


class Command(BaseCommand):
    help = "Сommand to fill the database with the specified ratio"
    fake = Faker()

    def add_arguments(self, parser):
        parser.add_argument("ratio", nargs="?",  type=int, default=10_000)

    def handle(self, *args, **options):
        ratio = options["ratio"]
        self.stdout.write(f"Запуск генерации ratio = {ratio}")
        # self.generate_profiles(ratio)
        # self.generate_tags(ratio)
        # self.generate_questions(ratio)
        # self.generate_answers(ratio)
        # self.generate_questions_likes(ratio)
        # self.generate_answers_likes(ratio)
        self.stdout.write(self.style.SUCCESS("База успешно заполнена!"))
        
    def generate_profiles(self, ratio):
        self.stdout.write("Генерация профилей пользователей...")
        users = []
        for i in range(ratio):
            try:
                username = self.fake.unique.user_name()
            except UniquenessException:
                username = self.fake.user_name() + str(i)
            try:
                email = self.fake.unique.email()
            except UniquenessException:
                email = f"{username}{i}@{self.fake.free_email_domain()}"
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password'
            )
            users.append(user)
        profiles = [Profile(user=users[i]) for i in range(ratio)]
        Profile.objects.bulk_create(profiles)
        
    def generate_tags(self, ratio):
        self.stdout.write("Генерация тегов...")
        tags = []
        for i in range(ratio):
            try:
                title = self.fake.unique.word()
            except UniquenessException:
                title = self.fake.word() + str(i)
            tags.append(Tag(title=title))
        Tag.objects.bulk_create(tags)
        
    def generate_questions(self, ratio):
        self.stdout.write("Генерация вопросов...")
        all_profiles = Profile.objects.values_list("id", flat=True)
        all_tags = list(Tag.objects.values_list("id", flat=True))
        self.stdout.write("Сбор данных завершен")  
        questions = []
        for i in range(ratio * 10):
            questions.append(Question(
                profile_id=random.choice(all_profiles),
                title=self.fake.sentence(nb_words=5)[:-1],
                content=self.fake.paragraph(nb_sentences=5)
            ))
        Question.objects.bulk_create(questions)
            
        for question in Question.objects.all():
            tags = random.sample(all_tags, random.randint(2, 4))
            question.tags.add(*tags)
            
    def generate_answers(self, ratio):
        self.stdout.write("Генерация ответов...")
        all_profiles = Profile.objects.values_list("id", flat=True)
        all_questions = Question.objects.values_list("id", flat=True)
        self.stdout.write("Сбор данных завершен")  
        answers = []
        for i in range(ratio * 100):
            answers.append(Answer(
                profile_id=random.choice(all_profiles),
                question_id=random.choice(all_questions),
                content=self.fake.paragraph(nb_sentences=4)
            ))
        Answer.objects.bulk_create(answers)
    
    def generate_questions_likes(self, ratio):
        self.stdout.write("Генерация лайков вопросов...")      
        all_profiles = list(Profile.objects.values_list("id", flat=True))
        all_questions = list(Question.objects.values_list("id", flat=True))
        self.stdout.write("Сбор данных завершен")  
        likes = []
        for profile in all_profiles:
            unique_questions = random.sample(all_questions, 200)
            for question in unique_questions:
                like = random.choice([1, -1])
                likes.append(QuestionLike(profile_id=profile, question_id=question, like=like))
        QuestionLike.objects.bulk_create(likes)
                
    def generate_answers_likes(self, ratio):
        self.stdout.write("Генерация лайков ответов...")
        all_profiles = Profile.objects.values_list("id", flat=True)
        all_answers = list(Answer.objects.values_list("id", flat=True))
        self.stdout.write("Сбор данных завершен")
        likes = []
        for profile in all_profiles:
            unique_answers = random.sample(all_answers, 200)
            for answer in unique_answers:
                likes.append(AnswerLike(profile_id=profile, answer_id=answer))
        AnswerLike.objects.bulk_create(likes)
                
        
        