# Generated by Django 2.2.24 on 2021-07-20 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0005_tracebacklog'),
    ]

    operations = [
        migrations.AddField(
            model_name='linemessagelog',
            name='method',
            field=models.CharField(default='reply', max_length=10, verbose_name='回應方式'),
        ),
        migrations.AddField(
            model_name='linemessagelog',
            name='timestamp',
            field=models.FloatField(blank=True, null=True, verbose_name='請求時間戳'),
        ),
    ]
