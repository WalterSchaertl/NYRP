# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-28 00:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NYRP', '0004_auto_20170626_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='A',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='B',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='C',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='D',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='E',
            field=models.CharField(max_length=200),
        ),
    ]
