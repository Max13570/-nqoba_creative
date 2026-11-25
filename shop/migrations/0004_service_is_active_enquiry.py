from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_alter_order_options_alter_service_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Untick to hide this service from the website without deleting it.',
            ),
        ),
        migrations.CreateModel(
            name='Enquiry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=30)),
                ('service', models.CharField(max_length=100)),
                ('budget', models.CharField(blank=True, default='', max_length=50)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                'verbose_name': 'Project Enquiry',
                'verbose_name_plural': 'Project Enquiries',
                'ordering': ['-created_at'],
            },
        ),
    ]
