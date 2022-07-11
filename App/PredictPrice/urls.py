from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^line/$', views.LineView.as_view(), name='line'),
    url('', views.PredictView.as_view(), name='predict'),
]