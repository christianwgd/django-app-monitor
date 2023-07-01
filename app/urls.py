from django.urls import path

from app import views

app_name = 'app'


urlpatterns = [
    path('', views.AppList.as_view(), name='list'),
    path('detail/<int:pk>/', views.AppDetail.as_view(), name='detail'),
    path('update/<int:app_id>/', views.instant_update, name='update'),
    path('update-all/', views.instant_update_all, name='update-all'),
]
