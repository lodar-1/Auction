# Generated by Django 4.2.5 on 2023-10-12 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_comment_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listingbid',
            name='bid_amount',
            field=models.FloatField(),
        ),
    ]