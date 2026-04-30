import hashlib
from file import FileReader, FileWriter

class UserManager:
    def __init__(self):
        self.FILE = "users.json"
        self.users = FileReader.read_json(self.FILE)
        self.save()

    def _hash_password(self, password: str) -> str:
        """将明文密码转换为 SHA-256 哈希字符串"""
        # 使用 sha256 算法
        sha256 = hashlib.sha256()
        # 哈希计算需要 bytes 类型，所以要 encode
        sha256.update(password.encode('utf-8'))
        return sha256.hexdigest()

    def contains(self, phone_number: str) -> bool: 
        return phone_number in self.users
    
    def add(self, phone_number: str, nick_name: str, password: str):
        """添加用户时，存储哈希后的密码"""
        hashed_pwd = self._hash_password(password)
        
        self.users[phone_number] = {
            "nick_name": nick_name,
            "password": hashed_pwd
        }
        self.save()

    def verify_login(self, phone_number: str, input_password: str) -> bool:
        """验证登录：比对输入密码的哈希值与存储的是否一致"""
        user = self.users.get(phone_number)
        if not user:
            return False
        
        # 将用户刚才输入的密码进行同样的哈希处理
        return user["password"] == self._hash_password(input_password)

    def save(self):
        """持久化到文件"""
        FileWriter.write_json(self.FILE, self.users)