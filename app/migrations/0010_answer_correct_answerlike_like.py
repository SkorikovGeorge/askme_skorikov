# Generated by Django 4.2.16 on 2024-12-12 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_profile_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='correct',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='answerlike',
            name='like',
            field=models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], default=1),
            preserve_default=False,
        ),
    ]
