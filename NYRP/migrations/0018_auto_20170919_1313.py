# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-19 17:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NYRP', '0017_auto_20170919_1303'),
    ]

    operations = [
        migrations.RenameField(
            model_name='selector',
            old_name='indexes',
            new_name='pri_keys',
        ),
    ]
