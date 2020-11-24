from rest_framework import serializers
from api.models import Meeting, Location, APIUser


class RoomSerializer(serializers.ModelSerializer):
    manager = serializers.SlugRelatedField(slug_field='email', queryset=APIUser.objects.all())

    class Meta:
        model = Location
        fields = ["id", "manager", "name", "address"]


class EventSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field='email', read_only=True)
    participant_list = serializers.SlugRelatedField(
        many=True,
        slug_field='email',
        queryset=APIUser.objects.all()
    )
    location = RoomSerializer(read_only=True)

    class Meta:
        model = Meeting
        fields = ['id', 'owner', 'event_name', 'meeting_agenda', 'start', 'end', 'participant_list', 'location']

    def save(self, **kwargs):
        """Set owner from current request."""
        request = self._context['request']
        super().save(owner=request.user, **kwargs)
