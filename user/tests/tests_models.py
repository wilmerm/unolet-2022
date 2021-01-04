from django.test import TestCase

from user.models import User


def get_or_create_user():
    try:
        user = User.objects.get(username="test")
    except (User.DoesNotExist):
        user = User.objects.create_user(username="test", password="test")
        user.clean()
        user.save()
    return user