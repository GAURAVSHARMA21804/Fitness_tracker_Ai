# users_auth/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from datetime import date

@receiver(post_save, sender='users_auth.CustomUser')
def log_initial_weight(sender, instance, created, **kwargs):
    if not created:  # Ensure it runs only when a new user is created
        return

    # Avoid direct or indirect saving of the user instance
    DailySummary = apps.get_model('tracker', 'DailySummary')

    # Check if all necessary fields for BMR calculation are present
    if instance.weight and instance.height and instance.dob and instance.gender:
        instance.last_calculated_bmr = instance.calculate_bmr()  # Avoid saving the instance here

    # Initialize today's daily summary
    today = date.today()
    DailySummary.objects.get_or_create(
        user=instance,
        date=today,
        defaults={
            'bmr': instance.last_calculated_bmr or 0,
            'net_calories': 0,
            'calories_in': 0,
            'calories_out': 0,
        },
    )
