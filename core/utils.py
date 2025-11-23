# core/utils.py
from .models import Notification
from django.db import IntegrityError

def create_notification(to_username, actor_username, verb, notif_type='like', post_id=None, url=''):
    """
    Create a Notification record. Fail quietly but return the object on success.
    """
    try:
        n = Notification.objects.create(
            to_user=to_username,
            actor=actor_username,
            verb=verb,
            notif_type=notif_type,
            post_id=post_id,
            url=url,
        )
        return n
    except IntegrityError:
        return None
    except Exception:
        # avoid crashing the main user flow for any unexpected reason
        return None
