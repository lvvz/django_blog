# Generated by Django 3.2.1 on 2021-05-05 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20210504_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='upvote',
            field=models.BooleanField(null=True),
        ),
    ]
