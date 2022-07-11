from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ren/$', views.RenView.as_view(), name='ren'),
    url('', views.RenoView.as_view(), name='reno'),
]