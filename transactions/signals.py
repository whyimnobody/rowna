from django.db.models import signals
from django.dispatch import receiver

from .models import TransactionsFile


@receiver(signals.post_save, sender=TransactionsFile)
def process_file(sender, instance, created, **kwargs):
    """
    A post-save signal to process the uploaded file
    """

    if created:
        instance.process_file()
    # TODO: Add notification system for admins to have a look at the file, as to
    #  why it didn't save
