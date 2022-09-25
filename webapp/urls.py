from django.contrib import admin
from django.urls import path
from webapp import views
urlpatterns = [
    path('home-config/', views.ScreenPageConfig.as_view()),
    path('category/', views.HomepageCategory.as_view()),
    path('packages/', views.Package.as_view()),
    path('labs/', views.Labs.as_view()),
]
