"""
API Root View - Provides a simple API overview
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint that lists available endpoints
    """
    return Response({
        'message': 'Birthday API',
        'version': '1.0.0',
        'endpoints': {
            'parties': reverse('party-list', request=request, format=format),
            'photos': reverse('partyphoto-list', request=request, format=format),
            'rsvps': reverse('rsvp-list', request=request, format=format),
            'gifts': reverse('giftregistryitem-list', request=request, format=format),
            'guestbook': reverse('guestbookentry-list', request=request, format=format),
            'scores': reverse('gamescore-list', request=request, format=format),
            'badges': reverse('badge-list', request=request, format=format),
            'trivia': reverse('trivia-list', request=request, format=format),
            'trivia-questions': reverse('triviaquestion-list', request=request, format=format),
            'timeline-events': reverse('timelineevent-list', request=request, format=format),
            'check-admin': reverse('check_admin_status', request=request, format=format),
        }
    })
