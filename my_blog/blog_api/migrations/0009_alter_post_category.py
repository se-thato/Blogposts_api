# Generated by Django 5.1.2 on 2024-12-14 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_api', '0008_remove_comment_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(default='Tech', max_length=50),
        ),
    ]