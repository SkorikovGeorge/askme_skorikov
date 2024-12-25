from django.core.management.base import BaseCommand
from app.models import Tag, Profile
from django.core.cache import cache

class Command(BaseCommand):
    def handle(self, *args, **options):
        popular_tags = list(Tag.objects.get_popular_tags())
        cache.set("popular_tags", popular_tags, 60)
        
        best_members = list(Profile.objects.get_best_members())
        cache.set("best_members", best_members, 60)