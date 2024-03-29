# Generated by Django 4.2.5 on 2023-09-27 19:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caegory_name', models.CharField(max_length=64)),
                ('category_description', models.CharField(max_length=500)),
            ],
        ),
        migrations.RemoveField(
            model_name='listing',
            name='bid_amount',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='bid_datetime',
        ),
        migrations.AddField(
            model_name='listing',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='listing',
            name='description',
            field=models.CharField(default=None, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='image_link',
            field=models.CharField(default=None, max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='listing_date',
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='title',
            field=models.CharField(default=None, max_length=64),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listing_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auctions.listing')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserWatchlist', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ListingBid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid_amount', models.IntegerField()),
                ('bid_datetime', models.DateTimeField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserBid', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='listing',
            name='category_id',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='ListingCategory', to='auctions.category'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='watchlist',
            constraint=models.UniqueConstraint(models.F('user_id'), models.F('listing_id'), name='WatchlistComposite'),
        ),
    ]
