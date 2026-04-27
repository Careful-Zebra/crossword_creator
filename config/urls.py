"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from CrosswordCreator import views



urlpatterns = [
    path('admin/', admin.site.urls),
    # Changed 'puzzles.urls' to 'CrosswordCreator.urls'
    path('', include('CrosswordCreator.urls')), 
]
# urlpatterns = [
#     path("admin/", admin.site.urls),
# ]


# urlpatterns = [
#     # Player URLs
#     path('', views.enter_code, name='enter_code'),
#     path('play/<str:code>/', views.play_crossword, name='play_crossword'),

#     path('admin/', admin.site.urls),
#     path('', include('puzzles.urls')),

#     # Admin URLs
#     path('creator/new/', views.create_crossword, name='create_crossword'),
#     path('creator/<int:puzzle_id>/edit/', views.edit_crossword, name='edit_crossword'),
# ]