# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-14 21:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NYRP', '0013_auto_20170914_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
