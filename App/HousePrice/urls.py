from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^bar/$', views.BarView.as_view(), name='bar'),
    url('', views.HouseView.as_view(), name='house'),
]