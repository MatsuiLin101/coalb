# Generated by Django 2.2.11 on 2021-06-24 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0004_linecallbacklog'),
    ]

    operations = [
        migrations.CreateModel(
            name='TracebackLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app', models.CharField(max_length=255, verbose_name='關聯app')),
                ('message', models.TextField(verbose_name='錯誤訊息')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
            ],
            options={
                'verbose_name': '例外報錯記錄',
                'verbose_name_plural': '例外報錯記錄',
            },
        ),
    ]