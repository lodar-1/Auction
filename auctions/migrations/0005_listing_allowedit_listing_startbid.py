# Generated by Django 4.2.5 on 2023-10-02 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_rename_caegory_name_category_category_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='allowedit',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='startbid',
            field=models.FloatField(default=0),
        ),
    ]