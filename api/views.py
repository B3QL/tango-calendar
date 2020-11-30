from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFilter
from api.serializers import EventSerializer, RoomSerializer
from api.models import Meeting, Location


class EventFilter(FilterSet):
    day = DateFilter(field_name="start", lookup_expr="exact", label="Day")

    class Meta:
        model = Meeting
        fields = ["location_id", "day"]


class EventsView(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["event_name", "meeting_agenda"]
    filterset_class = EventFilter

    def get_queryset(self):
        """Restrict view to tenants, participants and location owners."""
        tenant_meetings = Meeting.objects.filter(
            owner__company_id=self.request.user.company_id
        )
        participate_in = tenant_meetings.filter(
            participant_list__in=[self.request.user]
        )
        is_location_manager = tenant_meetings.filter(
            location__manager=self.request.user
        )
        filtered = participate_in | is_location_manager
        return filtered.distinct()


class RoomsView(viewsets.ModelViewSet):
    serializer_class = RoomSerializer

    def get_queryset(self):
        """Restrict view to tenants."""
        return Location.objects.filter(manager__company_id=self.request.user.company_id)
