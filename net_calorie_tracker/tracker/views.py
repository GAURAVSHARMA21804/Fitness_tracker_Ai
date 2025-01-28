# user and admin pages views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Case, When, Value, CharField
from .models import CustomUser,FoodData,DailyFoodLog,MealType,ActivityData,DailyActivityLog,DailySummary
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

#home page view logic
def home(request):
    return render(request, 'tracker/home.html')

# user daily log dashboard page viewlogic
@login_required
def user_daily_logs_dashboard(request):
    return render(request, 'tracker/user_dailylogs_dashboard.html')

#admin dashboard page view logic
@login_required
def admin_dashboard(request):
    try:
        if request.user.is_staff:
            users = CustomUser.objects.filter(is_staff=False)  
            print(users)
            return render(request, 'tracker/admin_panel_dashboard.html', {'users': users})
    except Exception as e:
        logger.error(f"Error in admin_dashboard: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)    

# user dashboard view logic
@login_required
def user_dashboard(request):
    try:
        user_id = request.GET.get('user_id')
        print(f"User ID: {user_id}")  # Debugging line to check the user_id
        if user_id:
            daily_logs = DailySummary.objects.filter(user_id=user_id)
        else:
            daily_logs = DailySummary.objects.all()

        return render(request, 'tracker/user_dashboard.html', {'daily_logs': daily_logs})
    except Exception as e:
        logger.error(f"Error in user_dashboard: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)


# search food from activity data view logic
@login_required
def search_food(request):
    try:
        query = request.GET.get('query', '').strip()
        if query:
            from django.db.models import Case, When, Value, CharField
            foods = FoodData.objects.filter(food_name__icontains=query).annotate(
                priority=Case(
                    When(food_name__istartswith=query, then=Value(1)),
                    default=Value(0),
                    output_field=CharField()
                )
            ).order_by('-priority', 'food_name').values('food_id', 'food_name', 'food_group')
            
            food_list = list(foods)
            return JsonResponse({'foods': food_list})
        return JsonResponse({'foods': []})
    except Exception as e:
        logger.error(f"Error in search_food: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)
    
# save food log of a user view logic
@login_required
def save_food_log(request):
    try:
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                date = data.get('date')
                food_id = data.get('food_item')
                meal_type = data.get('meal_type')
                serving_count = data.get('serving_count')

                
                if not date or not food_id or not meal_type or not serving_count:
                    return JsonResponse({"error": "Missing required fields"}, status=400)

                
                try:
                    serving_count = float(serving_count)
                except ValueError:
                    return JsonResponse({"error": "Invalid serving count"}, status=400)

                
                try:
                    food_item = FoodData.objects.get(food_id=food_id)
                except FoodData.DoesNotExist:
                    return JsonResponse({"error": "Food item not found"}, status=400)

                
                try:
                    meal_type_obj = MealType.objects.get(name=meal_type)
                except MealType.DoesNotExist:
                    return JsonResponse({"error": "Meal type not found"}, status=400)

                try:
                    food_date = datetime.strptime(date, '%Y-%m-%d').date()  
                except ValueError:
                    return JsonResponse({"error": "Invalid date format"}, status=400)

                # Create a new DailyFoodLog entry
                daily_food_log = DailyFoodLog(
                    user=request.user, 
                    date=food_date,
                    food_item=food_item,
                    meal_type=meal_type_obj,
                    serving_count=serving_count,
                )

            
                try:
                    food_item_calories = float(food_item.calories)  # Make sure it's a float
                except ValueError:
                    return JsonResponse({"error": "Invalid calories value"}, status=400)

                daily_food_log.total_calories = serving_count * food_item_calories

                daily_food_log.save()

                
                return JsonResponse({"message": "Food log added successfully!"})

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    except Exception as e:
        logger.error(f"Error in save_food_log: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)



# search activity from activity data view logic
@login_required
def search_activity(request):
    try:
        query = request.GET.get('query', '').strip()
        if query:
            activities = ActivityData.objects.filter(activity_name__icontains=query).annotate(
                priority=Case(
                    When(activity_name__istartswith=query, then=Value(1)),
                    default=Value(0),
                    output_field=CharField()
                )
            ).order_by('-priority', 'activity_name').values('activity_id', 'activity_name', 'specific_motion', 'mets')
            
            activity_list = list(activities)
            return JsonResponse({'activities': activity_list})
        return JsonResponse({'activities': []})
    except Exception as e:
        logger.error(f"Error in search_activity: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)
    
# save activity log of a user view logic
@login_required
def save_activity_log(request):
    try:
        if request.method == "POST":
            try:
                
                data = json.loads(request.body)

                
                date = data.get('date')
                activity_id = data.get('activity_id')
                duration_minutes = data.get('duration_minutes')
                description = data.get('description', '')

                # Validate the required fields
                if not date or not activity_id or not duration_minutes:
                    return JsonResponse({"error": "Missing required fields"}, status=400)

                
                try:
                    duration_minutes = int(duration_minutes)
                    if duration_minutes <= 0:
                        return JsonResponse({"error": "Duration must be greater than zero"}, status=400)
                except ValueError:
                    return JsonResponse({"error": "Invalid duration value"}, status=400)

                
                try:
                    activity_item = ActivityData.objects.get(activity_id=activity_id)
                except ActivityData.DoesNotExist:
                    return JsonResponse({"error": "Activity not found"}, status=400)

                
                try:
                    activity_date = parse_date(date)  
                    if not activity_date:
                        raise ValueError("Invalid date format")
                except ValueError:
                    return JsonResponse({"error": "Invalid date format"}, status=400)

                # Create a new DailyActivityLog entry
                daily_activity_log = DailyActivityLog(
                    user=request.user,  
                    date=activity_date,
                    activity=activity_item,
                    duration_minutes=duration_minutes,
                    description=description,
                )

                
                daily_activity_log.save()

                
                return JsonResponse({"message": "Activity log added successfully!"})

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

        return JsonResponse({"error": "Invalid request method"}, status=400)
    except Exception as e:
        logger.error(f"Error in save_activity: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)

# get daily food and activity logs for a user view logic
@login_required
def get_logs(request):
    try:
        date = request.GET.get("date")
        print(f"Selected date: {date}")  
        if not date:
            return JsonResponse({"error": "Date is required"}, status=400)

        print(f"User: {request.user}")  
        food_logs = DailyFoodLog.objects.filter(user=request.user, date=date)
        activity_logs = DailyActivityLog.objects.filter(user=request.user, date=date)
        
        daily_summary = DailySummary.objects.filter(user=request.user, date=date).first()
        print (f"Daily summary: {daily_summary}") 

        print(f"Food logs count: {food_logs.count()}") 
        print(f"Activity logs count: {activity_logs.count()}")  
        
        if daily_summary:
            print(f"BMR: {daily_summary.bmr}")
            print(f"Calories In: {daily_summary.calories_in}")
            print(f"Calories Out: {daily_summary.calories_out}")
            print(f"Net Calories: {daily_summary.net_calories}")
        else:
            print("No daily summary found.")
        
        print(f"Food logs count: {food_logs.count()}")  
        print(f"Activity logs count: {activity_logs.count()}")  
        for log in food_logs:
            print(f"Food Log ID: {log.id}, Food Name: {log.food_item.food_name}")
        food_logs_data = [
            {
                "date": log.date.strftime("%Y-%m-%d"),
                "id": log.id,
                "food_name": log.food_item.food_name,
                "meal_type": log.meal_type.name,
                "food_group": log.food_item.food_group,
                "serving_count": log.serving_count,
                "total_calories": log.total_calories,
            }
            for log in food_logs
        ]

        activity_logs_data = [
            {
                "date": log.date.strftime("%Y-%m-%d"),
                "id": log.id,
                "activity_name": log.activity.activity_name,
                "description": log.description,
                "duration_minutes": log.duration_minutes,
                "calories_burned": log.calories_burned,
            }
            for log in activity_logs
        ]
        
        # Prepare summary data if it exists
        summary_data = {
            "bmr": daily_summary.bmr if daily_summary and daily_summary.bmr is not None else "-",
            "calories_in": daily_summary.calories_in if daily_summary and daily_summary.calories_in is not None else "-",
            "calories_out": daily_summary.calories_out if daily_summary and daily_summary.calories_out is not None else "-",
            "net_calories": daily_summary.net_calories if daily_summary and daily_summary.net_calories is not None else "-",
        }
        
        print("Returning response")  
        
        return JsonResponse({
            "food_logs": food_logs_data,
            "activity_logs": activity_logs_data,
            "summary": summary_data,
        })
    except Exception as e:
        logger.error(f"Error in search_activity: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)




# delete food log of user view logic
@login_required
@require_http_methods(["DELETE"])
def delete_food_log(request, log_id):
    try:
        food_log = DailyFoodLog.objects.get(id=log_id)
        food_log.delete()
        return JsonResponse({'message': 'Food log deleted successfully'})
    except DailyFoodLog.DoesNotExist:
        return JsonResponse({'error': 'Food log not found'}, status=404)


# delete activiy log of user view logic    
@require_http_methods(["DELETE"])
def delete_activity_log(request, log_id):
   try:
       activity_log = DailyActivityLog.objects.get(id=log_id)
       activity_log.delete()
       return JsonResponse({'message': 'Activity log deleted successfully'})
   except DailyActivityLog.DoesNotExist:
       return JsonResponse({'error': 'Activity log not found'}, status=404)
   

# daily summery of user view logic
@login_required
def get_daily_summaries(request):
    try:
        date = request.GET.get('date')  
        user_id = request.user.id
        
        if date:
            summaries = DailySummary.objects.filter(user_id=user_id,date=date)  
        else:
            summaries = DailySummary.objects.filter(user_id=user_id).order_by('-date')  
        
        data = {
            'summaries': [
                {
                    'date': summary.date,
                    'bmr': summary.bmr,
                    'calories_in': summary.calories_in,
                    'calories_out': summary.calories_out,
                    'net_calories': summary.net_calories,
                }
                for summary in summaries
            ]
            
        }

        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error in get_daily_summeries: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)


# daily summary of user for admin view logic
def daily_summery_for_admin(request, user_id):
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        filter_date = request.GET.get('date')
        if filter_date:
            summaries = DailySummary.objects.filter(user=user, date=filter_date)
        else:
            summaries = DailySummary.objects.filter(user=user).order_by('-date')
        
        context = {
            'user': user,
            'summaries': summaries,
        }
        return render(request, 'tracker/users_daily_logsdetails.html', context)
    except Exception as e:
        logger.error(f"Error in daily_summery_for_admin: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)


# daily logs of food and acitivty for admin view logic
def daily_logs(request, user_id, selected_date=None):
    try:
    
        user = get_object_or_404(CustomUser, id=user_id)
        if selected_date is None:
            selected_date_str = request.GET.get('date', None)
            if selected_date_str:
                try:
                    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                except ValueError:
                    selected_date = datetime.today().date()  # Default to today if invalid date format
            else:
                selected_date = datetime.today().date()

        # Fetch data using the selected date
        food_logs = DailyFoodLog.objects.filter(user=user, date=selected_date)
        activity_logs = DailyActivityLog.objects.filter(user=user, date=selected_date)
        daily_summary = DailySummary.objects.filter(user=user, date=selected_date).first()

        context = {
            'user': user,
            'selected_date': selected_date,
            'food_logs': food_logs,
            'activity_logs': activity_logs,
            'daily_summary': daily_summary,
        }

        return render(request, 'tracker/users_foodactivitylogs_details.html', context)
    except Exception as e:
        logger.error(f"Error in daily logs: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)

