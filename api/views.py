from rest_framework import viewsets
from api.serializers import EventSerializer, RoomSerializer
from api.models import Meeting, Location


class EventsView(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Meeting.objects.all()


class RoomsView(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    queryset = Location.objects.all()
