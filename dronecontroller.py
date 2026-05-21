import airsim
import time

class DroneController:
    def __init__(self, ip: str = "127.0.0.1", port: int = 41451):
        self.client = airsim.MultirotorClient(ip=ip, port=port)
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)

    def takeoff(self, altitude: float = 10.0, timeout: float = 20.0):
        """
        起飞到指定高度（米），默认 10 米。
        AirSim 使用 NED 坐标系，Z 轴向下，所以高度取负值。
        """
        print(f"[Takeoff] 起飞中，目标高度 {altitude}m ...")
        self.client.takeoffAsync(timeout_sec=timeout).result()

        # takeoffAsync 只飞到约 3m，继续爬升到目标高度
        if altitude > 3.0:
            self.client.moveToZAsync(-altitude, velocity=3.0).result()

        print(f"[Takeoff] 已到达 {altitude}m")

    def goto(self, lat: float, lon: float, alt: float,
             velocity: float = 5.0, timeout: float = 60.0):
        """
        飞往目标 GPS 坐标。
        lat/lon 为十进制度，alt 为高度（米，正值）。
        """
        print(f"[Goto] 飞往 ({lat:.6f}, {lon:.6f})，高度 {alt}m ...")
        self.client.moveToGPSAsync(
            latitude=lat,
            longitude=lon,
            altitude=alt,
            velocity=velocity,
            timeout_sec=timeout,
        ).result()
        print(f"[Goto] 已到达目标点")

    def land(self, timeout: float = 60.0):
        """降落"""
        print("[Land] 降落中 ...")
        self.client.landAsync(timeout_sec=timeout).result()
        self.client.armDisarm(False)
        print("[Land] 已降落")

    def get_state(self) -> dict:
        """获取当前位置和速度"""
        state = self.client.getMultirotorState()
        gps = state.gps_location
        vel = state.kinematics_estimated.linear_velocity
        return {
            "lat": gps.latitude,
            "lon": gps.longitude,
            "alt": gps.altitude,
            "vx": vel.x_val,
            "vy": vel.y_val,
            "vz": vel.z_val,
        }

    def close(self):
        """释放 API 控制权"""
        self.client.enableApiControl(False)


if __name__ == "__main__":
    drone = DroneController()

    try:
        # 1. 起飞到 15m
        drone.takeoff(altitude=15.0)
        time.sleep(2)

        # 打印当前状态
        state = drone.get_state()
        print(f"[State] 当前位置: ({state['lat']:.6f}, {state['lon']:.6f}), 高度: {state['alt']:.1f}m")

        # 2. 飞往目标点（替换为实际坐标）
        TARGET_LAT = 28.164329
        TARGET_LON = 112.932320
        TARGET_ALT = 137.0          # 海拔高度（米），按 AirSim 场景调整

        drone.goto(TARGET_LAT, TARGET_LON, TARGET_ALT, velocity=8.0)
        time.sleep(2)

        # 3. 降落
        drone.land()

    finally:
        drone.close()