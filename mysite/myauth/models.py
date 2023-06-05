from django.contrib.auth.models import User
from django.db import models


def user_preview_directory_path(instance: 'User', filename: str) -> str:
    return 'users/user_{pk}/avatar/{filename}'.format(pk=instance.pk, filename=filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, upload_to=user_preview_directory_path)
