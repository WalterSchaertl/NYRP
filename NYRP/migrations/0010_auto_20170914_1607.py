# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-14 20:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NYRP', '0009_auto_20170831_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='E',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
