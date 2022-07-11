from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^pie/$', views.PieView.as_view(), name='pie'),
    url('', views.AmountView.as_view(), name='amount'),
]
