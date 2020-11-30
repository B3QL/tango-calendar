from datetime import datetime, timedelta
import pytz
from freezegun import freeze_time
from django.test import TestCase
from rest_framework.test import APIClient
import factory
from api.models import APIUser, Location, Meeting
from api.serializers import RoomSerializer, EventSerializer


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.org")
    company_id = "029cf390-4234-494d-b464-000000c0ffee"

    class Meta:
        model = APIUser


class LocationFactory(factory.django.DjangoModelFactory):
    manager = factory.SubFactory(UserFactory)

    class Meta:
        model = Location


class MeetingFactory(factory.django.DjangoModelFactory):
    event_name = factory.Sequence(lambda n: f"Event {n}")
    meeting_agenda = factory.Sequence(lambda n: f"Event agenda {n}")
    start = datetime(2020, 11, 27, tzinfo=pytz.utc)
    end = datetime(2020, 11, 27, 6, tzinfo=pytz.utc)
    owner = factory.SubFactory(UserFactory)
    location = factory.SubFactory(LocationFactory)

    class Meta:
        model = Meeting


class TestEventsView(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.client = APIClient()
        self.client.force_login(self.user)
        self.location = LocationFactory.create(manager=self.user)
        self.events_url = "/api/events/"
        self.rooms_url = "/api/rooms/"

    def test_users_only_logged(self):
        self.client.logout()
        for url in [self.events_url, self.rooms_url]:
            with self.subTest(msg=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_location_tenants(self):
        same_tenant_user = UserFactory.create(company_id=self.user.company_id)
        other_tenant_user = UserFactory.create(
            company_id="029cf390-4234-494d-b464-0000deadbeef"
        )
        _same_tenant_location = LocationFactory.create(manager=same_tenant_user)
        _other_tenant_location = LocationFactory.create(manager=other_tenant_user)

        self.assertEqual(Location.objects.count(), 3)

        response = self.client.get(self.rooms_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_events_tenants(self):
        same_tenant_user = UserFactory.create(company_id=self.user.company_id)
        other_tenant_user = UserFactory.create(
            company_id="029cf390-4234-494d-b464-0000deadbeef"
        )
        same_tenant_event = MeetingFactory.create(owner=same_tenant_user)
        same_tenant_event.participant_list.set([self.user])
        other_tenant_event = MeetingFactory.create(owner=other_tenant_user)
        other_tenant_event.participant_list.set([self.user])

        self.assertEqual(Meeting.objects.count(), 2)

        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_events_access_location_manager(self):
        another_user = UserFactory.create(company_id=self.user.company_id)
        location = LocationFactory(manager=another_user)
        _with_other_location = MeetingFactory.create(location=location)
        _with_user_location = MeetingFactory.create(location=self.location)
        _without_location = MeetingFactory.create(location=None)

        self.assertEqual(Meeting.objects.count(), 3)

        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_events_access_participant(self):
        another_user = UserFactory.create(company_id=self.user.company_id)
        _no_participant = MeetingFactory.create()
        other_participant = MeetingFactory.create()
        other_participant.participant_list.set([another_user])

        user_participant = MeetingFactory.create()
        user_participant.participant_list.set([another_user, self.user])

        self.assertEqual(Meeting.objects.count(), 3)

        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_events_duplicates(self):
        other_user = UserFactory.create()
        event = MeetingFactory.create(location=self.location)
        event.participant_list.set([other_user, self.user])

        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_events_empty(self):
        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_events_day_filtering(self):
        MeetingFactory.create(
            start=datetime(2020, 11, 27, tzinfo=pytz.utc),
            end=datetime(2020, 11, 27, 8, tzinfo=pytz.utc),
            location=self.location,
        )
        MeetingFactory.create(
            start=datetime(2020, 11, 28, tzinfo=pytz.utc),
            end=datetime(2020, 11, 28, 8, tzinfo=pytz.utc),
            location=self.location,
        )

        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

        response = self.client.get(self.events_url, data={"day": "2020-11-27"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    @freeze_time("2020-11-30")
    def test_events_timezones(self):
        warsaw_user = UserFactory.create(timezone="Europe/Warsaw")

        self.assertNotEqual(self.user.timezone, warsaw_user.timezone)
        self.client.force_login(warsaw_user)
        create_response = self.client.post(
            self.events_url,
            data={
                "event_name": "Test event",
                "meeting_agenda": "Dummy agenda",
                "start": "2222-12-12T06:00:00",
                "end": "2222-12-12T12:00:00",
                "participant_list": [self.user.email, warsaw_user.email],
                "location": self.location.id,
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, 201)

        self.client.force_login(self.user)
        response = self.client.get(self.events_url)
        (event,) = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(event["start"], "2222-12-12T05:00:00Z")
        self.assertEqual(event["end"], "2222-12-12T11:00:00Z")

    def test_events_location_filtering(self):
        with_location = MeetingFactory.create(location=self.location)
        without_location = MeetingFactory.create(location=None)
        without_location.participant_list.set([self.user])

        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

        response = self.client.get(
            self.events_url, data={"location_id": with_location.location.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_events_search(self):
        _event_with_name = MeetingFactory.create(
            event_name="A", meeting_agenda="B", location=self.location
        )
        _event_with_agenda = MeetingFactory.create(
            meeting_agenda="A", event_name="B", location=self.location
        )
        _filtered_event = MeetingFactory.create(
            event_name="B", meeting_agenda="B", location=self.location
        )

        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

        response = self.client.get(self.events_url, data={"query": "A"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_events_nested_location(self):
        MeetingFactory.create(location=self.location)

        response = self.client.get(self.events_url)
        (event,) = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(event["location"], RoomSerializer(self.location).data)

    def test_events_set_owner(self):
        event = MeetingFactory.build()
        event_json = EventSerializer(event).data
        event_json["location"] = self.location.id
        del event_json["owner"]

        self.test_events_empty()

        response = self.client.post(self.events_url, data=event_json, format="json")
        event_response = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(event_response["owner"], self.user.email)

    def test_events_length_limit(self):
        start = datetime(2020, 11, 23, 21, 37)
        end = start + timedelta(hours=8)
        overtime = end + timedelta(microseconds=1)
        event = MeetingFactory.build(start=start, end=end)
        event_json = EventSerializer(event).data
        event_json["location"] = self.location.id
        del event_json["owner"]

        self.test_events_empty()

        response = self.client.post(self.events_url, data=event_json, format="json")
        self.assertEqual(response.status_code, 201)

        event_json["end"] = overtime.isoformat()
        response = self.client.post(self.events_url, data=event_json, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"non_field_errors": ["Meetings shouldn’t be longer than 8 hours."]},
        )
