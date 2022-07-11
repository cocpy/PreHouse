import json
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg
from django.db.models import Count

import numpy as np
from pyecharts.charts import Bar
from pyecharts import options as opts
from rest_framework.views import APIView

import common
from App.DataSource.models import Home

JsonResponse = common.json_response
JsonError = common.json_error


# 获取二手房热门户型均价
def handle_house_type():
    house_type = []  # 户型
    hot_price = []  # 均价
    house_number = []  # 户型数量
    ue_type = []
    house_temp = list(
        Home.objects.values('house_type').filter(city_name='长春').annotate(dcount=Count('house_type')).distinct())
    for j in house_temp:
        house_type.append(j.get('house_type'))
        house_number.append(j.get('dcount'))

    xx = np.asarray(house_number)
    top_idx = list(xx.argsort()[-1:-6:-1])

    if len(house_type) > 5:
        for k in top_idx:
            ue_type.append(house_type[k])
        house_type = ue_type  # 取前5条数据

    hot_type = house_type  # 热门户型
    for i in hot_type:
        tol = Home.objects.filter(house_type=i).aggregate(Avg('total_price'))
        avg_temp = int(tol.get('total_price__avg'))
        hot_price.append(avg_temp)
    return hot_type, hot_price  # 返回户型与均价


# 绘制柱状图
def lar_base() -> Bar:
    res = handle_house_type()
    la = res[0]
    lb = res[1]
    c = (
        Bar()
            .add_xaxis(la)
            .add_yaxis("均价", lb)
            .reversal_axis()
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                name='户型',
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


class LarView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(lar_base()))


class HotView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("App/HotPrice/templates/hot_price.html", 'rb').read())


def get_house_type(request):
    return render(request, 'hot_price.html')
