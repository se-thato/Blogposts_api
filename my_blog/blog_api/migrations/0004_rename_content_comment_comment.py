# Generated by Django 5.1.2 on 2024-11-21 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog_api", "0003_comment"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="content",
            new_name="comment",
        ),
    ]
