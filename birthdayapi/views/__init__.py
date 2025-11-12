"""
Birthday API Views Package

This package contains all the ViewSets for the Birthday API application.
Each ViewSet handles CRUD operations and custom actions for their respective models.
"""

# Import all ViewSets for easy access
from .party import PartyViewSet
from .photo import PartyPhotoViewSet
from .rsvp import RSVPViewSet
from .gift_registry import GiftRegistryItemViewSet
from .guest_book import GuestBookEntryViewSet
from .game_score import GameScoreViewSet
from .badges import BadgeViewSet, UserBadgeViewSet
from .timeline import PartyTimelineEventViewSet, PartyTimelineEventSerializer
from .trivia_question import TriviaQuestionViewSet

# Import serializers if needed elsewhere
from .game_score import GameScoreSerializer
from .guest_book import GuestBookEntrySerializer
from .badges import BadgeSerializer, UserBadgeSerializer
from .trivia_question import TriviaQuestionSerializer

# Version info
__version__ = '1.0.0'
__author__ = 'Birthday API Team'

# All ViewSets available in this package
__all__ = [
    # ViewSets
    'PartyViewSet',
    'PartyPhotoViewSet',
    'RSVPViewSet',
    'GiftRegistryItemViewSet',
    'GuestBookEntryViewSet',
    'GameScoreViewSet',
    'BadgeViewSet',
    'UserBadgeViewSet',
    'PartyTimelineEventViewSet',
    'TriviaQuestionViewSet',
    
    # Serializers
    'GameScoreSerializer',
    'GuestBookEntrySerializer',
    'BadgeSerializer',
    'UserBadgeSerializer',
    'PartyTimelineEventSerializer',
    'TriviaQuestionSerializer',
]

# ViewSet registry for programmatic access
VIEWSETS = {
    'party': PartyViewSet,
    'photo': PartyPhotoViewSet,
    'rsvp': RSVPViewSet,
    'gift_registry': GiftRegistryItemViewSet,
    'guest_book': GuestBookEntryViewSet,
    'game_score': GameScoreViewSet,
    'badge': BadgeViewSet,
    'user_badge': UserBadgeViewSet,
    'timeline_event': PartyTimelineEventViewSet,
    'trivia_question': TriviaQuestionViewSet,
}
