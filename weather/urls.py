from django.urls import path
from .views import get_weather, login_user, get_forecast, user_details, update_delete_user

urlpatterns = [
    path('weather/', get_weather),
    path('forecast/', get_forecast),
    path('login/', login_user),
    path('userdetails/', user_details),
    path('userdetails/<int:pk>/', update_delete_user),
]




