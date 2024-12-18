# you’ll want a utility function that will be used in your views, signals, or anywhere else in the codebase to log activity.
from . models import Logbook

def log_activity(user, action, description:None):
    Logbook.objects.create(user=user, action=action, description=description)
