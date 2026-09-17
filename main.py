"""DroneGo 应用入口。

UI 代码已迁移至 views/ 子包，本文件只保留 App 入口（生命周期 + 后台任务）。
"""

import asyncio
import datetime

import flet as ft
import keyvals

from config import Config
from dronecontroller import DroneController
from dronemanager import DroneManager
from usermanager import UserManager

from views.pages.agreement import build_agreement
from views.view_builder import ViewBuilder


class App:
    def __init__(self):
        self.AMAP_KEY = keyvals.AMAP_KEY
        self.config = Config()
        self.user_manager = UserManager()
        self.drone_manager = DroneManager()
        # self.drone_controller = DroneController()
        self.page = None
        self.view_builder = ViewBuilder(self)

    def before_main(self, page: ft.Page):
        """首启：未同意协议则显示协议页；已同意则直接进入主界面。"""
        self.page = page
        page.title = "DroneGo"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0

        if not self.config.get("agreed"):
            page.add(build_agreement(self))
        else:
            self.main(page)

    def main(self, page: ft.Page):
        """主界面：底部导航 + 首页 + 后台订单扫描任务。"""
        def on_nav_change(e):
            """底部导航栏切换"""
            index = e.control.selected_index
            if index == 0:
                self.view_builder.goto("home")
            elif index == 1:
                self.view_builder.goto("orders")
            elif index == 2:
                self.view_builder.goto("profile")

        page.navigation_bar = ft.NavigationBar(
            selected_index=0,
            on_change=on_nav_change,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.EXPLORE_OUTLINED,
                    selected_icon=ft.Icons.EXPLORE,
                    label="首页",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.LIST_ALT_OUTLINED,
                    selected_icon=ft.Icons.LIST_ALT,
                    label="订单",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.PERSON_OUTLINE,
                    selected_icon=ft.Icons.PERSON,
                    label="我的",
                ),
            ],
        )

        # 加载首页（通过 ViewBuilder.start，不再直接引用 build_home）
        page.add(self.view_builder.start())
        page.run_task(self.order_checker)

    async def order_checker(self):
        """后台任务：扫描到时间的"待配送"订单，自动转入"租赁中"并起飞无人机。"""
        while True:
            phone = self.config.get("last_user")

            if not phone:
                await asyncio.sleep(10)
                continue

            now = datetime.datetime.now().astimezone()
            for order in self.user_manager.get_orders(phone):
                status = order.get("status")
                start = datetime.datetime.strptime(
                    order["start_time"], "%Y-%m-%d %H:%M"
                ).astimezone()

                if status == "待配送" and now >= start:
                    on_task_finished = lambda: self.user_manager.update_order_status(
                        phone, order["id"], "已完成"
                    )
                    self.drone_controller.create_task(
                        order["start_location"], order["location"], on_task_finished
                    )
                    self.user_manager.update_order_status(phone, order["id"], "租赁中")

            await asyncio.sleep(10)

    def __call__(self, *args, **kwargs):
        self.before_main(*args, **kwargs)


if __name__ == "__main__":
    app = App()
    ft.run(app, view=ft.AppView.WEB_BROWSER)
