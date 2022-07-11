import json
import numpy
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg

from pyecharts.charts import Bar, Pie
from pyecharts import options as opts
from pyecharts.faker import Faker
from rest_framework.views import APIView

import common
from App.DataSource.models import Home

JsonResponse = common.json_response
JsonError = common.json_error


def handle_house_amount():
    region = []  # 区域
    number = []  # 数量百分比
    region_temp = list(Home.objects.values('house_area').filter(city_name='长春').distinct())
    all_count = Home.objects.filter(city_name='长春').count()
    for j in region_temp:
        region.append(j.get('house_area'))
    for i in region:
        tol = Home.objects.filter(house_area=i).count()
        percentage = tol / all_count * 100  # 计算每个区域房子数量的百分比
        number.append(percentage)
    return region, number  # 返回区域与对应的数量百分比


# 绘制饼状图
def pie_base() -> Pie:
    res = handle_house_amount()
    la = res[0]
    lb = numpy.round(res[1], 2)
    c = (
        Pie()
            .add("", [list(z) for z in zip(la, lb)])
            .set_colors(["blue", "green", "yellow", "red", "pink", "orange", "purple"])
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            .dump_options_with_quotes()
    )
    return c


class PieView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(pie_base()))


class AmountView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("App/HouseAmount/templates/house_amount.html", 'rb').read())


def get_house_number(request):
    return render(request, 'house_amount.html')
