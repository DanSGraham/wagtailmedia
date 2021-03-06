from __future__ import unicode_literals

import os.path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import Signal
from django.dispatch.dispatcher import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

try:
    from django.urls import reverse
except ImportError:  # fallback for older versions of Django
    from django.core.urlresolvers import reverse

try:
    from wagtail.admin.utils import get_object_usage
    from wagtail.core.models import CollectionMember
    from wagtail.search import index
    from wagtail.search.queryset import SearchableQuerySetMixin
except ImportError:  # fallback for wagtail <2.0
    from wagtail.wagtailadmin.utils import get_object_usage
    from wagtail.wagtailcore.models import CollectionMember
    from wagtail.wagtailsearch import index
    from wagtail.wagtailsearch.queryset import SearchableQuerySetMixin


class MediaQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


@python_2_unicode_compatible
class AbstractMedia(CollectionMember, index.Indexed, models.Model):
    MEDIA_TYPES = (
        ('audio', _('Audio file')),
        ('video', _('Video file')),
    )

    title = models.CharField(max_length=255, verbose_name=_('title'))
    file = models.FileField(upload_to='media', verbose_name=_('file'))

    type = models.CharField(choices=MEDIA_TYPES, max_length=255, blank=False, null=False)
    #To get duration of audio, use MutaGen module rather than ask user to input.
    duration = models.PositiveIntegerField(verbose_name=_('duration'), help_text=_('Duration in seconds'))
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('width'))
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('height'))
    thumbnail = models.FileField(upload_to='media_thumbnails', blank=True, verbose_name=_('thumbnail'))

    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('uploaded by user'),
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL
    )

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_('tags'))

    objects = MediaQuerySet.as_manager()

    search_fields = CollectionMember.search_fields + [
        index.SearchField('title', partial_match=True, boost=10),
        index.RelatedFields('tags', [
            index.SearchField('name', partial_match=True, boost=10),
        ]),
        index.FilterField('uploaded_by_user'),
    ]

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def thumbnail_filename(self):
        return os.path.basename(self.thumbnail.name)

    @property
    def file_extension(self):
        return os.path.splitext(self.filename)[1][1:]

    @property
    def url(self):
        return self.file.url

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse('wagtailmedia:media_usage',
                       args=(self.id,))

    def is_editable_by_user(self, user):
        from wagtailmedia.permissions import permission_policy
        return permission_policy.user_has_permission_for_instance(user, 'change', self)

    class Meta:
        abstract = True
        verbose_name = _('media')


class Media(AbstractMedia):
    admin_form_fields = (
        'title',
        'file',
        'collection',
        'duration',
        'width',
        'height',
        'thumbnail',
        'tags',
    )

def get_media_model_string():
    """
    Get the dotted ``app.Model`` name for the image model as a string.
    Useful for developers making Wagtail plugins that need to refer to the
    image model, such as in foreign keys, but the model itself is not required.
    """
    return getattr(settings, 'WAGTAILMEDIA_MEDIA_MODEL', 'wagtailmedia.Media')



def get_media_model():
    from django.apps import apps

    model_string = get_media_model_string()
    try:
        return apps.get_model(model_string)
    except ValueError:
        raise ImproperlyConfigured("WAGTAILMEDIA_MEDIA_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAILMEDIA_MEDIA_MODEL refers to model '%s' that has not been installed" %
            model_string
        )

# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=Media)
def media_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
    instance.thumbnail.delete(False)


media_served = Signal(providing_args=['request'])
