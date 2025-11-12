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
        # Write permissions require staff/admin or superuser
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_staff or request.user.is_superuser


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
    
    def to_internal_value(self, data):
        """Convert options array to individual option fields if needed"""
        # If frontend sends options as an array, convert to option_1, option_2, etc.
        if 'options' in data and isinstance(data['options'], list):
            options = data['options']
            # Map array to individual fields - always set all fields when options array is provided
            if len(options) > 0:
                data['option_1'] = options[0]
            if len(options) > 1:
                data['option_2'] = options[1]
            if len(options) > 2:
                data['option_3'] = options[2]
            else:
                data['option_3'] = ''  # Clear if fewer than 3 options
            if len(options) > 3:
                data['option_4'] = options[3]
            else:
                data['option_4'] = ''  # Clear if fewer than 4 options
            # Remove options array as it's not a model field
            data.pop('options', None)
        
        return super().to_internal_value(data)
    
    def validate(self, attrs):
        """Validate the entire object, including correct_answer range"""
        # Count how many options are provided
        options_count = 2
        if attrs.get('option_3'):
            options_count = 3
        if attrs.get('option_4'):
            options_count = 4
        
        # Validate correct_answer is within range
        correct_answer = attrs.get('correct_answer')
        if correct_answer is not None and correct_answer >= options_count:
            raise serializers.ValidationError({
                'correct_answer': f'correct_answer must be between 0 and {options_count - 1}'
            })
        
        return attrs


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
