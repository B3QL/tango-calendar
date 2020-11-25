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
    queryset = Meeting.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["event_name", "meeting_agenda"]
    filterset_class = EventFilter


class RoomsView(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    queryset = Location.objects.all()
