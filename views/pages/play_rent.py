"""自驾模式页（含 AirSim 实时图传与摇杆控制）。"""

import asyncio
import queue
import threading
import time

import airsim
import cv2
import flet as ft
import numpy as np


def build_play_rent(app, **kwargs):
    """切换横屏 + 实时图传 + 摇杆控制"""
    # 切换横屏
    app.page.navigation_bar.visible = False
    app.page.update()

    # ── 状态 ────────────────────────────────────────────────────────────
    ctrl = {"vx": 0.0, "vy": 0.0, "vz": 0.0, "yaw": 0.0}
    flags = {"flying": False, "cam_on": True}
    frame_queue = queue.Queue(maxsize=1)

    HSPD, VSPD, YAW_SPD = 4.0, 2.5, 45.0

    # ── 抓帧线程 ─────────────────────────────────────────────────────────
    def capture_loop():
        client = app.drone_controller.client
        while flags["cam_on"]:
            raw = client.simGetImage("0", airsim.ImageType.Scene)
            if raw:
                arr = np.frombuffer(raw, np.uint8)
                img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                img = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_LINEAR)
                _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 75])
                raw = buf.tobytes()

                if frame_queue.full():
                    try:
                        frame_queue.get_nowait()
                    except:
                        pass
                frame_queue.put(raw)

    threading.Thread(target=capture_loop, daemon=True).start()

    # ── 控件 ─────────────────────────────────────────────────────────────
    img_view = ft.Image(
        fit=ft.BoxFit.FILL,
        gapless_playback=True,
        src="https://placehold.co/1920*1080/263238/90A4AE?text=画面加载中",
        height=1080,
        width=1920
    )

    fps_text = ft.Text("FPS: --", color=ft.Colors.GREEN, size=11)

    cam_area = ft.Stack([
        img_view,
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=fps_text,
                        padding=ft.Padding(6, 2, 6, 2),
                        bgcolor=ft.Colors.with_opacity(0.55, ft.Colors.BLACK),
                        border_radius=4,
                    )])
            ], spacing=4),
            alignment=ft.Alignment(-1, 1),
            padding=ft.Padding(8, 0, 0, 8),
        ),
    ], expand=True)

    # ── 图传异步循环 ──────────────────────────────────────────────────────
    async def camera_loop():
        loop = asyncio.get_event_loop()
        last_time = time.perf_counter()

        while flags["cam_on"]:
            try:
                raw = await loop.run_in_executor(
                    None, lambda: frame_queue.get()
                )
                img_view.src = raw
                img_view.update()

                current_time = time.perf_counter()
                elapsed = current_time - last_time
                last_time = current_time

                if elapsed > 0:
                    fps_text.value = f"FPS: {1 / elapsed:.1f}"
                    fps_text.update()

            except:
                pass

    # ── 控制指令循环 ──────────────────────────────────────────────────────
    async def control_loop():
        loop = asyncio.get_event_loop()
        client = app.drone_controller.client

        while flags["flying"]:
            try:
                if ctrl["yaw"] != 0.0:
                    await loop.run_in_executor(
                        None,
                        lambda: client.rotateByYawRateAsync(ctrl["yaw"], 0.15),
                    )
                else:
                    vx, vy, vz = ctrl["vx"], ctrl["vy"], ctrl["vz"]
                    await loop.run_in_executor(
                        None,
                        lambda: client.moveByVelocityBodyFrameAsync(vx, vy, vz, duration=0.2),
                    )
            except Exception:
                pass
            await asyncio.sleep(0.1)

    # ── 起飞/降落 ─────────────────────────────────────────────────────────
    fly_btn = ft.Button(
        "一键起飞",
        icon=ft.Icons.FLIGHT_TAKEOFF,
        bgcolor=ft.Colors.GREEN_700,
        color=ft.Colors.WHITE,
        height=40,
    )

    async def toggle_flight(_):
        loop = asyncio.get_event_loop()
        client = app.drone_controller.client

        if not flags["flying"]:
            try:
                await loop.run_in_executor(None, lambda: client.enableApiControl(True))
                await loop.run_in_executor(None, lambda: client.armDisarm(True))
                await loop.run_in_executor(None, lambda: client.takeoffAsync(timeout_sec=15).result())
                flags["flying"] = True
                fly_btn.content = "紧急降落"
                fly_btn.icon = ft.Icons.FLIGHT_LAND
                fly_btn.bgcolor = ft.Colors.RED_700
                fly_btn.update()
                app.page.run_task(control_loop)
            except Exception as e:
                app.view_builder.show_snackbar(f"起飞失败：{e}", ft.Colors.RED_400)
        else:
            flags["flying"] = False
            ctrl.update({"vx": 0, "vy": 0, "vz": 0, "yaw": 0})
            fly_btn.content = "一键起飞"
            fly_btn.icon = ft.Icons.FLIGHT_TAKEOFF
            fly_btn.bgcolor = ft.Colors.GREEN_700
            fly_btn.update()
            try:
                await loop.run_in_executor(None, lambda: client.landAsync().result())
            except Exception:
                pass

    fly_btn.on_click = toggle_flight

    # ── 摇杆按钮工厂 ──────────────────────────────────────────────────────
    def joy_btn(icon, axis, value, size=52):
        def on_down(_):
            ctrl[axis] = value

        def on_up(_):
            ctrl[axis] = 0.0

        return ft.GestureDetector(
            content=ft.Container(
                content=ft.Icon(icon, size=22, color=ft.Colors.WHITE),
                width=size, height=size,
                bgcolor=ft.Colors.BLUE_GREY_700,
                border_radius=size // 2,
                alignment=ft.Alignment(0, 0),
                shadow=ft.BoxShadow(
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
                ),
            ),
            on_tap_down=on_down,
            on_tap_up=on_up,
            on_pan_end=on_up,
        )

    def cross_pad(top_icon, top_axis, top_val,
                  bot_icon, bot_axis, bot_val,
                  lft_icon, lft_axis, lft_val,
                  rgt_icon, rgt_axis, rgt_val,
                  label: str):
        return ft.Column([
            ft.Text(label, size=10, color=ft.Colors.GREY_400,
                    text_align=ft.TextAlign.CENTER),
            joy_btn(top_icon, top_axis, top_val),
            ft.Row([
                joy_btn(lft_icon, lft_axis, lft_val),
                ft.Container(width=14, height=14,
                             bgcolor=ft.Colors.BLUE_GREY_400,
                             border_radius=7),
                joy_btn(rgt_icon, rgt_axis, rgt_val),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            joy_btn(bot_icon, bot_axis, bot_val),
        ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            alignment=ft.MainAxisAlignment.END  # 👈 关键：强制让 Column 内部的所有按钮和文字沉到最底部
        )

    left_pad = cross_pad(
        ft.Icons.KEYBOARD_ARROW_UP, "vz", -VSPD,
        ft.Icons.KEYBOARD_ARROW_DOWN, "vz", VSPD,
        ft.Icons.ROTATE_LEFT, "yaw", -YAW_SPD,
        ft.Icons.ROTATE_RIGHT, "yaw", YAW_SPD,
        "油门 / 偏航",
    )

    right_pad = cross_pad(
        ft.Icons.KEYBOARD_ARROW_UP, "vx", HSPD,
        ft.Icons.KEYBOARD_ARROW_DOWN, "vx", -HSPD,
        ft.Icons.KEYBOARD_ARROW_LEFT, "vy", -HSPD,
        ft.Icons.KEYBOARD_ARROW_RIGHT, "vy", HSPD,
        "前后 / 左右",
    )

    # ── 退出 ─────────────────────────────────────────────────────────────
    def on_back(_):
        flags["cam_on"] = False
        flags["flying"] = False
        app.page.navigation_bar.visible = True
        app.page.orientation = "portrait"
        app.page.update()
        app.view_builder.goto("home")

    # 启动图传循环
    app.page.run_task(camera_loop)

    # ── 布局（横屏：左摇杆 | 画面+顶栏 | 右摇杆）────────────────────────
    return ft.Row([
        # 左摇杆
        ft.Container(
            content=left_pad,
            width=130,
            alignment=ft.Alignment(-0.5, 0.8),
            bgcolor=ft.Colors.WHITE,
            padding=ft.Padding(10, 0, 0, 20),
        ),

        # 中间
        ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back),
                    ft.Text("自驾模式", size=15, weight="bold", expand=True),
                    fly_btn,
                ], spacing=8),
                bgcolor=ft.Colors.WHITE,
                padding=ft.Padding(5, 8, 10, 8),
            ),
            ft.Container(
                content=cam_area,
                expand=True,
                bgcolor=ft.Colors.BLACK,
                border_radius=8,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
        ], expand=True, spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH),

        # 右摇杆
        ft.Container(
            content=right_pad,
            width=130,
            alignment=ft.Alignment(0.5, 0.8),
            bgcolor=ft.Colors.WHITE,
            padding=ft.Padding(0, 0, 10, 20),
        ),
    ], expand=True, spacing=0)
