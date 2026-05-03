from file import FileReader

class DroneManager:
    def __init__(self):
        self.FILE = "drones.json"
        self.drones = FileReader.read_json(self.FILE).get("drones", [])
    
    def get_all(self) -> list:
        """获取所有无人机"""
        return self.drones
    
    def get_by_id(self, drone_id: str) -> dict:
        """根据ID获取无人机"""
        for drone in self.drones:
            if drone.get("id") == drone_id:
                return drone
        return None
    
    def get_by_category(self, category: str) -> list:
        """根据分类获取无人机"""
        return [d for d in self.drones if d.get("category") == category]
    
    def search(self, keyword: str) -> list:
        """搜索无人机（按名称或规格）"""
        keyword = keyword.lower()
        return [
            d for d in self.drones 
            if keyword in d.get("name", "").lower() 
            or keyword in d.get("specs", "").lower()
            or keyword in d.get("description", "").lower()
        ]
    
    def get_hot(self, limit: int = 4) -> list:
        """获取热门无人机（按销量排序）"""
        sorted_drones = sorted(
            self.drones, 
            key=lambda d: d.get("sales", 0), 
            reverse=True
        )
        return sorted_drones[:limit]