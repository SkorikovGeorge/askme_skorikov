# Generated by Django 5.1.2 on 2024-11-13 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_question_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(related_name='questions', to='app.tag'),
        ),
    ]