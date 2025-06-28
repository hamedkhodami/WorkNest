import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from phonenumber_field.phonenumber import PhoneNumber
from apps.notification.models import Notification
from apps.notification.enums import NotificationType, NotificationStatus
from apps.account.tests.factories import UserFactory


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    type = factory.Iterator([NotificationType.EMAIL, NotificationType.SMS, NotificationType.IN_APP])
    status = factory.Iterator([NotificationStatus.PENDING, NotificationStatus.SENT, NotificationStatus.FAILED])

    title = factory.Faker('sentence', nb_words=6)
    description = factory.Faker('paragraph', nb_sentences=3)
    kwargs = factory.LazyFunction(lambda: {"link": "https://example.com/detail/123", "priority": "high"})

    user = factory.SubFactory(UserFactory)
    email = factory.LazyAttribute(lambda obj: obj.user.email if obj.user else factory.Faker('email').generate({}))
    phone_number = factory.LazyAttribute(lambda _: PhoneNumber.from_string("+989123456789", region="IR"))

    is_visited = factory.Faker('boolean', chance_of_getting_true=30)
    retry_count = factory.Faker('random_int', min=0, max=3)
    sent_at = factory.LazyFunction(timezone.now)
