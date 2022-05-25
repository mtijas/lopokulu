# Generated by Django 4.0 on 2022-05-23 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_alter_person_is_superuser'),
        ('equipment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('READONLY', 'Read only'), ('USER', 'User'), ('ADMIN', 'Administrator')], default='READONLY', max_length=32)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='equipment.equipment')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.person')),
            ],
        ),
    ]
