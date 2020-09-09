import sys

sys.path.append("..")

import models


class get_log:
    def __init__(self, data):
        self.models = models
        self.imei = data['imei']
        self.page = data['page']
        self.size = data['size']

    def get_logs(self):
        pass
