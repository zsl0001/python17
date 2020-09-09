from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random


class VercCode():
    random_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345789'
    width = 107
    height = 43

    @classmethod
    def generate_vercode(cls):
        # 创建一个新的图像, 设置长宽和背景颜色
        img = Image.new('RGB', (cls.width, cls.height), "#f1f0f0")
        font = ImageFont.truetype('msyhbd.ttc', 30)
        draw = ImageDraw.Draw(img)
        vercode = ""
        # 生成随机验证码,并将验证码转成图像打印到图像
        for item in range(4):
            code = random.choice(cls.random_letters)
            vercode += code
            draw.text((6 + random.randint(1, 2) + 23 * item, 2), text=code, fill=cls.__random_color(), font=font)
        # 画几条随机线,让验证码看起来更专业
        for x in range(4):
            x1 = random.randint(0, cls.width // 2)
            y1 = random.randint(0, cls.height // 2)
            x2 = random.randint(0, cls.width)
            y2 = random.randint(cls.height // 2, cls.height)
            draw.line(((x1, y1), (x2, y2)), fill=cls.__random_color(), width=2)
        # 加上一层滤波器滤镜
        img = img.filter(ImageFilter.EDGE_ENHANCE)
        return img, vercode.lower()

    @classmethod
    def __random_color(cls):
        # 随机生成一个RGB颜色值
        return tuple([random.randint(64, 180) for _ in range(3)])
