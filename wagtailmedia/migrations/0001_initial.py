# Generated by Django 2.1.4 on 2018-12-24 18:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import wagtail.core.models
import wagtail.search.index


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('file', models.FileField(upload_to='media', verbose_name='file')),
                ('type', models.CharField(choices=[('audio', 'Audio file'), ('video', 'Video file')], max_length=255)),
                ('duration', models.PositiveIntegerField(help_text='Duration in seconds', verbose_name='duration')),
                ('width', models.PositiveIntegerField(blank=True, null=True, verbose_name='width')),
                ('height', models.PositiveIntegerField(blank=True, null=True, verbose_name='height')),
                ('thumbnail', models.FileField(blank=True, upload_to='media_thumbnails', verbose_name='thumbnail')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('collection', models.ForeignKey(default=wagtail.core.models.get_root_collection_id, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Collection', verbose_name='collection')),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text=None, through='taggit.TaggedItem', to='taggit.Tag', verbose_name='tags')),
                ('uploaded_by_user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='uploaded by user')),
            ],
            options={
                'verbose_name': 'media',
                'abstract': False,
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
    ]
