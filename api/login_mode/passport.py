

from flask import g, current_app, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth
from login_mode.login_model import app, User, db
from login_mode.response_code import RET

auth = HTTPBasicAuth()


@app.route('/signin', methods=['POST'])
def signin():
    '''用户注册接口
    :return 返回注册信息{'re_code': '0', 'msg': '注册成功'}
    '''
    data = request.get_json(force=True)
    username = data['username']
    password = data['password']
    if not all([username, password]):
        return jsonify(re_code=RET.PARAMERR, msg='参数不完整')

    user = User()
    user.username = username
    user.password = password  # 利用user model中的类属性方法加密用户的密码并存入数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return jsonify(re_code=RET.DBERR, msg='注册失败')
    # 6.响应结果
    return jsonify(re_code=RET.OK, msg='注册成功')


@app.route('/login', methods=['POST'])
def login():
    '''登录
    TODO: 添加图片验证
    :return 返回响应,保持登录状态
    '''
    data = request.get_json(force=True)
    username = data['username']
    password = data['password']

    # 解析Authorization
    # email, password = base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode().split(':')

    if not all([username, password]):
        return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
    try:
        user = User.query.filter(User.username == username).first()
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(re_code=RET.DBERR, msg='查询用户失败')
    if not user:
        return jsonify(re_code=RET.NODATA, msg='用户不存在', user=user)
    if not user.verify_password(password):
        return jsonify(re_code=RET.PARAMERR, msg='帐户名或密码错误')

    # 更新最后一次登录时间
    user.update_last_seen()
    token = user.generate_user_token()
    return jsonify(re_code=RET.OK, msg='登录成功', token=token,username=user.username,ID=user.id)


@auth.verify_password
def verify_password(username_or_token, password):
    if request.path == '/login':
        user = User.query.filter_by(email=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    else:
        user = User.verify_user_token(username_or_token)
        if not user:
            return False

    g.user = user
    return True


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 201)


@app.route('/')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@app.route('/login')
@auth.login_required
def get_user_token():
    token = g.user.generate_user_token()
    return jsonify(re_code=RET.OK, msg='获取Token成功', token=token.decode('ascii'), usr=g.user.username)


if __name__ == '__main__':
    app.run(host='0.0.0.0',  # 设置ip，默认127.0.0.1
            port=5555,  # 设置端口，默认5000
            debug=None)  # 设置是否开启调试，默认false
