# 0002_add_status_field.py
from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):
    dependencies = [
        ('todo_app', '0001_initial'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='todo',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed')
                ],
                default='pending',
                
                max_length=20
            ),
        ),
       
       
    ]