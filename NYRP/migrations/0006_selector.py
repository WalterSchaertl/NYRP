# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-31 23:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NYRP', '0005_auto_20170627_2045'),
    ]

    operations = [
        migrations.CreateModel(
            name='Selector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
