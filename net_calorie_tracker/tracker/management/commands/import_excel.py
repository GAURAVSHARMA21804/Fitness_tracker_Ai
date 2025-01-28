import pandas as pd
from django.core.management.base import BaseCommand
from tracker.models import FoodData, ActivityData

class Command(BaseCommand):
    help = 'Imports data from an Excel file (food or activity)'

    def add_arguments(self, parser):
        # Adding arguments for Excel file and data type (food or activity)
        parser.add_argument('excel_file', type=str)
        parser.add_argument('--type', type=str, choices=['food', 'activity'], help="Type of data to import (food/activity)")

    def handle(self, *args, **kwargs):
        # Geting the file path and type of data to import
        excel_file = kwargs['excel_file']
        data_type = kwargs['type']

        if data_type == 'food':
            self.import_food_data(excel_file)
        elif data_type == 'activity':
            self.import_activity_data(excel_file)
        else:
            self.stdout.write(self.style.ERROR('Invalid data type specified'))

    def import_food_data(self, excel_file):
        try:
            # Loading the Excel file containing food data
            df = pd.read_excel(excel_file)
            self.stdout.write(f"Number of rows in Excel: {len(df)}")

            # Loop through the rows in the DataFrame and save to database
            for index, row in df.iterrows():
                try:
                    # Extractacting data from each row
                    food_name = row.get('name', None)
                    food_group = row.get('Food Group', '')
                    calories = row.get('Calories', 0)
                    fat = row.get('Fat (g)', 0)
                    protein = row.get('Protein (g)', 0)
                    carbohydrate = row.get('Carbohydrate (g)', 0)
                    serving_description = row.get('Serving Description 1 (g)', '')

                    # Skip row if essential fields are missing
                    if not food_name:
                        continue

                    # Create and save a new food data entry
                    FoodData.objects.create(
                        food_name=food_name,
                        food_group=food_group,
                        calories=calories,
                        fat=fat,
                        protein=protein,
                        carbohydrate=carbohydrate,
                        serving_description=serving_description
                    )

                    self.stdout.write(f"Imported {food_name} successfully")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing row {index}: {e}"))

            self.stdout.write(self.style.SUCCESS('Food data import completed successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing food data: {e}"))

    def import_activity_data(self, excel_file):
        try:
            # Loading the Excel file containing activity data
            df = pd.read_excel(excel_file)
            self.stdout.write(f"Number of rows in Excel: {len(df)}")

            # Loop through the rows in the DataFrame and save to database
            for index, row in df.iterrows():
                try:
                    # Extractacting data from each row
                    activity_name = row.get('ACTIVITY', None)
                    specific_motion = row.get('SPECIFIC MOTION', '')
                    mets = row.get('METs', 0)

                    # Skip row if essential fields are missing
                    if not activity_name:
                        continue

                    # Create and save a new activity data entry
                    ActivityData.objects.create(
                        activity_name=activity_name,
                        specific_motion=specific_motion,
                        mets=mets
                    )

                    self.stdout.write(f"Imported {activity_name} successfully")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing row {index}: {e}"))

            self.stdout.write(self.style.SUCCESS('Activity data import completed successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing activity data: {e}"))
