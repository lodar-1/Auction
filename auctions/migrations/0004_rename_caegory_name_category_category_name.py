# Generated by Django 4.2.5 on 2023-09-28 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_category_remove_listing_bid_amount_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='caegory_name',
            new_name='category_name',
        ),
    ]
