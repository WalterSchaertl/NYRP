# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-14 21:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NYRP', '0014_auto_20170914_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='diagram',
            field=models.FileField(blank=True, default=None, null=True, upload_to='diagrams'),
        ),
    ]
