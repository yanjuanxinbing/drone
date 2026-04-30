from file import FileReader, FileWriter

class Config:
    def __init__(self):
        self.FILE = "config.json"
        self.CONFIG = {
            "agreed": False,        # 用户协议
            "language": "zh_CN",    # 语言
            "last_user": "",        # 最后登录手机号
            "last_name": ""         # 最后用户昵称
        }

        try:
            user_data = FileReader.read_json(self.FILE)
            self.CONFIG.update(user_data)
            self.save()

        except Exception as e:
            self.save()
            print(f"Config: 配置文件解析失败 ({e})，将使用默认参数运行。")

    def get(self, key: str):
        """安全获取配置项"""
        return self.CONFIG.get(key)

    def set(self, key: str, value):
        """设置并持久化配置项"""
        self.CONFIG[key] = value
        self.save()

    def save(self):
        """将当前内存中的实例属性写入磁盘"""
        try:
            FileWriter.write_json(self.FILE, self.CONFIG)
        except Exception as e:
            print(f"Config: 无法保存配置到磁盘: {e}")