from datetime import timedelta
from rest_framework.serializers import ValidationError


def validate_meeting_length(meeting):
    meeting_length = meeting["end"] - meeting["start"]
    if meeting_length > timedelta(hours=8):
        raise ValidationError("Meetings shouldn’t be longer than 8 hours.")
