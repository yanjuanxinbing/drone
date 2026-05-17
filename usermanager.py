import hashlib
from file import FileReader, FileWriter

class UserManager:
    def __init__(self):
        self.FILE = "users.json"
        self.users = FileReader.read_json(self.FILE)

    def _hash_password(self, password: str) -> str:
        """将明文密码转换为 SHA-256 哈希字符串"""
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf-8'))
        return sha256.hexdigest()

    def get(self, phone) -> dict:
        return self.users.get(phone)

    def get_addresses(self, phone: str) -> list:
        return self.get(phone).get("addresses")

    def get_location_by_address(self, phone: str, address: str) -> str:
        for a in self.get_addresses(phone):
            if a["address"] == address:
                return a["location"]

    def add_address(self, phone: str, address: str, location: str):
        addresses = self.get_addresses(phone)
        new_id = str(int(addresses[-1]["id"]) + 1) if addresses else "1"
        addresses.append({"id": new_id, "address": address, "location": location})
        self.save()

    def update_address(self, phone: str, addr_id: str, address: str, location: str):
        for addr in self.get_addresses(phone):
            if addr["id"] == addr_id:
                addr["address"] = address
                addr["location"] = location
                self.save()
                return

    def set_default_address(self, phone: str, addr_id: str):
        addresses = self.get_addresses(phone)
        idx = next((i for i, a in enumerate(addresses) if a["id"] == addr_id), None)
        addresses[0]["address"], addresses[idx]["address"] = addresses[idx]["address"], addresses[0]["address"]
        addresses[0]["location"], addresses[idx]["location"] = addresses[idx]["location"], addresses[0]["location"]
        self.save()

    def delete_address(self, phone: str, addr_id: str):
        self.users[phone]["addresses"] = [
            a for a in self.get(phone).get("addresses") if a["id"] != addr_id
        ]
        self.save()

    def get_orders(self, phone: str) -> list:
        return self.get(phone).get("orders")

    def add_order(self, phone: str, order: dict):
        self.get_orders(phone).append(order)
        self.save()

    def get_order_by_id(self, phone: str, order_id: str) -> dict:
        for order in self.get_orders(phone):
            if order.get("id") == order_id:
                return order
        return None

    def update_order_status(self, phone: str, order_id: str, status: str):
        for order in self.get_orders(phone):
            if order.get("id") == order_id:
                order["status"] = status
                self.save()
                return

    def cancel_order(self, phone: str, order_id: str):
        self.update_order_status(phone, order_id, "已取消")

    def contains(self, phone: str) -> bool: 
        return phone in self.users

    # 后续如果增加属性，应当于此修改默认值
    def add(self, phone: str, nick_name: str, password: str):
        """添加用户时，存储哈希后的密码"""
        hashed_pwd = self._hash_password(password)
        
        self.users[phone] = {
            "nick_name": nick_name,
            "password": hashed_pwd,
            "gender": "保密",
            "birthday": "",
            "addresses": [],
            "orders": []
        }
        self.save()

    def delete(self, phone: str):
        self.users.pop(phone)
        self.save()

    def update_value(self, phone, nick_name, gender, birthday):
        """更新除密码外的值"""
        self.users[phone]["nick_name"] = nick_name
        self.users[phone]["gender"] = gender
        self.users[phone]["birthday"] = birthday

        self.save()

    def update_password(self, phone, new_password):
        """更新密码（存储哈希后的新密码）"""
        self.users[phone]["password"] = self._hash_password(new_password)

        self.save()

    def update_key(self, phone_old, phone_new) -> bool:
        """更新手机号码"""
        if self.contains(phone_new):
            return False

        user = self.get(phone_old).copy()
        self.users.pop(phone_old)
        self.users[phone_new] = user
        self.save()

        return True

    def verify_login(self, phone: str, input_password: str) -> bool:
        """验证登录：比对输入密码的哈希值与存储的是否一致"""
        user = self.users.get(phone)
        if not user:
            return False
        
        # 将用户刚才输入的密码进行同样的哈希处理
        return user["password"] == self._hash_password(input_password)

    def save(self):
        """持久化到文件"""
        FileWriter.write_json(self.FILE, self.users)