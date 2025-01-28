from django.db import models
from users_auth.models import CustomUser
from datetime import date


# food data model 
class FoodData(models.Model):
    food_id = models.AutoField(primary_key=True)
    food_name = models.CharField(max_length=355)
    food_group = models.CharField(max_length=255, blank=True, null=True)  # Food group (optional)
    calories = models.FloatField()  # Calories per serving
    fat = models.FloatField()  # Fat in grams per serving
    protein = models.FloatField()  # Protein in grams per serving
    carbohydrate = models.FloatField()  # Carbohydrate in grams per serving
    serving_description = models.CharField(max_length=255, blank=True, null=True , default=1)  # Serving description (e.g., 100g)

    def __str__(self):
        return f"{self.food_name} ({self.calories} cal)"

# activity data model
class ActivityData(models.Model):
    activity_id = models.AutoField(primary_key=True)
    activity_name = models.CharField(max_length=255)  # General activity name
    specific_motion = models.CharField(max_length=255)  # Detailed description
    mets = models.FloatField()  # METs value for the activity

    def __str__(self):
        return f"{self.activity_name} - {self.specific_motion} ({self.mets} METs)"

# Lookup table for meal types (optional)
class MealType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# daily food logs model 
class DailyFoodLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    food_item = models.ForeignKey(FoodData, on_delete=models.CASCADE)
    meal_type = models.ForeignKey(MealType, on_delete=models.CASCADE)
    serving_count = models.PositiveIntegerField()
    total_calories = models.FloatField(editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate total calories for the serving count
        self.total_calories = self.serving_count * self.food_item.calories
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food_item.food_name} ({self.date})"
    
# daily activity log model
class DailyActivityLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    activity = models.ForeignKey(ActivityData, on_delete=models.CASCADE)
    duration_minutes = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)  # Optional activity description
    calories_burned = models.FloatField(editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate calories burned using METs, user weight, and duration
        weight_kg = self.user.weight  # Use the weight from CustomUser directly
        duration_hours = self.duration_minutes / 60
        self.calories_burned = self.activity.mets * weight_kg * duration_hours
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.activity.activity_name} ({self.date})"

# Daily summary for storing calculated metrics
class DailySummary(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    bmr = models.FloatField()  # Copied from UserProfile
    calories_in = models.FloatField()  # Sum of food calories
    calories_out = models.FloatField()  # Sum of activity calories burned
    net_calories = models.FloatField(editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Safeguard against NoneType values
        self.calories_in = self.calories_in or 0
        self.calories_out = self.calories_out or 0
        self.bmr = self.bmr or 0

        # Calculate net calories
        self.net_calories = self.calories_in - (self.calories_out + self.bmr)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s summary on {self.date}"


    

