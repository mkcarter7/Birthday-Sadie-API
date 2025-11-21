"""
Birthday API URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from birthdayapi.views.party import PartyViewSet
from birthdayapi.views.photo import PartyPhotoViewSet
from birthdayapi.views.rsvp import RSVPViewSet
from birthdayapi.views.gift_registry import GiftRegistryItemViewSet
from birthdayapi.views.guest_book import GuestBookEntryViewSet
from birthdayapi.views.game_score import GameScoreViewSet
from birthdayapi.views.badges import BadgeViewSet
from birthdayapi.views.trivia import TriviaViewSet
from birthdayapi.views.trivia_question import TriviaQuestionViewSet
from birthdayapi.views.admin import check_admin_status
from birthdayapi.views.timeline import PartyTimelineEventViewSet
from birthdayapi.views.api_root import api_root

router = DefaultRouter()
router.register(r'api/parties', PartyViewSet, basename='party')
router.register(r'api/photos', PartyPhotoViewSet, basename='partyphoto')
router.register(r'api/rsvps', RSVPViewSet, basename='rsvp')
router.register(r'api/gifts', GiftRegistryItemViewSet, basename='giftregistryitem')
router.register(r'api/guestbook', GuestBookEntryViewSet, basename='guestbookentry')
router.register(r'api/scores', GameScoreViewSet, basename='gamescore')
router.register(r'api/badges', BadgeViewSet, basename='badge')
router.register(r'api/trivia', TriviaViewSet, basename='trivia')
router.register(r'api/trivia-questions', TriviaQuestionViewSet, basename='triviaquestion')
router.register(r'api/timeline-events', PartyTimelineEventViewSet, basename='timelineevent')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API root
    path('api/', api_root, name='api-root'),
    
    path('api/auth/', include('rest_framework.urls')),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/check-admin/', check_admin_status, name='check_admin_status'),
    
    path('', include(router.urls)),
]

# Serve media files in both development and production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # In production, serve media files through Django
    # Note: Render's filesystem is ephemeral - files will be lost on redeploy
    # For production with many/large files, consider using S3 or similar
    from django.views.static import serve
    from django.urls import re_path
    from django.views.decorators.cache import never_cache
    from django.http import Http404
    
    def serve_media(request, path):
        """Serve media files in production"""
        try:
            return serve(request, path, document_root=settings.MEDIA_ROOT, show_indexes=False)
        except Http404:
            # Log 404s for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Media file not found: {path}")
            raise
    
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', never_cache(serve_media)),
    ]
