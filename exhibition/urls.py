from django.urls import path
from . import views

urlpatterns = [
    path('exhibition/list/', views.get_exhibition_list, name='get_exhibition_list'),
    path('exhibition/detail/<int:exhibition_id>/', views.get_exhibition_detail, name='get_exhibition_detail'),
]