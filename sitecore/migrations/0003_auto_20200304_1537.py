# Generated by Django 2.2.9 on 2020-03-04 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitecore', '0002_sitesettings_ga_tracking_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='ga_tracking_id',
            field=models.CharField(blank=True, help_text='Google Analytics Tracking ID (UA-#########-#)', max_length=32),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='twitter',
            field=models.CharField(blank=True, help_text='Twitter Account', max_length=128),
        ),
    ]
