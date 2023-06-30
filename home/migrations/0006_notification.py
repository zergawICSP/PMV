# Generated by Django 4.1.4 on 2023-01-14 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_rename_comany_name_client_company_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading1', models.CharField(max_length=300)),
                ('heading2', models.CharField(blank=True, max_length=300, null=True)),
                ('message', models.TextField()),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.client')),
            ],
        ),
    ]
