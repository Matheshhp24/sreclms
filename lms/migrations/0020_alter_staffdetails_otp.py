# Generated by Django 5.0.6 on 2024-06-20 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0019_staffdetails_otp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffdetails',
            name='otp',
            field=models.IntegerField(default=0),
        ),
    ]
