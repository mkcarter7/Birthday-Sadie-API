from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from ..models import TriviaQuestion, Party


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to anyone, but write operations require admin/staff status.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions require staff/admin
        return request.user and request.user.is_authenticated and request.user.is_staff


class TriviaQuestionSerializer(serializers.ModelSerializer):
    """Serializer for TriviaQuestion model"""
    party_name = serializers.CharField(source='party.name', read_only=True)
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = TriviaQuestion
        fields = [
            'id', 'party', 'party_name', 'category', 'question',
            'option_1', 'option_2', 'option_3', 'option_4',
            'options', 'correct_answer', 'points', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_options(self, obj):
        """Return list of options, filtering out empty ones"""
        return obj.get_options()
    
    def validate_correct_answer(self, value):
        """Ensure correct_answer is within valid range"""
        options_count = 2
        if self.initial_data.get('option_3'):
            options_count = 3
        if self.initial_data.get('option_4'):
            options_count = 4
        
        if value >= options_count:
            raise serializers.ValidationError(
                f'correct_answer must be between 0 and {options_count - 1}'
            )
        return value


class TriviaQuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trivia questions
    Admins can create, update, and delete trivia questions
    """
    serializer_class = TriviaQuestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            # Anyone can view trivia questions
            return [AllowAny()]
        else:
            # Only admins can create, update, or delete
            return [IsAdminOrReadOnly()]
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = TriviaQuestion.objects.select_related('party')
        
        # Filter by party if specified
        party_id = self.request.query_params.get('party')
        if party_id:
            queryset = queryset.filter(party_id=party_id)
        
        # Filter by category if specified
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Filter active questions only (for non-admin list view)
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(question__icontains=search) |
                Q(category__icontains=search)
            )
        
        return queryset.order_by('category', 'question')
