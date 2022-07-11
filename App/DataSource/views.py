import difflib
from django.http import HttpResponse

import requests
from bs4 import BeautifulSoup
from rest_framework.views import APIView
from requests_html import HTMLSession  # 导入HTMLSession类
from fake_useragent import UserAgent

from App.DataSource.models import Home


def string_similar(s1, s2):
    """比较字符串s1和s2的相似度"""
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def get_area(area, compare_list):
    """判断area是已知区域列表中的哪一个"""
    similarity_list = []
    for i in compare_list:
        similarity_i = string_similar(area, i)
        similarity_list.append(similarity_i)

    index = similarity_list.index(max(similarity_list))  # 获取列表中最大值的索引
    return compare_list[index]


def get_city_url():
    """获取所有城市链接"""
    url = 'https://www.lianjia.com/city'
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'lianjia_uuid=07e69a53-d612-4caa-9145-b31c2e9410f4; _smt_uid=5c2b6394.297c1ea9; UM_distinctid=168097cfb8db98-058790b6b3796c-10306653-13c680-168097cfb8e3fa; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1546347413; _ga=GA1.2.1249021892.1546347415; _gid=GA1.2.1056168444.1546347415; all-lj=c60bf575348a3bc08fb27ee73be8c666; TY_SESSION_ID=d35d074b-f4ff-47fd-9e7e-8b9500e15a82; CNZZDATA1254525948=1386572736-1546352609-https%253A%252F%252Fbj.lianjia.com%252F%7C1546363071; CNZZDATA1255633284=2122128546-1546353480-https%253A%252F%252Fbj.lianjia.com%252F%7C1546364280; CNZZDATA1255604082=1577754458-1546353327-https%253A%252F%252Fbj.lianjia.com%252F%7C1546366122; lianjia_ssid=087352e7-de3c-4505-937e-8827e808c2ee; select_city=440700; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1546391853',
        'DNT': '1',
        'Host': 'www.lianjia.com',
        'Referer': 'https://www.lianjia.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    index_response = requests.get(url=url, headers=header)
    if index_response.status_code != 200:
        print('connect index False')
    index_soup = BeautifulSoup(index_response.text, 'html.parser')
    city_url_dict = {}
    for each_province in index_soup.find_all('div', class_='city_list'):
        for each_city in each_province.find_all('li'):
            city_url_dict[each_city.get_text()] = each_city.find('a')['href']
    return city_url_dict


def get_house_info(city_url, city_name):
    """爬取二手房数据，并保存到数据库"""

    session = HTMLSession()  # 创建HTML会话对象

    # 直接生成一个列表，列表内包含该城市所有待访问的url
    page_url = [city_url, city_url + '/ershoufang'] + [city_url + '/ershoufang/pg{}/'.format(str(i)) for i in
                                                       range(2, 101)]

    for i in range(1, 101):
        # 为每一个页面构建不同的Referer信息
        # 0.1.11版本的 agent.json文件  下载地址 https://fake-useragent.herokuapp.com/browsers/0.1.11
        ua = UserAgent(path='agent.json').random  # 创建随机请求头
        index_response = session.get(url=page_url[i], headers={'user-agent': ua})

        # 需先确认传入的链接在爬虫目标网站中有二手房
        # 有些城市可能没有100页的二手房信息，因此执行完最后一页就需要跳出循环
        # 没有成功访问页面，即返回的状态码不是200，跳出循环
        if index_response.status_code != 200:
            print(city_name, 'page', str(i), 'pass')
            break
            # time.sleep(random.uniform(2, 4))

        # 解析页面
        index_soup = BeautifulSoup(index_response.text, 'html.parser')

        try:
            area_list = index_soup.find('div', class_='position').get_text().replace(' ', '').splitlines()  # 区域列表
            # 去除列表中的空值
            while '' in area_list:
                area_list.remove('')

            for each_house in index_soup.find_all('li', class_='clear LOGVIEWDATA LOGCLICKDATA'):
                house_code = each_house.find('div', class_='title').find('a')['data-housecode']  # 编号
                home_exist = Home.objects.filter(house_code=house_code)  # 查询数据库是否有记录
                # 数据库记录存在，跳过本次循环
                if home_exist.exists():
                    continue

                # 小区和区域
                estate_name = each_house.find('div', class_='positionInfo').get_text().replace(' ', '').split('-')[0]
                vague_area = each_house.find('img', class_='lj-lazy').attrs.get('alt').replace(city_name, '')  # 模糊区域
                house_area = get_area(vague_area, area_list[2:])  # 区域

                # 户型 | 面积 | 朝向 | 装修 | 楼层 | 构造，这些信息汇总
                desc_list = each_house.find('div', class_='houseInfo').get_text().replace(' ', '').split('|')
                house_type = desc_list[0]  # 户型
                house_measure = desc_list[1].replace('平米', '')  # 面积
                house_orientation = desc_list[2]  # 朝向
                house_decoration = desc_list[3]  # 装修
                house_floor = desc_list[4]  # 楼层

                total_price = each_house.find('div', class_='totalPrice').get_text()  # 总价
                unit_price = each_house.find('div', class_='unitPrice').get_text()  # 单价

                house_tag = each_house.find('div', class_='tag').get_text('/')  # 标签
                house_url = each_house.find('div', class_='title').find('a')['href']  # 链接
                house_name = each_house.find('div', class_='title').find('a').get_text()  # 标题

                # 存储数据
                home = Home(estate_name=estate_name, house_area=house_area, house_type=house_type,
                            house_measure=house_measure, house_orientation=house_orientation,
                            house_decoration=house_decoration, house_floor=house_floor,
                            total_price=total_price, unit_price=unit_price, house_tag=house_tag,
                            house_code=house_code, house_url=house_url, house_name=house_name, city_name=city_name)
                home.save()

        except Exception as e:
            print(e)
            break


class DataView(APIView):
    def get(self, request, *args, **kwargs):
        get_house_info('https://cc.lianjia.com', '长春')
        return HttpResponse('爬取数据完成！！！')
