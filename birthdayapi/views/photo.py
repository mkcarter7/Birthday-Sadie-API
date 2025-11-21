from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ..models import PartyPhoto, PhotoLike, Party
from rest_framework import serializers
from rest_framework import permissions


class IsPhotoOwnerOrAdmin(permissions.BasePermission):
    """
    Allow deletion if the user is a staff/admin or the uploader of the photo.
    """
    def has_object_permission(self, request, view, obj):
        # Allow if user is staff/admin
        if request.user and request.user.is_staff:
            return True
        # Allow if user is the photo owner
        return obj.uploaded_by == request.user

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class PartyPhotoSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    party_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()  # Override to return absolute URL
    
    class Meta:
        model = PartyPhoto
        fields = [
            'id', 'party', 'image', 'caption', 'uploaded_at', 'uploaded_by',
            'likes_count', 'is_liked', 'is_featured', 'party_name'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'likes_count', 'image']
    
    def get_likes_count(self, obj):
        """Safely get likes count"""
        try:
            return obj.likes_count if hasattr(obj, 'likes_count') else obj.likes.count()
        except Exception:
            return 0
    
    def get_party_name(self, obj):
        """Safely get party name"""
        try:
            return obj.party.name if obj.party else None
        except Exception:
            return None
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            try:
                return obj.likes.filter(user=request.user).exists()
            except Exception:
                # If there's any error checking likes, just return False
                return False
        return False
    
    def get_image(self, obj):
        """Return absolute URL for image in production"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            # Fallback: construct absolute URL from settings
            from django.conf import settings
            if hasattr(settings, 'ALLOWED_HOSTS') and settings.ALLOWED_HOSTS:
                host = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
                protocol = 'https' if not settings.DEBUG else 'http'
                return f'{protocol}://{host}{obj.image.url}'
        return None

class PhotoLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PhotoLike
        fields = ['id', 'user', 'photo', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class PartyPhotoViewSet(viewsets.ModelViewSet):
    serializer_class = PartyPhotoSerializer
    permission_classes = [AllowAny]  # Default to allow anyone to view
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Anyone can view photos
        if self.action in ['list', 'retrieve', 'party_gallery']:
            return [AllowAny()]
        # Allow owner or admin to delete (must be authenticated)
        elif self.action in ['destroy']:
            return [IsAuthenticated(), IsPhotoOwnerOrAdmin()]
        # Authenticated users can upload and like
        else:
            return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        """Override list to handle errors gracefully"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error listing photos: {str(e)}", exc_info=True)
            # Return empty list instead of 500 error
            return Response({
                'count': 0,
                'results': []
            }, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        queryset = PartyPhoto.objects.all()
        
        # Filter by party if specified
        party_id = self.request.query_params.get('party')
        if party_id:
            queryset = queryset.filter(party_id=party_id)
        
        # Filter by user's photos (only if authenticated)
        my_photos = self.request.query_params.get('my_photos')
        if my_photos and my_photos.lower() == 'true':
            # Safely check if user is authenticated
            if hasattr(self.request, 'user') and self.request.user and self.request.user.is_authenticated:
                queryset = queryset.filter(uploaded_by=self.request.user)
        
        # Filter by featured photos
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.select_related('uploaded_by', 'party').prefetch_related('likes')
    
    def create(self, request, *args, **kwargs):
        """Override create to provide better error messages"""
        # Check authentication first
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required. Please log in to upload photos."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # User is already authenticated due to permission classes and create() check
        party_id = self.request.data.get('party')
        if not party_id:
            raise serializers.ValidationError({"party": "Party ID is required"})
        
        try:
            party = Party.objects.get(id=party_id)
        except Party.DoesNotExist:
            raise serializers.ValidationError({"party": f"Party with ID {party_id} does not exist"})
        
        # Validate that image is provided
        if 'image' not in self.request.data and 'image' not in self.request.FILES:
            raise serializers.ValidationError({"image": "Image file is required"})
        
        serializer.save(uploaded_by=self.request.user, party=party)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to like photos'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        photo = self.get_object()
        like, created = PhotoLike.objects.get_or_create(
            user=request.user,
            photo=photo
        )
        
        if created:
            return Response(
                {'message': 'Photo liked', 'likes_count': photo.likes_count},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Photo already liked', 'likes_count': photo.likes_count},
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to unlike photos'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        photo = self.get_object()
        
        try:
            like = PhotoLike.objects.get(user=request.user, photo=photo)
            like.delete()
            return Response(
                {'message': 'Photo unliked', 'likes_count': photo.likes_count},
                status=status.HTTP_200_OK
            )
        except PhotoLike.DoesNotExist:
            return Response(
                {'message': 'Photo was not liked', 'likes_count': photo.likes_count},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        photo = self.get_object()
        
        # Check if user is the party host
        if photo.party.host != request.user:
            return Response(
                {'error': 'Only the party host can feature photos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        photo.is_featured = not photo.is_featured
        photo.save()
        
        return Response({
            'message': f'Photo {"featured" if photo.is_featured else "unfeatured"}',
            'is_featured': photo.is_featured
        })

    def perform_destroy(self, instance):
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def party_gallery(self, request):
        party_id = request.query_params.get('party_id')
        if not party_id:
            return Response(
                {'error': 'party_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        party = get_object_or_404(Party, id=party_id)
        photos = PartyPhoto.objects.filter(party=party).select_related('uploaded_by')
        
        serializer = self.get_serializer(photos, many=True)
        return Response({
            'party': {
                'id': party.id,
                'name': party.name,
                'date': party.date
            },
            'photos': serializer.data
        })
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ..models import PartyPhoto, PhotoLike, Party
from rest_framework import serializers
from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)


class IsPhotoOwnerOrAdmin(permissions.BasePermission):
    """
    Allow deletion if the user is a staff/admin or the uploader of the photo.
    """
    def has_object_permission(self, request, view, obj):
        # Allow if user is staff/admin
        if request.user and request.user.is_staff:
            return True
        # Allow if user is the photo owner
        return obj.uploaded_by == request.user

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class PartyPhotoSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    party_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()  # Override to return absolute URL
    
    class Meta:
        model = PartyPhoto
        fields = [
            'id', 'party', 'image', 'caption', 'uploaded_at', 'uploaded_by',
            'likes_count', 'is_liked', 'is_featured', 'party_name'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'likes_count', 'image']
    
    def get_likes_count(self, obj):
        """Safely get likes count"""
        try:
            return obj.likes_count if hasattr(obj, 'likes_count') else obj.likes.count()
        except Exception:
            return 0
    
    def get_party_name(self, obj):
        """Safely get party name"""
        try:
            return obj.party.name if obj.party else None
        except Exception:
            return None
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            try:
                return obj.likes.filter(user=request.user).exists()
            except Exception:
                # If there's any error checking likes, just return False
                return False
        return False
    
    def get_image(self, obj):
        """Return absolute URL for image in production"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            # Fallback: construct absolute URL from settings
            from django.conf import settings
            if hasattr(settings, 'ALLOWED_HOSTS') and settings.ALLOWED_HOSTS:
                host = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
                protocol = 'https' if not settings.DEBUG else 'http'
                return f'{protocol}://{host}{obj.image.url}'
        return None

class PhotoLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PhotoLike
        fields = ['id', 'user', 'photo', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class PartyPhotoViewSet(viewsets.ModelViewSet):
    serializer_class = PartyPhotoSerializer
    permission_classes = [AllowAny]  # Default to allow anyone to view
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Anyone can view photos
        if self.action in ['list', 'retrieve', 'party_gallery']:
            return [AllowAny()]
        # Allow owner or admin to delete (must be authenticated)
        elif self.action in ['destroy']:
            return [IsAuthenticated(), IsPhotoOwnerOrAdmin()]
        # Authenticated users can upload and like
        else:
            return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        """Override list to handle errors gracefully"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error listing photos: {str(e)}", exc_info=True)
            # Return empty list instead of 500 error
            return Response({
                'count': 0,
                'results': []
            }, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        queryset = PartyPhoto.objects.all()
        
        # Filter by party if specified
        party_id = self.request.query_params.get('party')
        if party_id:
            queryset = queryset.filter(party_id=party_id)
        
        # Filter by user's photos (only if authenticated)
        my_photos = self.request.query_params.get('my_photos')
        if my_photos and my_photos.lower() == 'true':
            # Safely check if user is authenticated
            if hasattr(self.request, 'user') and self.request.user and self.request.user.is_authenticated:
                queryset = queryset.filter(uploaded_by=self.request.user)
        
        # Filter by featured photos
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.select_related('uploaded_by', 'party').prefetch_related('likes')
    
    def create(self, request, *args, **kwargs):
        """Override create to provide better error messages and debug authentication"""
        # Log authentication debugging info
        auth_header = request.META.get('HTTP_AUTHORIZATION') or request.META.get('Authorization')
        logger.info(f"Photo upload - Request method: {request.method}")
        logger.info(f"Photo upload - Content-Type: {request.content_type}")
        logger.info(f"Photo upload - Authorization header present: {bool(auth_header)}")
        if auth_header:
            logger.info(f"Photo upload - Authorization header prefix: {auth_header[:30]}")
        else:
            # Log all headers that start with HTTP_ to see what's available
            http_headers = {k: v[:50] if len(v) > 50 else v for k, v in request.META.items() if k.startswith('HTTP_')}
            logger.warning(f"Photo upload - Available HTTP_ headers: {list(http_headers.keys())}")
        
        logger.info(f"Photo upload - User authenticated: {request.user.is_authenticated if hasattr(request, 'user') else 'No user object'}")
        logger.info(f"Photo upload - User: {request.user if hasattr(request, 'user') else 'No user'}")
        
        # Check authentication first
        if not request.user or not request.user.is_authenticated:
            logger.error("Photo upload - Authentication failed: User not authenticated")
            return Response(
                {"error": "Authentication required. Please log in to upload photos."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        logger.info(f"Photo upload - Proceeding with authenticated user: {request.user.username}")
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # User is already authenticated due to permission classes and create() check
        party_id = self.request.data.get('party')
        if not party_id:
            raise serializers.ValidationError({"party": "Party ID is required"})
        
        try:
            party = Party.objects.get(id=party_id)
        except Party.DoesNotExist:
            raise serializers.ValidationError({"party": f"Party with ID {party_id} does not exist"})
        
        # Validate that image is provided
        if 'image' not in self.request.data and 'image' not in self.request.FILES:
            raise serializers.ValidationError({"image": "Image file is required"})
        
        serializer.save(uploaded_by=self.request.user, party=party)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to like photos'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        photo = self.get_object()
        like, created = PhotoLike.objects.get_or_create(
            user=request.user,
            photo=photo
        )
        
        if created:
            return Response(
                {'message': 'Photo liked', 'likes_count': photo.likes_count},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Photo already liked', 'likes_count': photo.likes_count},
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to unlike photos'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        photo = self.get_object()
        
        try:
            like = PhotoLike.objects.get(user=request.user, photo=photo)
            like.delete()
            return Response(
                {'message': 'Photo unliked', 'likes_count': photo.likes_count},
                status=status.HTTP_200_OK
            )
        except PhotoLike.DoesNotExist:
            return Response(
                {'message': 'Photo was not liked', 'likes_count': photo.likes_count},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        photo = self.get_object()
        
        # Check if user is the party host
        if photo.party.host != request.user:
            return Response(
                {'error': 'Only the party host can feature photos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        photo.is_featured = not photo.is_featured
        photo.save()
        
        return Response({
            'message': f'Photo {"featured" if photo.is_featured else "unfeatured"}',
            'is_featured': photo.is_featured
        })

    def perform_destroy(self, instance):
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def party_gallery(self, request):
        party_id = request.query_params.get('party_id')
        if not party_id:
            return Response(
                {'error': 'party_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        party = get_object_or_404(Party, id=party_id)
        photos = PartyPhoto.objects.filter(party=party).select_related('uploaded_by')
        
        serializer = self.get_serializer(photos, many=True)
        return Response({
            'party': {
                'id': party.id,
                'name': party.name,
                'date': party.date
            },
            'photos': serializer.data
        })
