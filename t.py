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
        """
        print(f"[Takeoff] 起飞中，目标高度 {altitude}m ...")
        self.client.takeoffAsync(timeout_sec=timeout).result()

        if altitude > 3.0:
            self.client.moveToZAsync(-altitude, velocity=3.0).result()

        print(f"[Takeoff] 已到达 {altitude}m")

    def _get_distance_sensor_data(self, sensor_name: str) -> float:
        """获取指定传感器的距离值（如果读取失败或超出量程则返回默认最大距离）"""
        try:
            data = self.client.getDistanceSensorData(distance_sensor_name=sensor_name)
            return data.distance
        except Exception as e:
            print(f"距离传感器获取出错: {e}")
            return 20.0

    def goto(self, lat: float, lon: float, alt: float,
             velocity: float = 5.0, safe_distance: float = 4.0):
        """
        自带避障功能的飞往目标 GPS 坐标。
        safe_distance: 触发避障的临界距离（米），当低于此距离时触发绕行
        """
        print(f"[Goto] 开始导航至 ({lat:.6f}, {lon:.6f})，高度 {alt}m，启用避障功能...")
        
        # 启动初始的向目标飞行的异步任务
        fly_task = self.client.moveToGPSAsync(
            latitude=lat, longitude=lon, altitude=alt, velocity=velocity
        )

        while True:
            # 检查是否已经到达目标点（异步任务是否结束）
            if fly_task.done():
                print("[Goto] 已成功到达目标点")
                break

            # 1. 读取各方向传感器的实时距离
            dist_front = self._get_distance_sensor_data("DistanceFront")
            dist_left  = self._get_distance_sensor_data("DistanceLeft")
            dist_right = self._get_distance_sensor_data("DistanceRight")
            dist_up    = self._get_distance_sensor_data("DistanceUp")

            # 2. 核心避障逻辑判断
            if dist_front < safe_distance:
                print(f"⚠️ [Obstacle Detected] 前方有障碍物！距离: {dist_front:.2f}m")

                # 立即取消当前的导航路线，让无人机停下准备避障
                fly_task.cancel()
                self.client.hoverAsync().result()

                # 决定绕行方向：哪边空旷往哪边走，如果左右都不行就往上拉升
                vx, vy, vz = 0.0, 0.0, 0.0

                if dist_right > dist_left and dist_right > safe_distance:
                    print("➡️ 正在向右侧横移绕行...")
                    vy = 3.0  # 向右平移速度 (NED系中Y轴正向为右)
                elif dist_left > safe_distance:
                    print("⬅️ 正在向左侧横移绕行...")
                    vy = -3.0 # 向左平移速度 (NED系中Y轴负向为左)
                elif dist_up > 2.0:
                    print("⬆️ 左右受限，正在向上拉升绕行...")
                    vz = -3.0 # 向上拉升 (NED系中Z轴负向为上)
                else:
                    print("🛑 四周受限，紧急原地悬停等待！")
                    time.sleep(1)
                    continue

                # 执行短暂的避障微调动作，持续 1.5 秒
                self.client.moveByVelocityAsync(vx, vy, vz, duration=1.5).result()

                # 避障动作完成后，重新计算并下发飞往目标的任务，继续循环监听
                print("🔄 避障暂告段落，重新规划路线飞往目标...")
                fly_task = self.client.moveToGPSAsync(
                    latitude=lat, longitude=lon, altitude=alt, velocity=velocity
                )

            # 每 0.1 秒扫描一次传感器，避免给仿真器造成过高负载
            time.sleep(0.1)

    def land(self, timeout: float = 60.0):
        """降落"""
        print("[Land] 降落中 ...")
        self.client.landAsync(timeout_sec=timeout).result()
        time.sleep(2)
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

        # 2. 飞往目标点并开启自动避障
        TARGET_LAT = 28.164329
        TARGET_LON = 112.932320
        TARGET_ALT = 137.0

        # 传入 safe_distance=4.0 代表离障碍物还有 4 米时就会开始向侧方绕行
        drone.goto(TARGET_LAT, TARGET_LON, TARGET_ALT, velocity=6.0, safe_distance=15)
        time.sleep(2)

        # 3. 降落
        drone.land()

    finally:
        drone.close()