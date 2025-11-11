from rest_framework import viewsets, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..models import PartyTimelineEvent


class PartyTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyTimelineEvent
        fields = [
            'id',
            'party',
            'time',
            'activity',
            'description',
            'icon',
            'duration_minutes',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PartyTimelineEventViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for party timeline events.
    """

    serializer_class = PartyTimelineEventSerializer
    queryset = PartyTimelineEvent.objects.all().select_related('party')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        party_id = self.request.query_params.get('party')
        if party_id:
            queryset = queryset.filter(party_id=party_id)
        active = self.request.query_params.get('active')
        if active and active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset.order_by('time')
