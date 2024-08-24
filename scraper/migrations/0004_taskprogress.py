# Generated by Django 5.1 on 2024-08-22 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0003_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=255)),
                ('progress', models.IntegerField(default=0)),
                ('total', models.IntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]