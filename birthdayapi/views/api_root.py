"""
API Root View - Provides a simple API overview
"""
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.urls import NoReverseMatch

logger = logging.getLogger(__name__)


@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint that lists available endpoints
    """
    try:
        endpoints = {}
        
        # Helper to safely reverse URLs
        def safe_reverse(name, default=None):
            try:
                return reverse(name, request=request, format=format)
            except NoReverseMatch as e:
                logger.error(f"Failed to reverse URL '{name}': {e}")
                return default or f'[Error: {name} not found]'
            except Exception as e:
                logger.error(f"Unexpected error reversing URL '{name}': {e}")
                return default or f'[Error: {name} not found]'
        
        endpoints['parties'] = safe_reverse('party-list')
        endpoints['photos'] = safe_reverse('partyphoto-list')
        endpoints['rsvps'] = safe_reverse('rsvp-list')
        endpoints['gifts'] = safe_reverse('giftregistryitem-list')
        endpoints['guestbook'] = safe_reverse('guestbookentry-list')
        endpoints['scores'] = safe_reverse('gamescore-list')
        endpoints['badges'] = safe_reverse('badge-list')
        endpoints['trivia'] = safe_reverse('trivia-list')
        endpoints['trivia-questions'] = safe_reverse('triviaquestion-list')
        endpoints['timeline-events'] = safe_reverse('timelineevent-list')
        endpoints['check-admin'] = safe_reverse('check_admin_status')
        
        return Response({
            'message': 'Birthday API',
            'version': '1.0.0',
            'endpoints': endpoints
        })
    except Exception as e:
        logger.error(f"Error in api_root: {e}", exc_info=True)
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
