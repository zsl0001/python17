# from pyecharts import Line
# columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# # 设置数据
# data1 = [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]
# data2 = [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
# line = Line("折线图","一年的降水量与蒸发量")
# # is_label_show是设置上方数据是否显示
# line.add("降水量", columns, data1, is_label_show=True)
# line.add("蒸发量", columns, data2, is_label_show=True)
# line.render()

# import pyecharts.options as opts
# from pyecharts.charts import Line
# from pyecharts.faker import Faker
#
# c = (
#     Line()
#     .add_xaxis(Faker.choose())
#     .add_yaxis(
#         "商家A",
#         Faker.values(),
#         markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="min")]),
#     )
#     .add_yaxis(
#         "商家B",
#         Faker.values(),
#         markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
#     )
#     .set_global_opts(title_opts=opts.TitleOpts(title="Line-MarkPoint"))
#     .render("line_markpoint.html")
# )
from pyecharts.faker import Faker
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, SymbolType
import pandas as pd
import json


def add_adress_json() -> Geo:
    # http://api.map.baidu.com/geocoder?key=f247cdb592eb43ebac6ccd27f796e2d2&output=json&address=
    test_data_ = [("测试点1", 116.512885, 39.847469), ("测试点2", 125.155373, 42.933308), ("测试点3", 87.416029, 43.477086)]
    count = [1000, 2000, 500]
    address_ = []
    json_data = {}
    for ss in range(len(test_data_)):
        json_data[test_data_[ss][0]] = [test_data_[ss][1], test_data_[ss][2]]
        address_.append(test_data_[ss][0])

    json_str = json.dumps(json_data, ensure_ascii=False, indent=4)
    with open('test_data.json', 'w', encoding='utf-8') as json_file:
        json_file.write(json_str)

    c = (
        Geo()
            .add_schema(maptype="world")  # 可以换成 world,或 china
            .add_coordinate_json(json_file='test_data.json')  # 加入自定义的点
            # 为自定义的点添加属性
            .add("", data_pair=[list(z) for z in zip(address_, count)], symbol_size=30, large_threshold=2000,
                 symbol="pin")
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(visualmap_opts=opts.VisualMapOpts(max_=2000),
                             title_opts=opts.TitleOpts(title="json加入多个坐标"))
    )
    return c


if __name__ == '__main__':
    add_json = add_adress_json()
    add_json.render(path="test_json.html")