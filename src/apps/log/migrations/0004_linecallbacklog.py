# Generated by Django 2.2.11 on 2020-12-22 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0003_linefollowlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineCallBackLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature', models.CharField(max_length=255, verbose_name='簽名')),
                ('body', models.TextField(verbose_name='內容')),
                ('message', models.TextField(verbose_name='錯誤訊息')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
            ],
            options={
                'verbose_name': 'LINE掛勾錯誤記錄',
                'verbose_name_plural': 'LINE掛勾錯誤記錄',
            },
        ),
    ]
