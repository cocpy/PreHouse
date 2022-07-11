from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^lar/$', views.LarView.as_view(), name='lar'),
    url('', views.HotView.as_view(), name='hot'),
]
