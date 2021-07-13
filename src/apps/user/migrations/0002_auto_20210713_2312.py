# Generated by Django 2.2.24 on 2021-07-13 15:12

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='databasecontrol',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 13, 15, 22, 56, 303898, tzinfo=utc), verbose_name='過期時間'),
        ),
        migrations.CreateModel(
            name='AnyToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='名稱')),
                ('token', models.CharField(max_length=20, verbose_name='通行證')),
                ('status', models.BooleanField(default=False, verbose_name='狀態')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('expire_time', models.DateTimeField(default=datetime.datetime(2021, 7, 13, 15, 22, 56, 304493, tzinfo=utc), verbose_name='過期時間')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='使用者')),
            ],
            options={
                'verbose_name': '萬用通行證',
                'verbose_name_plural': '萬用通行證',
            },
        ),
    ]
