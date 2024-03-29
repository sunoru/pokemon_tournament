# Generated by Django 4.2.2 on 2023-06-12 20:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_name', models.CharField(max_length=50, unique=True, verbose_name='key')),
                ('option_value', models.TextField(default='', verbose_name='value')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlayerUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100, verbose_name='name')),
                ('player_id', models.CharField(default='test', max_length=100, unique=True, verbose_name='Play Pokemon ID')),
                ('birthday', models.DateField(auto_now_add=True, verbose_name='birthday')),
                ('information', models.TextField(default='{}', null=True, verbose_name='information')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
