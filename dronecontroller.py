import time
import airsim
from threading import Thread
from routemanager import RouteManager
from airsim import DrivetrainType, YawMode

class DroneController:
    def __init__(self, ip: str = "127.0.0.1", port: int = 41451):
        self.client = airsim.MultirotorClient(ip=ip, port=port)
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)
        self.alt = 0

    def get_distance(self, sensor_name: str):
        data = self.client.getDistanceSensorData(distance_sensor_name=sensor_name)
        return data.distance

    def takeoff(self, altitude: float = 15.0, timeout: float = 20.0):
        """
        起飞到指定高度（米）。
        AirSim 使用 NED 坐标系，Z 轴向下，所以高度取负值。
        """
        print(f"[Takeoff] 起飞中，目标高度 {altitude}m ...")
        self.client.takeoffAsync(timeout_sec=timeout).result()

        # takeoffAsync 只飞到约 3m，继续爬升到目标高度
        if altitude > 3.0:
            self.client.moveToZAsync(-altitude, velocity=3.0).result()

        print(f"[Takeoff] 已到达 {altitude}m")
        self.alt = self.get_state()["alt"]

    def goto(self, lat: float, lon: float, timeout: float = 3600.0):
        """
        飞往目标 GPS 坐标。
        lat/lon 为十进制度，alt 为高度（米，正值）。
        """
        print(f"[Goto] 飞往 ({lat:.6f}, {lon:.6f})，高度 {self.alt}m ...")

        fly_task = self.client.moveToGPSAsync(
            latitude=lat,
            longitude=lon,
            altitude=self.alt,
            velocity=15.0,
            timeout_sec=timeout,
            drivetrain=DrivetrainType.ForwardOnly,
            yaw_mode=YawMode(False, 0)
        )

        while True:
            if fly_task.done():
                print(f"[Goto] 已到达目标点")
                break

            distance_front = self.get_distance("DistanceFront")
            distance_left = self.get_distance("DistanceLeft")
            distance_right = self.get_distance("DistanceRight")
            distance_up = self.get_distance("DistanceUp")
            distance_down = self.get_distance("DistanceDown")

            if distance_front < 15.0:
                print(f"⚠️ [Obstacle Detected] 前方有障碍物！距离: {distance_front:.2f}m")

                fly_task.cancel()
                self.client.hoverAsync().result()

                vx, vy, vz = 0.0, 0.0, 0.0
                if distance_up > 25.0:
                    vz = -2.0
                elif distance_left > 25.0:
                    print("正在向左侧横移绕行...")
                    vy = -2.0
                elif distance_right > 25.0:
                    print("正在向右侧横移绕行...")
                    vy = 2.0

                self.client.moveByVelocityAsync(vx, vy, vz, duration=1.5).result()
                self.alt = self.get_state()["alt"]

                print("🔄 避障暂告段落，重新规划路线飞往目标...")
                fly_task = self.client.moveToGPSAsync(
                    latitude=lat, longitude=lon, altitude=self.alt, velocity=15.0, timeout_sec=timeout,
                    drivetrain=DrivetrainType.ForwardOnly, yaw_mode=YawMode(False, 0)
                )
            elif distance_down < 5:
                print(f"⚠️ [Ground Approaching] 防触底触发！下距离: {distance_down:.2f}m")

                vz = -2.0
                self.client.moveByVelocityAsync(0.0, 0.0, vz, duration=1.5).result()
                self.alt = self.get_state()["alt"]

                print("🔄 避障暂告段落，重新规划路线飞往目标...")
                fly_task = self.client.moveToGPSAsync(
                    latitude=lat, longitude=lon, altitude=self.alt, velocity=15.0, timeout_sec=timeout,
                    drivetrain=DrivetrainType.ForwardOnly, yaw_mode=YawMode(False, 0)
                )
            else:
                self.alt = self.get_state()["alt"]

            time.sleep(0.1)

    def land(self, timeout: float = 60.0):
        """
        基于下方距离传感器优化的柔性降落
        """
        print("[Land] 开始智能降落程序...")
        start_time = time.time()
        
        # 1. 确保无人机先进入速度控制模式，安全下落
        while time.time() - start_time < timeout:
            dist_down = self.get_distance("DistanceDown")
            print(f"[Land] 当前相对地面高度: {dist_down:.2f}m")

            # 阶段 A：距离地面较高，快速下降
            if dist_down > 1.5:
                # 速度 1.5 m/s 下降 (NED系中 Z轴正向为下)
                self.client.moveByVelocityAsync(0.0, 0.0, 1.5, duration=0.2).result()
            # 阶段 B：进入超低空缓冲区，柔性接地
            elif dist_down > 0.5:
                print("[Land] 进入超低空缓冲区，减速慢降...")
                # 切换为 0.3 m/s 的极慢速度，防止弹跳
                self.client.moveByVelocityAsync(0.0, 0.0, 0.3, duration=0.2).result()
            else:
                break

            time.sleep(0.1)

        print("[Land] 安全")
        # 让无人机静止一下
        self.client.hoverAsync().result()
        time.sleep(0.5)

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

    def fly_task(self, routes, callback):
        for route in routes:
            self.takeoff()

            for p in route:
                self.goto(p[0], p[1])

            self.land()

        self.close()
        callback()

    def create_task(self, start_location: str, location: str, callback):
        start_lng, start_lat = start_location.split(",")
        dest_lng, dest_lat = location.split(",")

        start_location = [float(start_lat), float(start_lng)]
        location = [float(dest_lat), float(dest_lng)]

        routes = RouteManager.auto_plan_and_visualize(start_location, location)

        task = Thread(target=self.fly_task, args=(routes, callback), daemon=True)
        task.start()