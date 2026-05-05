from file import FileReader, FileWriter

class Config:
    def __init__(self):
        self.FILE = "config.json"
        self.CONFIG = {
            "agreed": False,        # 用户协议
            "language": "zh_CN",    # 语言
            "notify_enabled": True, # 提醒功能
            "last_user": ""         # 最后登录手机号
        }

        user_data = FileReader.read_json(self.FILE)
        self.CONFIG.update(user_data)
        self.save()

    def get(self, key: str):
        """安全获取配置项"""
        return self.CONFIG.get(key)

    def set(self, key: str, value):
        """设置并持久化配置项"""
        self.CONFIG[key] = value
        self.save()

    def logout(self):
        self.CONFIG["last_user"] = ""
        self.save()

    def save(self):
        """将当前内存中的实例属性写入磁盘"""
        FileWriter.write_json(self.FILE, self.CONFIG)