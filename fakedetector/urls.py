from django.urls import path
from . import views
# urlpatterns = [
#     path('',views.prediccion,name='prediccion')
# ]
urlpatterns = [
    path('', views.prediccion.as_view()),
   
]