from django.core.management.base import BaseCommand
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Удаление данных из указанных моделей'

    def add_arguments(self, parser):
        parser.add_argument(
            "models",
            nargs='*',
            type=str,
            default=["Profile", "Tag", "Question", "Answer", "QuestionLike", "AnswerLike", "User"],
        )

    def handle(self, *args, **kwargs):
        models = kwargs["models"]

        default_models = {
            "Profile": Profile,
            "Tag": Tag,
            "Question": Question,
            "Answer": Answer,
            "QuestionLike": QuestionLike,
            "AnswerLike": AnswerLike,
            "User": User
        }

        try:
            models = [default_models[model_name] for model_name in models]
        except(KeyError):
            self.stdout.write(self.style.ERROR("Нет модели/моделей с таким названием!"))
            return

        for model in models:
            model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Данные из модели {model.__name__} удалены"))

        self.stdout.write(self.style.SUCCESS("Удаление данных завершено"))