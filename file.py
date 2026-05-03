import json

ROOT = "db"

class FileReader:
    @staticmethod
    def read_txt(filename: str, subdir: str = "txt") -> str:
        """
        读取文本文件
        
        Args:
            filename: 文件名（如 "user_agreement.txt"）
            subdir: 子目录（默认 "txt"，也可以是 "templates", "logs" 等）
        """
        path = f"{ROOT}/{subdir}/{filename}"
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"FileReader: 文件不存在 - {path}")
            return ""
        except Exception as e:
            print(f"FileReader: 读取失败 - {path} ({e})")
            return ""

    @staticmethod
    def read_json(filename: str, subdir: str = "data") -> dict:
        """读取 JSON 文件"""
        path = f"{ROOT}/{subdir}/{filename}"
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"FileReader: JSON 文件不存在 - {path}")
            return {}
        except Exception as e:
            print(f"FileReader: JSON 解析失败 - {path} ({e})")
            return {}
        
    @staticmethod
    def read_img(filename: str, subdir: str = "img"):
        path = f"{ROOT}/{subdir}/{filename}"

class FileWriter:
    @staticmethod
    def write_json(filename: str, content, subdir: str = "data"):
        """写入 JSON 文件"""
        path = f"{ROOT}/{subdir}/{filename}"
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=4)

        except Exception as e:
            print(f"FileWriter: JSON 写入失败 - {path} ({e})")