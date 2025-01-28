from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender='tracker.DailyFoodLog')
@receiver(post_save, sender='tracker.DailyActivityLog')
@receiver(post_delete, sender='tracker.DailyFoodLog')
@receiver(post_delete, sender='tracker.DailyActivityLog')
def update_daily_summary(sender, instance, **kwargs):
    """
    Updates the daily summary whenever a food or activity log is added, updated, or deleted.
    """
    DailySummary = apps.get_model('tracker', 'DailySummary')
    DailyFoodLog = apps.get_model('tracker', 'DailyFoodLog')
    DailyActivityLog = apps.get_model('tracker', 'DailyActivityLog')

    user = instance.user
    log_date = instance.date

    # Retrieve or create the DailySummary for the user and date
    daily_summary, created = DailySummary.objects.get_or_create(user=user, date=log_date)

    # Aggregate calories in and out
    total_calories_in = DailyFoodLog.objects.filter(user=user, date=log_date).aggregate(
        total=Sum('total_calories')
    )['total'] or 0

    total_calories_out = DailyActivityLog.objects.filter(user=user, date=log_date).aggregate(
        total=Sum('calories_burned')
    )['total'] or 0

    # Calculate BMR only if missing or when the summary is created
    if created or not daily_summary.bmr:
        daily_summary.bmr = user.calculate_bmr()

    # Calculate net calories
    net_calories = total_calories_in - (total_calories_out + daily_summary.bmr)

    # Update DailySummary fields
    daily_summary.calories_in = total_calories_in
    daily_summary.calories_out = total_calories_out
    daily_summary.net_calories = net_calories
    daily_summary.save(update_fields=['calories_in', 'calories_out', 'net_calories', 'bmr'])

    logger.info(f"Daily summary updated for {user.username} on {log_date}: {daily_summary}")
