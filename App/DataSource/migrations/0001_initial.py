# Generated by Django 3.2.6 on 2022-07-05 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Home',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estate_name', models.CharField(max_length=200, verbose_name='小区')),
                ('house_area', models.CharField(max_length=40, verbose_name='区域')),
                ('house_type', models.CharField(max_length=40, verbose_name='户型')),
                ('house_measure', models.CharField(max_length=20, verbose_name='面积')),
                ('house_orientation', models.CharField(max_length=20, verbose_name='朝向')),
                ('house_decoration', models.CharField(max_length=20, verbose_name='装修')),
                ('house_floor', models.CharField(max_length=40, verbose_name='楼层')),
                ('house_totalPrice', models.CharField(max_length=20, verbose_name='总价')),
                ('house_unitPrice', models.CharField(max_length=40, verbose_name='单价')),
                ('house_tag', models.CharField(max_length=40, verbose_name='标签')),
                ('house_code', models.CharField(max_length=20, verbose_name='编号')),
                ('house_url', models.CharField(max_length=300, verbose_name='链接')),
                ('house_name', models.CharField(max_length=100, verbose_name='标题')),
                ('city_name', models.CharField(max_length=100, verbose_name='城市')),
                ('create_time', models.DateField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
            ],
            options={
                'verbose_name': '二手房信息',
                'verbose_name_plural': '二手房信息',
                'db_table': 'home',
            },
        ),
    ]
