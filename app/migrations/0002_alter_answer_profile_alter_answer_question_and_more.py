# Generated by Django 5.1.2 on 2024-11-12 07:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='app.profile'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='app.question'),
        ),
        migrations.AlterField(
            model_name='answerlike',
            name='answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='app.answer'),
        ),
        migrations.AlterField(
            model_name='answerlike',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_likes', to='app.profile'),
        ),
        migrations.AlterField(
            model_name='question',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='app.profile'),
        ),
        migrations.AlterField(
            model_name='questionlike',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_likes', to='app.profile'),
        ),
        migrations.AlterField(
            model_name='questionlike',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='app.question'),
        ),
    ]
