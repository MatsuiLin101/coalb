# Generated by Django 2.2.11 on 2021-06-29 02:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coa', '0003_livestockfeedamount'),
    ]

    operations = [
        migrations.CreateModel(
            name='LivestockSlaughter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_class', models.CharField(max_length=50, verbose_name='主分類')),
                ('sub_class', models.CharField(max_length=50, verbose_name='次分類')),
                ('level', models.PositiveIntegerField(verbose_name='級別')),
                ('name', models.CharField(max_length=20, verbose_name='名稱')),
                ('value', models.CharField(max_length=20, verbose_name='值')),
                ('search_name', models.CharField(max_length=20, verbose_name='搜尋名稱')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coa.LivestockSlaughter', verbose_name='上層物件')),
            ],
            options={
                'verbose_name': '畜禽供應屠宰頭數',
                'verbose_name_plural': '畜禽供應屠宰頭數',
            },
        ),
    ]
