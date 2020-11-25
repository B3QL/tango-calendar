from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFilter
from api.serializers import EventSerializer, RoomSerializer
from api.models import Meeting, Location


class EventFilter(FilterSet):
    day = DateFilter(field_name="start", lookup_expr='exact', label="Day")

    class Meta:
        model = Meeting
        fields = ["location_id", "day"]


class EventsView(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["event_name", "meeting_agenda"]
    filterset_class = EventFilter

    def get_queryset(self):
        """Restrict view to participants and location owners."""
        participate_in = Meeting.objects.filter(participant_list=self.request.user)
        is_location_manager = Meeting.objects.filter(location__manager=self.request.user)
        return participate_in | is_location_manager


class RoomsView(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    queryset = Location.objects.all()
