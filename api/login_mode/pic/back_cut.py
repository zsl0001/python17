import os
from PIL import Image, ImageEnhance, ImageDraw
from io import BytesIO
import base64
import random
import uuid
import redis
from api_preceipt.myconfig import my_redis

# 普通连接
redis_conn = redis.Redis(host=my_redis['host'], port=my_redis['port'], db=my_redis['db'],password=my_redis['password'])


# conn.set("x1", "hello", ex=5)  # ex代表seconds，px代表ms
# val = conn.get("x1")
# print(val)


def isint(self, *args):
    for nb in args:
        try:
            int(nb)
        except Exception as e:
            return {False, nb}
    return {True, ''}


imgpath = os.path.join(os.path.dirname(__file__), 'silder_img')
uid = str(uuid.uuid1()).replace("-", "")


# 获取滑动认证的图片
def getAuthImage(redis_c=redis_conn, uid=uid):
    if os.path.isdir(imgpath) is False:
        return {'code': False, 'res': '{} 不存在'.format(imgpath)}

    img_list = os.listdir(imgpath)
    if img_list:
        random_img = img_list[random.randint(0, (len(img_list) - 1) - 1)]
        imgscr = os.path.join(imgpath, random_img)
    else:
        return {'code': False, 'res': '{} 不存在'.format(imgpath)}
    image = Image.open(imgscr)
    width = image.size[0]
    height = image.size[1]
    if width != 355 or height != 200:
        return {'code': False, 'res': '图片尺寸:355/200'.format(imgscr)}
    x = random.randint(40, 290)
    y = random.randint(40, 160)
    w = x + 40
    h = y + 40
    coordinate = (x, y, w, h)
    draw = ImageDraw.Draw(image)
    draw.rectangle((x, y, w+1, h+1), outline="black", width=1)
    region = image.crop(coordinate)  # .point(lambda p: p * 50)
    region = ImageEnhance.Contrast(region).enhance(1.0)  # 对比度增强
    region2 = ImageEnhance.Brightness(region).enhance(0.3)  # 亮度增强
    buffered = BytesIO()
    region.save(buffered, format="PNG")
    img_paste = base64.b64encode(buffered.getvalue()).decode()
    buffered.close()
    image.paste(region2, (x, y))
    buffered2 = BytesIO()
    image.save(buffered2, format="PNG")
    img_bg = base64.b64encode(buffered2.getvalue()).decode()
    buffered2.close()

    my_redis = redis_conn

    # 背景图片 ''
    my_redis.set("%s_bg_img" % uid, img_bg, 60 * 3)
    # 可移动图片
    my_redis.set("%s_move_img" % uid, img_paste, 60 * 3)
    # 可移动图片x，y坐标
    my_redis.set("%s_move_xy" % uid, '%s,%s' % (x, y), 60 * 3)
    # print("%s_move_xy" % uid, '%s,%s' % (x, y))
    # 认证失败次数
    my_redis.set("%s_img_error_count" % uid, 0, 60 * 3)

    data = [{'bg_img': img_bg},
            {'move_img': img_paste},
            ]
    return {'code': True, 'datalist': data, 'uid': uid, 'move_y': y}


# 认证图片是否移动到指定位置
def AuthImage(uid, move_x, move_y, redis_c=redis_conn):
    print(uid, move_x, move_y)
    isint_ret = isint(move_x, move_y)
    if list(isint_ret)[0] is False:
        describe = 'The "%s" data type is int' % (isint_ret[1])
        return {'code': False, 'res': describe, 'status_code': -10001}
    # 获取x,y坐标
    my_redis = redis_conn
    r_xy = my_redis.get("%s_move_xy" % uid)
    if r_xy:
        r_xy_list = r_xy.decode().split(',')
        r_x = r_xy_list[0]
        r_y = r_xy_list[1]
        if abs(int(r_x) - int(move_x)) <= 10 and abs(int(r_y) - int(move_y)) <= 10:
            my_redis.delete("%s_bg_img" % uid)
            my_redis.delete("%s_move_img" % uid)
            my_redis.delete("%s_move_xy" % uid)
            my_redis.delete("%s_img_error_count" % uid)
            random_str = str(uuid.uuid1()).replace('-', '')
            my_redis.set("%s" % uid, 'True', 60 * 3)
            return {'code': True, 'res': '认证成功！', 'status_code': 10001}
        else:
            error_count = my_redis.get("%s_img_error_count" % uid)
            if error_count:
                error_count = int(error_count.decode())
                new_count = error_count + 1
                if new_count > 5:
                    describe = '尝试次数过多!请刷新图片重试！'
                    my_redis.delete("%s_bg_img" % uid)
                    my_redis.delete("%s_move_img" % uid)
                    my_redis.delete("%s_move_xy" % uid)
                    my_redis.delete("%s_img_error_count" % uid)
                    return {'code': False, 'res': describe, 'uid': uid, 'status_code': -20001}
                else:
                    my_redis.set("%s_img_error_count" % uid, new_count, 30)
                describe = '认证失败!'
                return {'code': False, 'res': describe, 'status_code': -10001}
            else:
                describe = '认证失败!'
                return {'code': False, 'res': describe, 'status_code': -10001}
    else:
        describe = '认证失败!'
        return {'code': False, 'res': describe, 'status_code': -10001}


def get_redis_res(uid):
    my_redis = redis_conn
    res = my_redis.get("%s" % uid)
    if res:
        s2 = bytes.decode(res)
        return s2
    else:
        return None


# None
# a = get_redis_res(uid='8d092fd2959211eab6361831bf501dcb')
# print(a)
a = getAuthImage()
# a1 = a['datalist'][0]['bg_img']
# a2 = a['datalist'][1]['move_img']
# print(a1)
# print(a2)
# a1 = base64.b64decode(a1)
# a2 = base64.b64decode(a2)
# print(a1)
# print(a2)
# file = open(r'D:\PycharmProjects\python17\api_preceipt\api\login_mode\pic\silder_img\3.jpg', 'wb')
# file.write(a1)
# file = open(r'D:\PycharmProjects\python17\api_preceipt\api\login_mode\pic\silder_img\4.jpg', 'wb')
# file.write(a2)
# file.close()
# b = AuthImage(uid='a57078f4-94f7-11ea-8953-1831bf501dcb', move_x=194, move_y=67)
# print(b)
