import hashlib
from file import FileReader, FileWriter

class UserManager:
    def __init__(self):
        self.FILE = "users.json"
        self.users = FileReader.read_json(self.FILE)
        self.save()

    def _hash_password(self, password: str) -> str:
        """将明文密码转换为 SHA-256 哈希字符串"""
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf-8'))
        return sha256.hexdigest()

    def get(self, phone_number) -> dict:
        return self.users.get(phone_number)

    def get_addresses(self, phone: str) -> list:
        return self.get(phone).get("addresses", [])

    def add_address(self, phone: str, address: str):
        addresses = self.get_addresses(phone)
        new_id = str(int(addresses[-1]["id"]) + 1) if addresses else "1"
        addresses.append({"id": new_id, "address": address})
        self.users[phone]["addresses"] = addresses
        self.save()

    def update_address(self, phone: str, addr_id: str, new_address: str):
        for addr in self.get(phone).get("addresses"):
            if addr["id"] == addr_id:
                addr["address"] = new_address
                self.save()
                return

    def delete_address(self, phone: str, addr_id: str):
        self.users[phone]["addresses"] = [
            a for a in self.get(phone).get("addresses") if a["id"] != addr_id
        ]
        self.save()

    def contains(self, phone_number: str) -> bool: 
        return phone_number in self.users

    def add(self, phone_number, nick_name, password, gender="保密", birthday=""):
        """添加用户时，存储哈希后的密码"""
        hashed_pwd = self._hash_password(password)
        
        self.users[phone_number] = {
            "nick_name": nick_name,
            "password": hashed_pwd,
            "gender": gender,
            "birthday": birthday
        }
        self.save()

    def update_value(self, phone_number, nick_name, gender, birthday):
        """更新除密码外的值"""
        self.users[phone_number]["nick_name"] = nick_name
        self.users[phone_number]["gender"] = gender
        self.users[phone_number]["birthday"] = birthday

        self.save()

    def update_password(self, phone_number, new_password):
        """更新密码（存储哈希后的新密码）"""
        self.users[phone_number]["password"] = self._hash_password(new_password)

        self.save()

    def update_key(self, phone_number_old, phone_number_new) -> bool:
        """更新手机号码"""
        if self.contains(phone_number_new):
            return False

        user = self.get(phone_number_old).copy()
        self.users.pop(phone_number_old)
        self.users[phone_number_new] = user
        self.save()

        return True

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