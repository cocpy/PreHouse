import json
from django.shortcuts import render
from django.http import HttpResponse

from pyecharts.charts import Bar
from pyecharts import options as opts
from rest_framework.views import APIView

import common
from App.DataSource.models import Home

JsonResponse = common.json_response
JsonError = common.json_error


# 获取全市二手房装修程度对比
def handle_renovation():
    renovation_type = []  # 装修类型
    renovation_number = []  # 各类型对应的数量
    type_temp = list(Home.objects.values('house_decoration').filter(city_name='长春').distinct())
    # all_count = Home.objects.filter(city_name='长春').count()
    for j in type_temp:
        renovation_type.append(j.get('house_decoration'))
    for i in renovation_type:
        tol = Home.objects.filter(house_decoration=i).count()
        renovation_number.append(tol)

    return renovation_type, renovation_number  # 返回装修程度与对应的数量


# 绘制柱状图
def ren_base() -> Bar:
    res = handle_renovation()
    la = res[0]
    lb = res[1]
    c = (
        Bar()
            .add_xaxis(la)
            .add_yaxis("数量", lb)
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                name='装修类型',
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


class RenView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(ren_base()))


class RenoView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("App/Renovation/templates/renovation.html", 'rb').read())


def get_renovation(request):
    return render(request, 'renovation.html')
