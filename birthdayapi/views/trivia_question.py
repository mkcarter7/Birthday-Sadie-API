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
    party_name = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    
    def get_party_name(self, obj):
        """Return party name or None if party doesn't exist"""
        if obj and obj.party:
            return obj.party.name
        return None
    
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
        if obj is None:
            return []
        options = obj.get_options()
        # Ensure we always return a list, even if empty
        return options if isinstance(options, list) else []
    
    def to_internal_value(self, data):
        """Convert options array to individual option fields if needed"""
        # If frontend sends options as an array, convert to option_1, option_2, etc.
        if 'options' in data and isinstance(data['options'], list):
            options = data['options']
            # Map array to individual fields - always set all fields when options array is provided
            # This handles both full updates (PUT) and partial updates (PATCH)
            if len(options) > 0:
                data['option_1'] = options[0]
            else:
                data['option_1'] = ''  # Clear if empty
            if len(options) > 1:
                data['option_2'] = options[1]
            else:
                data['option_2'] = ''  # Clear if fewer than 2 options
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
        # For partial updates, we need to check existing instance values too
        instance = self.instance
        
        # Count how many options are provided
        # Check both attrs (new values) and instance (existing values) for partial updates
        option_1 = attrs.get('option_1') if 'option_1' in attrs else (instance.option_1 if instance else None)
        option_2 = attrs.get('option_2') if 'option_2' in attrs else (instance.option_2 if instance else None)
        option_3 = attrs.get('option_3') if 'option_3' in attrs else (instance.option_3 if instance else None)
        option_4 = attrs.get('option_4') if 'option_4' in attrs else (instance.option_4 if instance else None)
        
        # Count non-empty options
        options_count = 0
        if option_1:
            options_count = 1
        if option_2:
            options_count = 2
        if option_3:
            options_count = 3
        if option_4:
            options_count = 4
        
        # Validate correct_answer is within range
        # For partial updates, use existing correct_answer if not provided
        correct_answer = attrs.get('correct_answer')
        if correct_answer is None and instance:
            correct_answer = instance.correct_answer
        
        if correct_answer is not None:
            if options_count == 0:
                raise serializers.ValidationError({
                    'options': 'At least one option is required'
                })
            
            if correct_answer < 0 or correct_answer >= options_count:
                raise serializers.ValidationError({
                    'correct_answer': f'correct_answer must be between 0 and {options_count - 1} (you have {options_count} options)'
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
