import json
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg

from pyecharts.charts import Bar
from pyecharts import options as opts
from rest_framework.views import APIView

from App.DataSource.models import Home
import common

JsonResponse = common.json_response
JsonError = common.json_error


def handle_average_price():
    region = []  # 区域
    average_price = []  # 均价
    region_temp = list(Home.objects.values('house_area').filter(city_name='长春').distinct())
    for j in region_temp:
        region.append(j.get('house_area'))
    for i in region:
        tol = Home.objects.filter(house_area=i).aggregate(Avg('total_price'))
        avg_temp = int(tol.get('total_price__avg'))
        average_price.append(avg_temp)
    return region, average_price  # 返回区域与对应的均价


# 绘制柱状图
def bar_base() -> Bar:
    res = handle_average_price()
    la = res[0]
    lb = res[1]
    c = (
        Bar()
            .add_xaxis(la)
            .add_yaxis("均价", lb)
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                name='区域',
                name_location='middle',
                name_gap=35,
                offset=5,
                name_textstyle_opts=opts.TextStyleOpts(
                    color='black',
                    font_style='italic',
                    font_weight='bolder',
                    font_family='monospace',
                    font_size=20
                )
            )
        )
            .dump_options_with_quotes()
    )
    return c


class BarView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))


class HouseView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("App/HousePrice/templates/house_price.html", 'rb').read())


def get_average_price(request):
    return render(request, 'house_price.html')
