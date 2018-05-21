# Generated by Django 2.0 on 2018-05-18 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ej_conversations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_promoted',
            field=models.BooleanField(default=False, help_text='Promoted comments are prioritized when selecting random commentsto users.', verbose_name='Promoted comment?'),
        ),
    ]
