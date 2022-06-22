# Generated by Django 2.2.19 on 2022-05-16 19:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220514_2103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='group',
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.Group', verbose_name='Сообщество'),
        ),
    ]