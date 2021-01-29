import sys

from mongoengine import Q

sys.path.append("..")
import pyecharts.options as opts
from pyecharts.charts import Line

#  绘制电量曲线
import datetime

from my_db.Models import Log


def get_Utc_time(t):
    a = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    o = datetime.timedelta(hours=8)
    return a - o


s_time = '2020-12-24 00:00:00'
s_time = datetime.datetime.strptime(s_time, "%Y-%m-%d %H:%M:%S")
n_time = datetime.datetime.now()
print(s_time)
print(n_time)
l = []
l2=[]
while s_time <= n_time:
    l_time = datetime.timedelta(hours=2)
    s_time = s_time + l_time
    if s_time <=n_time:
        l.append(get_Utc_time(str(s_time)))
        l2.append(s_time)
    else:
        l.append(get_Utc_time(str(n_time).split('.')[0]))
        l2.append(str(n_time).split('.')[0])
imei = '351608087068594'
m = []
for i in l:
    res = Log.objects.filter((Q(time__gte=i) & Q(imei=imei))).order_by('time').first()
    print(i)
    if res:
        y_data = str(res.content).split(',')[2]
        print(y_data)
        m.append(y_data)
if len(m) != len(l):
    l = l[0:len(m)]
print(len(m))
c = (
    Line(init_opts=opts.InitOpts(width="1500px"))
        .add_xaxis(l2)
        .add_yaxis("351608087068594", y_axis=m, is_smooth=True)
        .set_global_opts(
        #
        tooltip_opts=opts.TooltipOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts={"interval": "1"}
        ),
        yaxis_opts=opts.AxisOpts(
            # 分割线配置，显示 y 轴每个刻度的分割线
            splitline_opts=opts.SplitLineOpts(is_show=True),
        )
    )
        .render("m.html")
)
