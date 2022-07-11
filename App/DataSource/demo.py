from requests_html import HTMLSession # 导入HTMLSession类
from requests_html import UserAgent   # 导入UserAgent类
from requests_html import HTML        # 导入HTML类
import pandas as pd# 导入pandas模块
import matplotlib  # 导入图表模块
import matplotlib.pyplot as plt # 导入绘图模块
# 避免中文乱码
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
from multiprocessing import Pool     # 导入进程池
# 分类列表，作为数据表中的列名
class_name_list = ['小区名字', '总价', '户型', '建筑面积', '单价', '区域']
# 创建DataFrame临时表格
df = pd.DataFrame(columns=class_name_list)

def menu():
    # 输出菜单
    print('''
    ╔——————可视化二手房数据查询系统—————╗
    │                                              │
    │   =============== 功能菜单 ===============│
    │                                              │
    │   1 爬取最新二手房数据                       │
    │   2 查看各区二手房数量比例                   │
    │   3 查看各区二手房均价                       │
    │   4 查看热门户型均价                         │
    │   0 退出系统                                 │
    │==========================================│
    ╚———————————————————————╝
    ''')

def main():
    ctrl = True  # 标记是否退出系统
    while (ctrl):
        menu()  # 显示菜单
        option = input("请选择：")  # 选择菜单项
        if option in ['0', '1', '2', '3', '4']:
            option_int = int(option)
            if option_int == 0:  # 退出系统
                print('退出可视化二手房数据查询系统！')
                ctrl = False
            elif option_int == 1:  # 爬取最新二手房数据
                print('爬取最新二手房数据')
                start_crawler()      # 启动多进程爬虫
                print('二手房数据爬取完毕！')
            elif option_int == 2:  # 查看各区房子数量比例
                print('查看各区房子数量比例')
                show_house_number()
            elif option_int == 3:  # 查看各区二手房均价
                print('查看各区二手房均价')
                show_average_price()
            elif option_int == 4:  # 查看热门户型均价
                print('查看热门户型均价')
                show_type()
        else:
            print('请输入正确的功能选项！')
# 启动爬虫
def start_crawler():
    df.to_csv("二手房数据.csv", encoding='utf_8_sig')  # 第一次生成带表头的空文件
    url = 'https://cc.lianjia.com/ershoufang/pg{}/'
    urls = [url.format(str(i)) for i in range(1, 101)]
    pool = Pool(processes=4)  # 创建4进程对象
    pool.map(get_house_info, urls)
    pool.close()  # 关闭进程池

def get_house_info(url):
    session = HTMLSession()  # 创建HTML会话对象
    ua = UserAgent().random  # 创建随机请求头
    response = session.get(url, headers={'user-agent': ua})  # 发送网络请求
    if response.status_code == 200:  # 判断请求是否成功
        html = HTML(html=response.text)  # 解析HTML
        li_all = html.find('.sellListContent li')  # 获取每页所有房子信息
        for li in li_all:
            name = li.xpath('//div[1]/div[2]/div/a[1]/text()')[0].strip()# 获取小区名称
            # 获取房子总价
            total_price = li.xpath('//div[1]/div[6]/div[1]/span/text()')[0] + '万'
            region = li.xpath('//div[1]/div[2]/div/a[2]/text()')[0]  # 获取房子区域
            unit_price = li.xpath('//div[1]/div[6]/div[2]/span/text()')[0]# 获取房子单价
            house_info = li.xpath('//div[1]/div[3]/div/text()')[0]  # 获取房子详细信息
            house_list = house_info.split('|')  # 使用|分割房子详细信息
            type = house_list[0].strip()  # 获取房子户型
            dimensions = house_list[1].strip()  # 获取房子面积
            # '小区名字', '总价', '户型', '建筑面积', '单价', '区域'
            print(name,total_price,type,dimensions,unit_price,region)
            # 将数据信息添加至DataFrame临时表格中
            df.loc[len(df) + 1] = {'小区名字': name, '总价': total_price, '户型': type,
                                   '建筑面积': dimensions, '单价': unit_price, '区域': region}
        # 将数据以添加模式写入csv文件当中，不再添加头部列
        df.to_csv("二手房数据.csv",  mode='a', header=False)
    else:
        print(response.status_code)

# 清洗数据
def cleaning_data():
    data = pd.read_csv('二手房数据.csv')  # 读取csv数据文件
    del data['Unnamed: 0']  # 将索引列删除
    data.dropna(axis=0, how='any', inplace=True)  # 删除data数据中的所有空值
    data = data.drop_duplicates()                 # 删除重复数据
    # 将单价“元/平米”去掉
    data['单价'] = data['单价'].map(lambda d: d.replace('元/平米', ''))
    data['单价'] = data['单价'].map(lambda d: d.replace('单价', ''))# 将单价“元/平米”去掉
    data['单价'] = data['单价'].astype(float)  # 将房子单价转换为浮点类型
    return data

# 显示各区二手房数量所占比例
def show_house_number():
    data = cleaning_data()                      # 获取清洗后的数据
    group_number = data.groupby('区域').size()  # 房子区域分组数量
    region = group_number.index  # 区域
    numbers = group_number.values  # 获取每个区域内房子出售的数量
    percentage = numbers / numbers.sum() * 100  # 计算每个区域房子数量的百分比
    plt.figure()                         # 图形画布
    plt.pie(percentage, labels=region,labeldistance=1.05,
            autopct="%1.1f%%", shadow=True, startangle=0, pctdistance=0.6)
    plt.axis("equal")  # 设置横轴和纵轴大小相等，这样饼才是圆的
    plt.title('各区二手房数量所占比例', fontsize=12)
    plt.show()    # 显示饼图

# 显示各区二手房均价图
def show_average_price():
    data = cleaning_data()        # 获取清洗后的数据
    group = data.groupby('区域')  # 将房子区域分组
    average_price_group = group['单价'].mean()  # 计算每个区域的均价
    region = average_price_group.index  # 区域
    average_price = average_price_group.values.astype(int) # 区域对应的均价
    plt.figure()  # 图形画布
    plt.bar(region,average_price, alpha=0.8)  # 绘制柱形图
    plt.xlabel("区域")  # 区域文字
    plt.ylabel("均价")  # 均价文字
    plt.title('各区二手房均价')  # 表标题文字
    # 为每一个图形加数值标签
    for x, y in enumerate(average_price):
        plt.text(x, y + 100, y, ha='center')
    plt.show()  # 显示图表

# 显示热门户型均价图
def show_type():
    data = cleaning_data()  # 获取清洗后的数据
    house_type_number = data.groupby('户型').size()  # 房子户型分组数量
    sort_values = house_type_number.sort_values(ascending=False)# 将户型分组数量进行降序
    top_five = sort_values.head(5)  # 提取前5组户型数据
    house_type_mean = data.groupby('户型')['单价'].mean()  # 计算每个户型的均价
    type = house_type_mean[top_five.index].index  # 户型
    price = house_type_mean[top_five.index].values  # 户型对应的均价
    price = price.astype(int)
    plt.figure()  # 图形画布
    plt.barh(type, price, height=0.3, color='r', alpha=0.8)  # 从下往上画水平柱形图
    plt.xlim(0, 15000)  # X轴的均价0~15000
    plt.xlabel("均价")  # 均价文字
    plt.title("热门户型均价")  # 表标题文字
    # 为每一个图形加数值标签
    for y, x in enumerate(price):
        plt.text(x + 10, y, str(x) + '元', va='center')
    plt.show()  # 显示图表

if __name__ == '__main__':   # 创建程序入口
    main()                   # 调用自定义main()方法
