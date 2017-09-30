# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 00:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dhint3', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Hint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hint1', models.CharField(default='', max_length=200)),
                ('hint2', models.CharField(default='', max_length=200)),
                ('hint3', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('A', models.BooleanField(default=False)),
                ('B', models.BooleanField(default=False)),
                ('C', models.BooleanField(default=False)),
                ('D', models.BooleanField(default=False)),
                ('E', models.BooleanField(default=False)),
                ('subject', models.CharField(choices=[('CHEM', 'Chemistry'), ('USHG', 'U.S. History & Government'), ('ALG1', 'Algebra I'), ('ALG2', 'Algebra II (Common Core)'), ('GHGE', 'Global History & Geography'), ('PHYS', 'Physics'), ('ERRO', 'Error: no subject')], default='ERRO', max_length=4)),
                ('question', models.CharField(max_length=200)),
                ('bug_rep', models.CharField(max_length=200)),
                ('month', models.CharField(max_length=200)),
                ('year', models.IntegerField()),
                ('unit', models.IntegerField()),
                ('diagram', models.FileField(default=None, upload_to='')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NYRP.Group')),
                ('hint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NYRP.Hint')),
            ],
        ),
    ]
