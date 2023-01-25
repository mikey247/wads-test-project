from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls

from .api import api_router

urlpatterns = [
    re_path(r'^django-admin/', admin.site.urls),
    re_path(r'^admin/autocomplete/', include(autocomplete_admin_urls)),
    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'^api/v2/', api_router.urls),

    re_path(r'^login/$', auth_views.LoginView.as_view(template_name = 'sitecore/registration/login.html'), name='login'),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(template_name = 'sitecore/registration/logout.html'), name='logout'),

    re_path(r'^documents/', include(wagtaildocs_urls)),

    re_path(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if settings.ENABLE_DEBUG_TOOLBAR:
        import debug_toolbar
        urlpatterns = [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
