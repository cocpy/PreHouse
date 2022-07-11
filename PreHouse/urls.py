"""PreHouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from App.Index.views import index
from App.HotPrice.views import get_house_type
from App.HousePrice.views import get_average_price
from App.HouseAmount.views import get_house_number
from App.PredictPrice.views import get_price_forecast
from App.Renovation.views import get_renovation

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('data/', get_data_source, name='data'),
    url(r'^data/', include('App.DataSource.urls')),
    # path('hot/', get_house_type, name='hot'),
    url(r'^hot/', include('App.HotPrice.urls')),
    # path('house/', get_average_price, name='house'),
    url(r'^house/', include('App.HousePrice.urls')),
    # path('amount/', get_house_number, name='amount'),
    url(r'^amount/', include('App.HouseAmount.urls')),
    # path('predict/', get_price_forecast, name='predict'),
    url(r'^predict/', include('App.PredictPrice.urls')),
    # path('reno/', get_renovation, name='reno'),
    url(r'^reno/', include('App.Renovation.urls')),
    path('', index),
]
