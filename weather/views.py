import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserDetail
from .serializers import UserDetailSerializer


# 🌦️ GET CURRENT WEATHER
@api_view(['GET'])
def get_weather(request):
    city = request.GET.get('city', 'Chennai')
    api_key = 'a223da58124f92fdeffce82f38f7db2f'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    res = requests.get(url)
    data = res.json()

    if res.status_code == 200:
        weather_info = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],  # ✅ Added humidity
            "wind_speed": data["wind"]["speed"],   # ✅ Added optional wind speed
            "description": data["weather"][0]["description"],
        }
        return Response(weather_info)
    else:
        return Response({"error": "City not found"}, status=res.status_code)


# ✅ USER LOGIN (USERNAME OR EMAIL)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username_or_email = request.data.get('username')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username_or_email, password=password)
    if user is None:
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username,
            'email': user.email
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


# 🌤️ GET 5-DAY FORECAST
@api_view(['GET'])
def get_forecast(request):
    city = request.GET.get('city', 'Chennai')
    api_key = 'a223da58124f92fdeffce82f38f7db2f'
    url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'

    res = requests.get(url)
    data = res.json()

    if res.status_code == 200:
        forecast_list = []
        for entry in data["list"]:
            forecast_list.append({
                "date": entry["dt_txt"].split(" ")[0],
                "temp": entry["main"]["temp"]
            })
        filtered_forecast = forecast_list[::8]  # One entry per day

        return Response({"forecast": filtered_forecast})
    else:
        return Response({"error": "City not found"}, status=res.status_code)


# 👥 USER DETAILS MANAGEMENT
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def user_details(request):
    if request.method == 'GET':
        users = UserDetail.objects.all()
        serializer = UserDetailSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User details saved successfully!"}, status=201)
        return Response(serializer.errors, status=400)


# ✏️ UPDATE OR DELETE USER
@api_view(['PUT', 'DELETE'])
@permission_classes([AllowAny])
def update_delete_user(request, pk):
    try:
        user = UserDetail.objects.get(pk=pk)
    except UserDetail.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully!"})
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        user.delete()
        return Response({"message": "User deleted successfully!"})

