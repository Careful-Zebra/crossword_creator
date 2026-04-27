# CrosswordCreator/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Player URLs
    path('', views.home, name='home'),
    path('play/<str:code>/', views.play_crossword, name='play_crossword'),
    path('enter_code/', views.enter_code, name='enter_code'),
    
    # Admin URLs
    path('creator/new/', views.create_crossword, name='create_crossword'),
    path('creator/<int:puzzle_id>/edit/', views.edit_crossword, name='edit_crossword'),
]