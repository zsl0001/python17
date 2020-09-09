import requests

url = 'https://m16376382e015561c.wxvote.pingxuan123.com/page/votedsf/id/1f63653cf600c009/v/2.html?iid=125e077c8c3a92df&verify=undefined'
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept - Language': 'zh - CN, zh;q = 0.8, en - US;q = 0.6, en;q = 0.5;q = 0.4',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1301.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI MicroMessenger/7.0.5 WindowsWechat',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': 'acw_tc = 76b20f4815919300067222548e9fba54a72c209b04b7f026c384c6056ec726;PHPSESSID = 2o1640acj755m4djldv9s0q8cl;_dx_uzZo5y = 589dbcaaf01654e76c85ac6e8782f68f20d84f0fde15bdb4ac7e76d32ef59592b59506ef;Hm_lvt_bcace4f98e9d72556c97c625891a8cda = 1591930010;Hm_lpvt_bcace4f98e9d72556c97c625891a8cda = 1591931487;read = 1f63653cf600c009;SERVERID = 37b41cf19ffebc0243e2bb33dc2afda0 | 1591931491 | 1591931469',
    'js_lib_ver': '1.01&hx%5Bvid%5D=1f63653cf600c009&hx%5Buid%5D=o5pn4vobZlAtR2RTWH7QBr629Xuw&hx%5Bwnw%5D=0&hx%5Btime%5D=1591931486&hx%5Btoken%5D=b7e82f63a3996639d97cb5bdd42bddec&hx%5Bdx_token%5D=5ee2ec9aM68RAE1fAcj0jnFSVRvV9ojQ9zhCuhk1&token=733b628258bfd19198f271d99ffa70d5'
}

data = {
    'js_lib_ver': '1.01',
    'hx[vid]': '1f63653cf600c009',
    'hx[uid]	': 'o5pn4vobZlAtR2RTWH7QBr629Xuw',
    'hx[wnw]': '0',
    'hx[time]': '1591931486',
    'hx[token]': 'b7e82f63a3996639d97cb5bdd42bddec',
    'hx[dx_token]': '5ee2ec9aM68RAE1fAcj0jnFSVRvV9ojQ9zhCuhk1',
    'token': '733b628258bfd19198f271d99ffa70d5'
}
res = requests.post(url, headers=headers)
print(res.content.decode('UTF-8'))
