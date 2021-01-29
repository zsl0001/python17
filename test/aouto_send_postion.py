from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/aotu_send_msg/", methods=['POST'])
def aotu_send_msg():
    if request.method == 'POST':
        data = request.get_json(force=True)
    return '200'


if __name__ == '__main__':
    app.run(host='0.0.0.0',  # 设置ip，默认127.0.0.1
            port=6666,  # 设置端口，默认5000
            debug=None,
            threaded=True)
