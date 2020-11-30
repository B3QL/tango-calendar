from collections import OrderedDict
from rest_framework import serializers
from api.models import Meeting, Location, APIUser
from api.validators import validate_meeting_length


class RoomSerializer(serializers.ModelSerializer):
    manager = serializers.SlugRelatedField(
        slug_field="email", queryset=APIUser.objects.all()
    )

    class Meta:
        model = Location
        fields = ["id", "manager", "name", "address"]


class RelatedFieldAlternative(serializers.PrimaryKeyRelatedField):
    """
    Related field which allows to use alternative representation.

    https://stackoverflow.com/questions/29950956/drf-simple-foreign-key-assignment-with-nested-serializers
    """

    def __init__(self, **kwargs):
        self.serializer = kwargs.pop("serializer", None)
        if self.serializer is not None and not issubclass(
            self.serializer, serializers.Serializer
        ):
            raise TypeError('"serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        """Do not use pk optimization when serializer present."""
        return False if self.serializer else True

    def to_representation(self, instance):
        """Return representation from custom serializer."""
        if self.serializer:
            return self.serializer(instance, context=self.context).data
        return super().to_representation(instance)

    def get_choices(self, cutoff=None):
        """Use parent `to_representation` to return choices."""
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        parent = super()
        return OrderedDict(
            [
                (parent.to_representation(item), self.display_value(item))
                for item in queryset
            ]
        )


class EventSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field="email", read_only=True)
    participant_list = serializers.SlugRelatedField(
        many=True, slug_field="email", queryset=APIUser.objects.all()
    )
    location = RelatedFieldAlternative(
        serializer=RoomSerializer, queryset=Location.objects.all(), allow_null=True
    )

    class Meta:
        model = Meeting
        fields = [
            "id",
            "owner",
            "event_name",
            "meeting_agenda",
            "start",
            "end",
            "participant_list",
            "location",
        ]
        validators = [validate_meeting_length]

    def save(self, **kwargs):
        """Set owner from current request."""
        request = self._context["request"]
        super().save(owner=request.user, **kwargs)
