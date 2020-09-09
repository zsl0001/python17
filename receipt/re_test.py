#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 正则表达式的使用
import re
import requests

# re.match 尝试从字符串的起始位置匹配一个模式。如果不是起始位置匹配成功的话，match（）就返回Nome
connet = 'Hello 123 4567 World_This is a Regex Demo'
result = re.match('^Hello\s\d\d\d\s\d{4}\s\w{10}.*Demo$', connet)  # \s为空格，\d为要匹配的字符
# 泛匹配
result = re.match('^Hello.*Demo$', connet)  # .*匹配中间所有字符串
# 匹配目标
# 从第一个括号中获取目标,指定左右端点
connet = 'Hello 1234567 World_This is a Regex Demo'
result = re.match('^Hello\s(\d+)\sWorld.*Demo$', connet)
print(result)
print(result.group(1))  # 返回匹配结果
print(result.span())  # 返回匹配结果长度
# 贪婪匹配
# .*尽可能匹配更多
connet = 'Hello 1234567 World_This is a Regex Demo'
result = re.match('^He.*(\d+).*Demo$', connet)
print(result)
print(result.group(1))  # 返回匹配结果
print(result.span())  # 返回匹配结果长度
# 非贪婪匹配
# .*?匹配尽可能少的字符
connet = 'Hello 1234567 World_This is a Regex Demo'
result = re.match('^He.*?(\d+).*Demo$', connet)
print(result)
print(result.group(1))  # 返回匹配结果,获取第一个括号中内容
print(result.span())  # 返回匹配结果长度
# 匹配模式
connet = '''Hello 1234567 World_This\
          is a Regex Demo'''
result = re.match('^He.*?(\d+).*?Demo$', connet)  # re.S添加换行符
print(result)
print(result.group(1))  # 返回匹配结果,获取第一个括号中内容
print(result.span())  # 返回匹配结果长度
# 转义
# \转义
content = 'price is $5.00'
result = re.match('price is \$5\.00', content)
print(result)
# 尽量使用泛匹配(.*)，使用括号得到匹配目标(\d+)，尽量使用非贪婪匹配(.*?)，有换行符就用re.S

re.search
#扫描整个字符串并返回第一个成功的匹配
connet = 'sad Hello 1234567 World_This is a Regex Demo'
result = re.search('Hello.*?(\d+).*?Demo', connet)
print(result)
print(result.group(1))
# 为了方便能用search就不用match
# re.findall 搜索字符串，以列表形式返回全部能匹配的字符串  匹配换行符（*？）
# re.sub 替换字符串每一个匹配的字符串返回替换后的字符串
connet = 'sad Hello 1234567 World_This is a Regex Demo'
result = re.sub('\d+', '', connet)
print(result)
# print(result.group(1))
# re.compile将正则字符串编译成正则表达式对象
connet = 'Hello 1234567 World_This is a Regex Demo'
pattern = re.compile('Hello.*?(\d+).*?Demo', re.S)  # 创建对象再引用
result = pattern.findall(connet)
print(result)
print(result.group(1))
# 爬取豆瓣网
headrs = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}
connet = requests.get('https://book.douban.com/', headers=headrs).text
pattern = re.compile(
    '<li.*?cover.*?href=\"(.*?)\".*?title=\"(.*?)\".*?more-meta.*?author\">(.*?)</span>.*?year\">(.*?)</span>.*?</li>',
    re.S)
results = re.findall(pattern, connet)
print(results)
for result in results:
    url, name, author, date = result
    author = re.sub('\\s', '', author)
    date = re.sub('\\s', '', date)
    print(url, name, author, date)
