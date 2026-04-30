import requests
from PIL import Image
import numpy as np

class Listener:
    def __init__(self):
        self.DRONE_PATH = "/Game/MainMap.MainMap:PersistentLevel.BP_Drone_C_UAID_74D4DD4FD33731D302_2051078935"
        self.CAMERA_PATH = self.DRONE_PATH + ".Camera"

    def _call(self, path, func, params=None):
        body = {"objectPath": path, "functionName": func}
        if params:
            body["parameters"] = params
        r = requests.put(
            "http://localhost:30010/remote/object/call",
            json=body
        )
        return r.json().get("ReturnValue")

    # ── Getters ──────────────────────────────────────────
    def get_location(self) -> dict:
        """获取无人机世界坐标 {X, Y, Z}"""
        return self._call(self.DRONE_PATH, "GetActorLocation")

    def get_velocity(self) -> dict:
        """获取无人机当前速度向量 {X, Y, Z}"""
        return self._call(self.DRONE_PATH, "GetVelocity")

    def get_camera_rotation(self) -> dict:
        """获取摄像机世界旋转 {Pitch, Yaw, Roll}"""
        return self._call(self.CAMERA_PATH, "GetWorldRotation")

    def get_frame(self) -> np.ndarray:
        """获取当前摄像机画面，返回 HxWx3 numpy数组"""
        return np.array(Image.open(r"C:\Users\23080\Desktop\frame.png"))

    def get_state(self) -> dict:
        """一次性获取完整状态，供AI观测使用"""
        return {
            "location":        self.get_location(),
            "velocity":        self.get_velocity(),
            "camera_rotation": self.get_camera_rotation(),
            "frame":           self.get_frame(),
        }