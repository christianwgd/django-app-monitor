# Generated by Django 4.2.3 on 2023-07-10 16:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_rename_processmetric_systemmetric'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='systemmetric',
            options={'ordering': ['timestamp'], 'verbose_name': 'System metric', 'verbose_name_plural': 'System metrics'},
        ),
        migrations.AddField(
            model_name='application',
            name='metric_days',
            field=models.PositiveIntegerField(default=1, help_text='After this time old metrics will be deleted', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Show metrics for number of days'),
        ),
    ]