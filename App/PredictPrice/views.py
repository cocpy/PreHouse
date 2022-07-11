import json
import numpy
import random
import pandas
from django.shortcuts import render
from django.http import HttpResponse

from pyecharts.charts import Line
from pyecharts import options as opts
from rest_framework.views import APIView
from sklearn.svm import LinearSVR  # 导入回归函数

import common
from App.DataSource.models import Home

JsonResponse = common.json_response
JsonError = common.json_error


# 获取价格预测
def handle_price_forecast():
    total_price_list = []  # 总价
    measure_list = []  # 面积
    room_list = []  # 室
    hall_list = []  # 厅
    toilet_list = []  # 卫

    temp = list(Home.objects.filter(city_name='长春'))

    for i in temp:
        total_price_list.append(float(i.total_price.replace('万', '')))
        measure_list.append(float(i.house_measure))
        room_list.append(float(i.house_type.replace('室', '').replace('厅', '')[0:1]))
        hall_list.append(float(i.house_type.replace('室', '').replace('厅', '')[1:2]))
        toilet_list.append(random.random())  # 无数据

    price_dict = {'总价': total_price_list, '建筑面积': measure_list, '室': room_list, '厅': hall_list, '卫': toilet_list}
    new_data = pandas.DataFrame(price_dict)
    print(new_data.head())  # 打印处理后的头部信息
    #  添加自定义预测数据
    new_data.loc[2505] = [None, 88.0, 2.0, 1.0, 1.0]
    new_data.loc[2506] = [None, 136.0, 3.0, 2.0, 2.0]
    data_train = new_data.loc[0:2504]
    x_list = ['建筑面积', '室', '厅', '卫']  # 自变量参考列
    data_mean = data_train.mean()  # 获取平均值
    data_std = data_train.std()  # 获取标准偏差
    data_train = (data_train - data_mean) / data_std  # 数据标准化
    x_train = data_train[x_list].values  # 特征数据
    y_train = data_train['总价'].values  # 目标数据，总价
    linearsvr = LinearSVR(C=0.1)  # 创建LinearSVR()对象
    linearsvr.fit(x_train, y_train)  # 训练模型
    x = ((new_data[x_list] - data_mean[x_list]) / data_std[x_list]).values  # 标准化特征数据
    new_data[u'y_pred'] = linearsvr.predict(x) * data_std['总价'] + data_mean['总价']  # 添加预测房价的信息列
    print('真实值与预测值分别为：\n', new_data[['总价', 'y_pred']])
    y = new_data[['总价']][2490:]  # 获取2490以后的真实总价
    y_pred = new_data[['y_pred']][2490:]  # 获取2490以后的预测总价
    return y, y_pred  # 返回真实房价与预测房价


# 绘制折线图
def line_base() -> Line:
    res = handle_price_forecast()
    la = numpy.array(res[0]).tolist()
    lb = numpy.round(numpy.array(res[1]), 1).tolist()
    c = (
        Line()
            .add_xaxis(list(range(2490, 2507, 1)))
            .add_yaxis(series_name="真实房价", y_axis=la)
            .add_yaxis(series_name="预测房价", y_axis=lb)
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="value", min_='dataMin'),
            yaxis_opts=opts.AxisOpts(type_="value")
        )
            .dump_options_with_quotes()
    )
    return c


class LineView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(line_base()))


class PredictView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("App/PredictPrice/templates/predict_price.html", 'rb').read())


def get_price_forecast(request):
    return render(request, 'predict_price.html')
