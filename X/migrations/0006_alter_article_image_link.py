# Generated by Django 4.2.7 on 2024-08-21 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('X', '0005_delete_scrapedarticle_delete_scrapedcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image_link',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]
