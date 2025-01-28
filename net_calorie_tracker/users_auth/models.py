from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password

class CustomUser(AbstractUser):
    name = models.CharField(max_length=150, blank=False)
    weight = models.FloatField(help_text="Weight in kg", null=True, blank=True)
    height = models.FloatField(help_text="Height in cm", null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female')],
        null=True,
        blank=True,
    )
    dob = models.DateField(help_text="Date of birth", null=True, blank=True)
    is_admin = models.BooleanField(default=False, help_text="True for admin users")
    last_calculated_bmr = models.FloatField(null=True, blank=True, help_text="Cached BMR value")
    def __str__(self):
        return self.username
    
    def set_password(self, raw_password):
        """Override to ensure password is hashed"""
        self.password = make_password(raw_password)

    @property
    def age(self):
        """Calculate age based on the date of birth."""
        from datetime import date
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None
    
    def calculate_bmr(self):
        """Explicit method to calculate and store BMR."""
        if not all([self.weight, self.height, self.age, self.gender]):
            return None  # Ensure all required fields are available
        if self.gender == 'male':
            bmr = 66.4730 + (13.7516 * self.weight) + (5.0033 * self.height) - (6.7550 * self.age)
        elif self.gender == 'female':
            bmr = 655.0955 + (9.5634 * self.weight) + (1.8496 * self.height) - (4.6756 * self.age)
        else:
            return None

        # Cache the BMR
        self.last_calculated_bmr = bmr
        self.save(update_fields=['last_calculated_bmr'])
        return bmr