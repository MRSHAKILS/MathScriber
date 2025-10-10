from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('stylus/', views.stylus_view, name='stylus'),
    path('results/', views.results_view, name='results'),
    path('delete/<int:upload_id>/', views.delete_upload_view, name='delete_upload'),
]
