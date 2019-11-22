def paginate(page, size=20):
    """
    数据库 分页 和 翻页 功能函数
    @param page: int or str 页面页数
    @param size: int or str 分页大小
    @return: dict
    {
        'limit': 20,   所取数据行数
        'offset': 0,   跳过的行数
        'before': 0,   前一页页码
        'current': 1,  当前页页码
        'next': 2      后一页页码
    }
    """

    if not isinstance(page, int):
        try:
            page = int(page)
        except TypeError:
            page = 1

    if not isinstance(size, int):
        try:
            size = int(size)
        except TypeError:
            size = 20

    if page > 0:
        page -= 1

    data = {
        "limit": size,
        "offset": page * size,
        "before": page,
        "current": page + 1,
        "next": page + 2
    }

    return data


if __name__ == '__main__':
    result = paginate(None, None)
    print(type(result))

    result = paginate(0, 20)
    print(result)

    result = paginate(1, 50)
    print(result)

    result = paginate(3, 20)
    print(result)

    result = paginate("3", "30")
    print(result)

    """
    {'limit': 20, 'offset': 0, 'before': 0, 'current': 1, 'next': 2}
    {'limit': 20, 'offset': 0, 'before': 0, 'current': 1, 'next': 2}
    {'limit': 50, 'offset': 0, 'before': 0, 'current': 1, 'next': 2}
    {'limit': 20, 'offset': 40, 'before': 2, 'current': 3, 'next': 4}
    {'limit': 30, 'offset': 60, 'before': 2, 'current': 3, 'next': 4}
    """
