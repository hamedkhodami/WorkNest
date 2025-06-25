from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
# TODO: install
#from jsonfield import JSONField

from apps.core.models import BaseModel


class NotificationUser(BaseModel):
    """
        notification for user
    """
    type = models.CharField(max_length=100)
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    #kwargs = JSONField(null=True, blank=True)
    send_notify = models.BooleanField(default=True)
    to_user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    is_visited = models.BooleanField(default=False)

    class Meta:
        ordering = '-created_at',

    def __str__(self):
        return f'notification for {self.to_user}'

    def get_title(self):
        return self.title or 'notification'

    def get_content(self):
        return f"""
            {self.get_title()}
            {self.description}
        """

    def get_link(self):
        try:
            link = self.kwargs['link']
            return link
        except (KeyError, TypeError):
            return None


class NotificationUserPhonenumber(BaseModel):
    """
        notification for user by phonenumber
    """
    type = models.CharField(max_length=100)
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    # attach content
    #kwargs = JSONField(null=True, blank=True)

    phone_number = PhoneNumberField(region='IR')