from django.conf import settings
from rest_framework import serializers

from .models import GalleryPhoto, Guest, GuestUpload, Rsvp, TimelineEvent, Wedding


class TimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEvent
        fields = ["id", "title", "date_label", "text"]


class GalleryPhotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryPhoto
        fields = ["id", "url", "caption"]

    def get_url(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return None
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class GuestSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Guest
        fields = ["code", "name", "honorific", "display_name", "seats"]


class WeddingSerializer(serializers.ModelSerializer):
    timeline = TimelineEventSerializer(many=True, read_only=True)
    gallery = GalleryPhotoSerializer(many=True, read_only=True)
    hero_url = serializers.SerializerMethodField()
    music_url = serializers.SerializerMethodField()
    max_upload_mb = serializers.SerializerMethodField()

    class Meta:
        model = Wedding
        fields = [
            "mode",
            "groom_name",
            "bride_name",
            "event_at",
            "welcome_time",
            "venue_name",
            "venue_address",
            "map_url",
            "latitude",
            "longitude",
            "invite_text",
            "dress_code",
            "contact_one_name",
            "contact_one_phone",
            "contact_two_name",
            "contact_two_phone",
            "hero_url",
            "music_url",
            "rsvp_open",
            "uploads_open",
            "thanks_title",
            "thanks_text",
            "upload_hint",
            "timeline",
            "gallery",
            "max_upload_mb",
        ]

    def _abs(self, field):
        request = self.context.get("request")
        if not field:
            return None
        return request.build_absolute_uri(field.url) if request else field.url

    def get_hero_url(self, obj):
        return self._abs(obj.hero_image)

    def get_music_url(self, obj):
        return self._abs(obj.music)

    def get_max_upload_mb(self, obj):
        return settings.MAX_UPLOAD_SIZE_MB


class RsvpCreateSerializer(serializers.ModelSerializer):
    guest_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Rsvp
        fields = ["name", "attending", "seats", "phone", "message", "guest_code"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Ismingizni to'liqroq yozing.")
        return value

    def validate_seats(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError("Mehmonlar soni 1 dan 20 gacha bo'lishi kerak.")
        return value


class GuestUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestUpload
        fields = ["id", "original_name", "size", "is_video", "created_at"]
        read_only_fields = fields
