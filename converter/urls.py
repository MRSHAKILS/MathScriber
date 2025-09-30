from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('results/', views.results_view, name='results'),
]
