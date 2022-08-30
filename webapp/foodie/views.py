from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Restaurant

def index(request):
    return HttpResponse("Hello, world. You're at the foodie index.")

def restaurant_profile(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    return render(request, 'foodie/restaurant_profile.html', {'restaurant':restaurant})
    
# def list(request, list_id):
#     return HttpResponse(f"List of restaurants ({list_id})")

