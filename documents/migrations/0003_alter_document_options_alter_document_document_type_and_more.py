# Generated by Django 4.2 on 2024-12-03 13:14

from django.db import migrations, models
import documents.models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='document',
            name='mfo',
            field=models.CharField(max_length=9),
        ),
        migrations.AlterField(
            model_name='document',
            name='pdf_file',
            field=models.FileField(upload_to='documents/', validators=[documents.models.validate_file_size]),
        ),
    ]
