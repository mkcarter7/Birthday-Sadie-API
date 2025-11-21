"""
API Root View - Provides a simple API overview
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.urls import NoReverseMatch


@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint that lists available endpoints
    """
    endpoints = {}
    
    # Helper to safely reverse URLs
    def safe_reverse(name, default=None):
        try:
            return reverse(name, request=request, format=format)
        except NoReverseMatch:
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
