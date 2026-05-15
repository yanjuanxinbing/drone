import re
import sys
import aiohttp
import asyncio
import keyvals
import datetime
import flet as ft
from config import Config
import flet_geolocator as ftg
from geopy.distance import geodesic
from usermanager import UserManager
from dronemanager import DroneManager
from file import FileReader, FileWriter

class ViewBuilder:
    """视图构建器 - 只负责生成 UI"""
    def __init__(self, app: App):
        self.app = app

    def goto(self, name, drone_id=None, keyword=None, is_booking=False, selected_address=None, start_address=None, is_start=False, order_id=None, selected_index=None):
        """通用页面跳转"""
        self.app.page.controls.clear()

        nav = self.app.page.navigation_bar
        match name:
            case "home":
                nav.selected_index = 0
                view = self.build_home()
            case "orders":
                nav.selected_index = 1
                view = self.build_orders(selected_index)
            case "order_detail":
                view = self.build_order_detail(order_id)
            case "profile":
                nav.selected_index = 2
                view = self.build_profile()
            case "login":
                view = self.build_login()
            case "register":
                view = self.build_register()
            case "forget":
                view = self.build_forget()
            case "drone":
                view = self.build_drone_detail(drone_id)
            case "order":
                view = self.build_order(drone_id, is_booking, selected_address, start_address)
            case "search":
                view = self.build_search(keyword)
            case "settings":
                view = self.build_settings()
            case "personal_info":
                view = self.build_personal_info()
            case "change_password":
                view = self.build_change_password()
            case "change_phone":
                view = self.build_change_phone()
            case "addresses":
                view = self.build_addresses()
            case "privacy_settings":
                view = self.build_privacy_settings()
            case "help_center":
                view = self.build_help_center()
            case "address_picker":
                view = self.build_address_picker(drone_id, is_booking, selected_address, start_address, is_start)
            case _:
                print(f"未知路由: {name}")
                return

        self.app.page.add(view)
        self.app.page.update()

    def show_snackbar(self, text, color):
        snackbar = ft.SnackBar(
            content=ft.Text(text), 
            bgcolor=color
            )
        self.app.page.overlay.append(snackbar)
        snackbar.open = True
        self.app.page.update()

    def build_card(self, drone_id, name, price, tag, specs):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("🚁", size=50),
                    alignment=ft.Alignment.CENTER,
                    height=100,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=12,
                ),
                ft.Text(name, weight="bold", size=16),
                ft.Text(specs, size=12, color=ft.Colors.GREY_600, max_lines=1),
                ft.Row([
                    ft.Text(f"¥ {price}", color=ft.Colors.BLUE_700, weight="bold", size=16),
                    ft.Container(
                        content=ft.Text(tag, size=10, color="white"),
                        bgcolor=ft.Colors.BLUE,
                        padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                        border_radius=4,
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            padding=12,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK_12),
            on_click=lambda: self.goto("drone", drone_id=drone_id)
        )

    def build_search(self, keyword: str):
        """搜索结果页"""
        results = self.app.drone_manager.search(keyword)

        if results:
            content = ft.GridView(
                expand=True,
                runs_count=2,
                max_extent=250,
                child_aspect_ratio=0.75,
                spacing=15,
                run_spacing=15,
                controls=[
                    self.build_card(
                        drone_id=drone["id"],
                        name=drone["name"],
                        price=str(drone["price"]),
                        tag=drone["tag"],
                        specs=drone["specs"],
                    ) for drone in results
                ],
            )
        else:
            content = ft.Container(
                content=ft.Column([
                    ft.Text("🔍", size=80),
                    ft.Container(height=10),
                    ft.Text("没有找到相关机型", size=18, weight="bold"),
                    ft.Container(height=8),
                    ft.Text(
                        f"试试其他关键词？",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Container(height=20),
                    ft.OutlinedButton(
                        "返回首页",
                        icon=ft.Icons.HOME_OUTLINED,
                        on_click=lambda: self.goto("home"),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
            )

        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda: self.goto("home")),
                    ft.TextField(
                        value=keyword,
                        prefix_icon=ft.Icons.SEARCH,
                        border_radius=15,
                        filled=True,
                        expand=True,
                        on_submit=lambda e: self.goto("search", keyword=e.control.value),
                    ),
                ], spacing=5),
                padding=ft.Padding(10, 20, 20, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            ft.Container(
                content=ft.Text(
                    f"{keyword} 共 {len(results)} 个结果" if results else f"未找到 {keyword}",
                    size=13,
                    color=ft.Colors.GREY_600,
                ),
                padding=ft.Padding.symmetric(horizontal=20, vertical=8),
            ),

            ft.Container(
                content=content,
                padding=ft.Padding.symmetric(horizontal=20),
                expand=True,
            ),
        ], expand=True)

    def build_home(self):
        """构建首页"""
        header = ft.Container(
            content=ft.Text("DroneGo", size=32, weight="bold", color="white"),
            bgcolor=ft.Colors.BLUE,
            padding=30,
            width=float("inf"),
            border_radius=ft.BorderRadius.only(bottom_left=30, bottom_right=30),
        )

        def on_search(e):
            keyword = e.control.value
            if keyword:
                self.goto("search", keyword=keyword)

        search_bar = ft.Container(
            content=ft.TextField(
                prefix_icon=ft.Icons.SEARCH,
                hint_text="搜索无人机型号...",
                border_radius=15,
                filled=True,
                on_submit=on_search,
                bgcolor=ft.Colors.WHITE,
            ),
            padding=ft.Padding.symmetric(horizontal=20),
            margin=ft.Margin.only(top=-25),
        )

        # 从数据文件获取热门无人机
        hot_drones = self.app.drone_manager.get_hot(limit=4)

        drone_grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=250,
            child_aspect_ratio=0.75,
            spacing=15,
            run_spacing=15,
            controls=[
                self.build_card(
                    drone_id=drone["id"],
                    name=drone["name"],
                    price=str(f"{drone["price"] / 100.0}/千米"),
                    tag=drone["tag"],
                    specs=drone["specs"]
                ) for drone in hot_drones
            ],
        )

        return ft.Column([
            header,
            search_bar,
            ft.Container(height=10),
            ft.Container(
                content=ft.Text("推荐机型", size=18, weight="bold"),
                padding=ft.Padding.symmetric(horizontal=20)
            ),
            ft.Container(content=drone_grid, padding=20, expand=True),
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def build_order_card(self, phone, order, refresh):
        status_color = {
            "待配送": ft.Colors.ORANGE,
            "租赁中": ft.Colors.BLUE,
            "已完成": ft.Colors.GREEN,
            "已取消": ft.Colors.GREY_500
        }

        def on_cancel():
            def confirm_cancel():
                self.app.user_manager.update_order_status(phone, order["id"], "已取消")
                dialog.open = False
                refresh()

            def on_close():
                dialog.open = False
                self.app.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("取消订单", weight="bold"),
                content=ft.Text("确认取消该订单？此操作不可撤销。"),
                actions=[
                    ft.TextButton("返回", on_click=on_close),
                    ft.Button(
                        "确认取消",
                        bgcolor=ft.Colors.RED_400,
                        color=ft.Colors.WHITE,
                        on_click=confirm_cancel,
                    ),
                ],
            )
            self.app.page.overlay.append(dialog)
            dialog.open = True
            self.app.page.update()

        return ft.Container(
            content=ft.Column([
                # 顶部：机型 + 状态
                ft.Row([
                    ft.Text(order["drone_name"], size=15, weight="bold", expand=True),
                    ft.Container(
                        content=ft.Text(
                            order["status"], size=12, color=ft.Colors.WHITE,
                        ),
                        bgcolor=status_color[order["status"]],
                        padding=ft.Padding.symmetric(vertical=3, horizontal=10),
                        border_radius=12,
                    ),
                ]),
                ft.Divider(height=10, color=ft.Colors.GREY_200),
                # 中部：时间和地址
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, size=14, color=ft.Colors.GREY_500),
                    ft.Text(
                        f"{order['start_time']}",
                        size=12, color=ft.Colors.GREY_600,
                    ),
                ], spacing=6),
                ft.Row([
                    ft.Icon(ft.Icons.LOCATION_ON, size=14, color=ft.Colors.GREY_500),
                    ft.Text(order["start_address"], size=12, color=ft.Colors.GREY_600, expand=True, max_lines=1),
                ], spacing=6),
                ft.Row([
                    ft.Icon(ft.Icons.LOCATION_ON, size=14, color=ft.Colors.GREY_500),
                    ft.Text(order["address"], size=12, color=ft.Colors.GREY_600, expand=True, max_lines=1),
                ], spacing=6),
                ft.Divider(height=10, color=ft.Colors.GREY_200),
                # 底部：费用 + 操作
                ft.Row([
                    ft.Text(f"¥{order['total_price']}", size=18,
                            color=ft.Colors.RED_700, weight="bold", expand=True),
                    ft.TextButton(
                        "取消订单",
                        on_click=on_cancel,
                        style=ft.ButtonStyle(color=ft.Colors.RED_400),
                        visible=order.get("status") == "待配送",
                    ),
                    ft.TextButton(
                        "查看详情",
                        on_click=lambda _, oid=order["id"]: self.goto("order_detail", order_id=oid),
                        style=ft.ButtonStyle(color=ft.Colors.BLUE),
                    ),
                ]),
            ], spacing=6),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
        )

    def build_tab_content(self, phone, status, refresh):
        orders = [o for o in self.app.user_manager.get_orders(phone) if o.get("status") == status]

        if not orders:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=80, color=ft.Colors.GREY_400),
                    ft.Text("暂无订单", size=16, color=ft.Colors.GREY_600)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER),
                expand=True
            )

        return ft.Column([
            self.build_order_card(phone, o, refresh) for o in reversed(orders)
        ], spacing=12, scroll=ft.ScrollMode.AUTO)

    def build_orders(self, selected_index=None):
        """构建订单页"""
        phone = self.app.config.get("last_user")

        if not phone:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=100, color=ft.Colors.GREY_400),
                    ft.Text("请先登录", size=20, weight="bold"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
            )

        tabs_container = ft.Container(expand=True)

        def refresh():
            tabs_container.content = build_tabs()
            self.app.page.update()

        selected_index = selected_index or 0
        def build_tabs():
            tab_labels = ["租赁中", "待配送", "已结束", "已取消"]
            tab_contents = [self.build_tab_content(phone, label, refresh) for label in tab_labels]

            def build_tab_row():
                def on_tab_click(idx):
                    nonlocal selected_index
                    selected_index = idx
                    tab_bar.content = build_tab_row()
                    content_container.content = tab_contents[idx]
                    tab_bar.update()
                    content_container.update()

                return ft.Row([
                    ft.Container(
                        content=ft.Text(
                            label,
                            size=14,
                            weight="bold" if i == selected_index else "normal",
                            color=ft.Colors.BLUE if i == selected_index else ft.Colors.GREY_600,
                        ),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                        border=ft.Border(
                            bottom=ft.BorderSide(
                                2, ft.Colors.BLUE if i == selected_index else ft.Colors.TRANSPARENT
                            )
                        ),
                        on_click=lambda _, idx=i: on_tab_click(idx),
                        ink=True,
                    )
                    for i, label in enumerate(tab_labels)
                ], spacing=0)

            tab_bar = ft.Container(
                content=build_tab_row(),
                bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK_12, offset=ft.Offset(0, 2)),
            )

            content_container = ft.Container(
                content=tab_contents[selected_index],
                expand=True,
                padding=ft.Padding.symmetric(horizontal=15, vertical=15),
            )

            return ft.Column([
                tab_bar,
                content_container,
            ], expand=True, spacing=0)

        refresh()

        return ft.Column([
            ft.Container(
                content=ft.Text("我的订单", size=20, weight="bold"),
                padding=ft.Padding(20, 25, 20, 15),
                bgcolor=ft.Colors.WHITE,
            ),
            tabs_container,
        ], expand=True, spacing=0)

    def build_order_detail(self, order_id: str):
        """订单详情页"""
        phone = self.app.config.get("last_user")
        order = self.app.user_manager.get_order_by_id(phone, order_id)

        if not order:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=100, color=ft.Colors.GREY_400),
                    ft.Text("订单不存在", size=20, weight="bold"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
            )

        drone = self.app.drone_manager.get_by_id(order["drone_id"])

        status_color = {
            "待配送": ft.Colors.ORANGE,
            "租赁中": ft.Colors.BLUE,
            "已完成": ft.Colors.GREEN,
            "已取消": ft.Colors.GREY_500
        }

        status_icon = {
            "待配送": ft.Icons.LOCAL_SHIPPING_OUTLINED,
            "租赁中": ft.Icons.FLIGHT,
            "已完成": ft.Icons.CHECK_CIRCLE_OUTLINE,
            "已取消": ft.Icons.CANCEL_OUTLINED
        }

        # 状态时间轴
        all_statuses = ["待配送", "租赁中", "已完成"]
        current = order.get("status")

        def build_timeline():
            if current == "已取消":
                return ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CANCEL_OUTLINED, color=ft.Colors.RED_400, size=20),
                        ft.Text("订单已取消", size=14, color=ft.Colors.RED_400),
                    ], spacing=8),
                    padding=ft.Padding.symmetric(vertical=10),
                )

            nodes = []
            for i, s in enumerate(all_statuses):
                is_done = all_statuses.index(current) >= i if current in all_statuses else False
                nodes.append(
                    ft.Column([
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.CHECK_CIRCLE if is_done else ft.Icons.RADIO_BUTTON_UNCHECKED,
                                color=ft.Colors.BLUE if is_done else ft.Colors.GREY_400,
                                size=20,
                            ),
                        ),
                        ft.Text(s, size=11,
                                color=ft.Colors.BLUE if is_done else ft.Colors.GREY_400),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
                )
                if i < len(all_statuses) - 1:
                    nodes.append(
                        ft.Container(
                            width=50, height=2,
                            bgcolor=ft.Colors.BLUE if all_statuses.index(current) > i else ft.Colors.GREY_300,
                            margin=ft.Margin.only(bottom=18),
                        )
                    )

            return ft.Row(nodes, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        def on_cancel():
            def confirm_cancel():
                self.app.user_manager.update_order_status(phone, order_id, "已取消")
                dialog.open = False
                self.goto("order_detail", order_id=order_id)

            def on_close():
                dialog.open = False
                self.app.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("取消订单", weight="bold"),
                content=ft.Text("确认取消该订单？此操作不可撤销。"),
                actions=[
                    ft.TextButton("返回", on_click=on_close),
                    ft.Button(
                        "确认取消",
                        bgcolor=ft.Colors.RED_400,
                        color=ft.Colors.WHITE,
                        on_click=confirm_cancel,
                    ),
                ],
            )
            self.app.page.overlay.append(dialog)
            dialog.open = True
            self.app.page.update()

        def info_row(icon, label, value):
            return ft.Row([
                ft.Icon(icon, size=16, color=ft.Colors.GREY_500),
                ft.Text(label, size=13, color=ft.Colors.GREY_600, width=70),
                ft.Text(value, size=13, expand=True),
            ], spacing=10)

        statuses = ["租赁中", "待配送", "已完成", "已取消"]

        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda: self.goto("orders", selected_index=statuses.index(current))),
                    ft.Text("订单详情", size=20, weight="bold", expand=True),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            ft.Container(
                content=ft.Column([

                    # ========== 状态卡片 ==========
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(
                                    status_icon.get(current, ft.Icons.INFO),
                                    color=status_color.get(current, ft.Colors.GREY_400),
                                    size=28,
                                ),
                                ft.Column([
                                    ft.Text(current, size=18, weight="bold",
                                            color=status_color.get(current, ft.Colors.GREY_400)),
                                    ft.Text(f"订单号：{order['id']}", size=11, color=ft.Colors.GREY_500),
                                ], spacing=2, expand=True),
                            ], spacing=12),
                            ft.Container(height=15),
                            build_timeline()
                        ]),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    ),

                    ft.Container(height=15),

                    # ========== 机型信息 ==========
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(drone["images"][0] if drone else "🚁", size=50),
                                width=80, height=80,
                                bgcolor=ft.Colors.BLUE_50,
                                border_radius=12,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column([
                                ft.Text(order["drone_name"], size=16, weight="bold"),
                                ft.Text(drone["specs"] if drone else "", size=13, color=ft.Colors.GREY_600),
                            ], spacing=4, expand=True),
                        ], spacing=15),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    ),

                    ft.Container(height=15),

                    # ========== 租赁信息 ==========
                    ft.Container(
                        content=ft.Column([
                            ft.Text("租赁信息", size=15, weight="bold"),
                            ft.Container(height=10),
                            info_row(ft.Icons.LOCATION_ON, "装货地址", order["start_address"]),
                            ft.Divider(height=12, color=ft.Colors.GREY_100),
                            info_row(ft.Icons.LOCATION_ON, "收货地址", order["address"]),
                            ft.Divider(height=12, color=ft.Colors.GREY_100),
                            info_row(ft.Icons.PLAY_CIRCLE_OUTLINE, "开始时间", order["start_time"]),
                            ft.Divider(height=12, color=ft.Colors.GREY_100),
                            info_row(ft.Icons.CALENDAR_TODAY, "下单时间", order["created_at"]),
                        ]),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    ),

                    ft.Container(height=15),

                    # ========== 费用明细 ==========
                    ft.Container(
                        content=ft.Column([
                            ft.Text("费用明细", size=15, weight="bold"),
                            ft.Container(height=10),
                            ft.Row([
                                ft.Text("租赁费用", size=14, color=ft.Colors.GREY_600, expand=True),
                                ft.Text(f"¥{order['total_price']}", size=14),
                            ]),
                            ft.Divider(height=12, color=ft.Colors.GREY_100),
                            ft.Row([
                                ft.Text("实付金额", size=15, weight="bold", expand=True),
                                ft.Text(f"¥{order['total_price']}", size=20,
                                        color=ft.Colors.RED_700, weight="bold"),
                            ]),
                        ]),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    ),

                    ft.Container(height=25),

                    # ========== 取消按钮 ==========
                    ft.Button(
                        "取消订单",
                        width=float("inf"),
                        height=55,
                        bgcolor=ft.Colors.RED_400,
                        color=ft.Colors.WHITE,
                        on_click=on_cancel,
                        visible=current == "待配送",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    ),

                    ft.Container(height=10),

                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=20,
            ),
        ], expand=True)

    def build_personal_info(self):
        """个人信息编辑页面"""
        # 1. 获取现有配置数据
        phone = self.app.config.get("last_user")
        username = self.app.user_manager.get(phone)["nick_name"]
        gender_val = self.app.user_manager.get(phone)["gender"]
        birthday_val = self.app.user_manager.get(phone)["birthday"]

        user_avatar = ft.CircleAvatar(
            content=ft.Icon(ft.Icons.PERSON, size=40),
            radius=50,
            foreground_image_src=FileReader.read_img(f"{phone}.png")
        )

        file_picker = ft.FilePicker()

        async def select():
            files = await file_picker.pick_files(
                file_type=ft.FilePickerFileType.IMAGE, 
                with_data=True
                )
            
            user_avatar.foreground_image_src = files[0].bytes
            user_avatar.update()

        # --- UI 控件定义 ---
        # 昵称
        nickname_field = ft.TextField(
            label="昵称", value=username, border_radius=10, width=350
        )

        # 性别下拉选择
        gender_dropdown = ft.Dropdown(
            label="性别",
            value=gender_val,
            options=[
                ft.dropdown.Option("男"),
                ft.dropdown.Option("女"),
                ft.dropdown.Option("保密"),
            ],
            border_radius=10,
            width=350,
        )

        # 出生日期显示（设为只读，通过弹窗修改）
        birthday_field = ft.TextField(
                label="出生日期",
                value=birthday_val,
                read_only=True,
                border_radius=10,
                width=310,
                hint_text="点击图标选择日期",
            )

        # 日期选择器逻辑
        def on_date_change(e):
            picked_date = e.control.value
            local_date = picked_date.astimezone()
            selected_date_str = local_date.strftime("%Y-%m-%d")
            birthday_field.value = selected_date_str
            birthday_field.update()

        date_picker = ft.DatePicker(
            value = datetime.datetime.strptime(birthday_val, "%Y-%m-%d") if birthday_val else None,
            on_change=on_date_change,
            first_date=datetime.datetime(1900, 1, 1),
            last_date=datetime.datetime.now().astimezone(),
        )

        def on_save_click():
            new_nickname = nickname_field.value.strip()
            if not new_nickname:
                self.show_snackbar("昵称不能为空", ft.Colors.RED_400)
                return

            avatar_bytes = user_avatar.foreground_image_src

            if avatar_bytes is not None:
                FileWriter.save_avatar(f"{phone}.png", avatar_bytes)

            # 保存所有信息到配置
            self.app.user_manager.update_value(phone, new_nickname, gender_dropdown.value, birthday_field.value)

            self.show_snackbar("个人信息已保存", ft.Colors.GREEN_400)

        # --- 页面布局 ---
        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.goto("settings")),
                    ft.Text("个人信息", size=20, weight="bold", expand=True),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            # 主要内容
            ft.Container(
                content=ft.Column([
                    ft.Container(height=20),
                    # 头像区域
                    ft.Column([
                        user_avatar,
                        ft.TextButton("更换头像", icon=ft.Icons.CAMERA_ALT_OUTLINED, on_click=select),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                    # 表单区域
                    ft.Column([
                        nickname_field,
                        gender_dropdown,
                        # 日期输入框配合选择图标
                        ft.Row([
                            birthday_field,
                            ft.IconButton(
                                icon=ft.Icons.CALENDAR_MONTH,
                                on_click=lambda: self.app.page.show_dialog(date_picker),
                                icon_color=ft.Colors.BLUE,
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                    ft.Container(height=30),
                    # 保存按钮
                    ft.Button(
                        "保存修改", width=350, height=55, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE,
                        on_click=on_save_click,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    ),
                ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True,
                padding=20,
            )
        ], expand=True)

    def build_change_password(self):
        """修改密码页面"""
        phone = self.app.config.get("last_user")

        current_password_field = ft.TextField(
            label="当前密码",
            hint_text="请输入当前密码",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            width=350,
        )

        new_password_field = ft.TextField(
            label="新密码",
            hint_text="请输入新密码（至少6位）",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            width=350,
        )

        confirm_password_field = ft.TextField(
            label="确认新密码",
            hint_text="请再次输入新密码",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            width=350,
        )

        def on_save_click():
            current = current_password_field.value
            new_pwd = new_password_field.value
            confirm = confirm_password_field.value

            if not current:
                self.show_snackbar("请输入当前密码", ft.Colors.RED_400)
                return

            if not self.app.user_manager.verify_login(phone, current):
                self.show_snackbar("当前密码错误", ft.Colors.RED_400)
                return

            if not new_pwd:
                self.show_snackbar("请输入新密码", ft.Colors.RED_400)
                return

            if len(new_pwd) < 6:
                self.show_snackbar("新密码至少需要6位", ft.Colors.RED_400)
                return

            if new_pwd == current:
                self.show_snackbar("新密码不能与当前密码相同", ft.Colors.RED_400)
                return

            if new_pwd != confirm:
                self.show_snackbar("两次输入的密码不一致", ft.Colors.RED_400)
                return

            self.app.user_manager.update_password(phone, new_pwd)
            self.show_snackbar("密码修改成功", ft.Colors.GREEN_400)

            # 清空输入框
            current_password_field.value = ""
            new_password_field.value = ""
            confirm_password_field.value = ""
            self.app.page.update()

        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.goto("settings")),
                    ft.Text("修改密码", size=20, weight="bold", expand=True),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            ft.Container(
                content=ft.Column([
                    ft.Container(height=20),

                    ft.Container(
                        content=ft.Icon(ft.Icons.LOCK_RESET, size=80, color=ft.Colors.BLUE),
                        alignment=ft.Alignment.CENTER,
                    ),

                    ft.Container(height=20),

                    ft.Text("修改密码", size=24, weight="bold", text_align=ft.TextAlign.CENTER),
                    ft.Text("请验证当前密码后设置新密码", size=14,
                            color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),

                    ft.Container(height=30),

                    current_password_field,
                    ft.Container(height=10),
                    ft.Divider(),
                    ft.Container(height=10),
                    new_password_field,
                    ft.Container(height=10),
                    confirm_password_field,

                    ft.Container(height=30),

                    ft.Button(
                        "确认修改", width=350, height=55,
                        bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE,
                        on_click=on_save_click,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=20,
            ),
        ], expand=True)

    def build_change_phone(self):
        """手机换绑页面"""
        phone = self.app.config.get("last_user")

        new_phone_field = ft.TextField(
            label="新手机号",
            hint_text="请输入新手机号",
            prefix_icon=ft.Icons.PHONE,
            border_radius=10,
            width=350,
            keyboard_type=ft.KeyboardType.PHONE,
        )

        password_field = ft.TextField(
            label="当前密码",
            hint_text="请输入当前密码验证身份",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            width=350,
        )

        def on_save_click():
            new_phone = new_phone_field.value
            password = password_field.value

            if not password:
                self.show_snackbar("请输入当前密码", ft.Colors.RED_400)
                return

            if not self.app.user_manager.verify_login(phone, password):
                self.show_snackbar("密码错误", ft.Colors.RED_400)
                return

            if not new_phone:
                self.show_snackbar("请输入新手机号", ft.Colors.RED_400)
                return

            phone_pattern = r"^1[3-9]\d{9}$"
            if not re.match(phone_pattern, new_phone):
                self.show_snackbar("请输入正确的11位手机号码", ft.Colors.RED_400)
                return

            if new_phone == phone:
                self.show_snackbar("新手机号不能与当前手机号相同", ft.Colors.RED_400)
                return

            if not self.app.user_manager.update_key(phone, new_phone):
                self.show_snackbar("该手机号已被注册", ft.Colors.RED_400)
                return

            self.app.config.set("last_user", new_phone)
            self.show_snackbar("手机号换绑成功", ft.Colors.GREEN_400)
            self.goto("settings")

        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.goto("settings")),
                    ft.Text("手机换绑", size=20, weight="bold", expand=True),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            ft.Container(
                content=ft.Column([
                    ft.Container(height=20),

                    ft.Container(
                        content=ft.Icon(ft.Icons.PHONE_ANDROID, size=80, color=ft.Colors.BLUE),
                        alignment=ft.Alignment.CENTER,
                    ),

                    ft.Container(height=20),

                    ft.Text("手机换绑", size=24, weight="bold", text_align=ft.TextAlign.CENTER),
                    ft.Text(
                        f"当前手机号：{phone[:3]}****{phone[7:]}",
                        size=14, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER,
                    ),

                    ft.Container(height=30),

                    password_field,
                    ft.Container(height=10),
                    ft.Divider(),
                    ft.Container(height=10),
                    new_phone_field,

                    ft.Container(height=30),

                    ft.Button(
                        "确认换绑", width=350, height=55,
                        bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE,
                        on_click=on_save_click,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=20,
            ),
        ], expand=True)

    async def get_current_loaction(self) -> str:
        gl = ftg.Geolocator()
        pos = await gl.get_current_position()
        lat, lng = pos.latitude, pos.longitude

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://restapi.amap.com/v3/assistant/coordinate/convert",
                params={
                    "key": self.app.AMAP_KEY,
                    "locations": f"{lng:.6f},{lat:.6f}",
                    "coordsys": "gps"
                }
            ) as resp:
                data = await resp.json()
                pos = data.get("locations")
                lng_str, lat_str = pos.split(",")
                lng = f"{float(lng_str):.6f}"
                lat = f"{float(lat_str):.6f}"
                location = f"{lng},{lat}"
                return location

    async def get_addr_citycode(self, location: str) -> tuple[str, str]:
        """定位获取当前位置和citycode"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://restapi.amap.com/v3/geocode/regeo",
                    params={
                        "key": self.app.AMAP_KEY,
                        "location": location
                        }
                ) as resp:
                    data = await resp.json()
                    if data.get("status") == "1":
                        return data.get("regeocode").get("formatted_address"), data.get("regeocode").get("addressComponent").get("citycode")
        except Exception as e:
            print(f"定位失败: {e}")

    async def search_tips(self, keyword: str, location: str, citycode: str) -> list:
        """输入提示补全"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://restapi.amap.com/v3/assistant/inputtips",
                    params={
                        "key": self.app.AMAP_KEY,
                        "keywords": keyword,
                        "location": location,
                        "city": citycode
                    }
                ) as resp:
                    data = await resp.json()
                    if data.get("status") == "1":
                        return data.get("tips", [])
                    else:
                        return []
        except Exception as e:
            print(f"输入提示失败: {e}")
            return []

    async def show_address_dialog(self, phone, refresh, existing=None):
        """新增或编辑地址弹窗"""
        is_edit = existing is not None

        # 获取城市和坐标
        location = await self.get_current_loaction()
        addr, citycode = await self.get_addr_citycode(location)

        tips_column = ft.Column([], spacing=0)
        debounce_task = None
        selected_loaction = None
        async def on_input_change():
            tips_column.controls.clear()

            keyword = address_field.value
            if not keyword:
                self.app.page.update()
                return

            # 取消上一个还没执行的任务
            nonlocal debounce_task
            if debounce_task:
                debounce_task.cancel()

            async def delayed_search():
                await asyncio.sleep(0.5)
                tips = await self.search_tips(keyword, location, citycode)

                for tip in tips[:6]:
                    name = tip.get("name", "")
                    district = tip.get("district", "")
                    address = tip.get("address", "")
                    tip_location = tip.get("location")
                    full = f"{district}{name}" if not address else f"{district}{name} {address}"

                    def on_tip_click(_, f=full, l=tip_location):
                        address_field.value = f
                        nonlocal selected_loaction
                        selected_loaction = tip_location
                        tips_column.controls.clear()
                        self.app.page.update()

                    tips_column.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(name, size=14, weight="bold"),
                                ft.Text(f"{district} {address}", size=12, color=ft.Colors.GREY_600),
                            ], spacing=2),
                            padding=ft.Padding(15, 10, 15, 10),
                            on_click=on_tip_click,
                            ink=True,
                            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
                        )
                    )

                self.app.page.update()

            debounce_task = self.app.page.run_task(delayed_search)

        address_field = ft.TextField(
            label="搜索地址",
            hint_text="输入地址关键词...",
            value=existing["address"] if is_edit else "",
            border_radius=10,
            width=400,
            prefix_icon=ft.Icons.SEARCH,
            on_change=on_input_change
        )

        def on_confirm():
            address = address_field.value
            if not address:
                self.show_snackbar("请选择或输入地址", ft.Colors.RED_400)
                return

            if is_edit:
                self.app.user_manager.update_address(phone, existing["id"], address)
                self.show_snackbar("地址已更新", ft.Colors.GREEN_400)
            else:
                self.app.user_manager.add_address(phone, address, selected_loaction)
                self.show_snackbar("地址已添加", ft.Colors.GREEN_400)

            dialog.open = False
            self.app.page.update()
            refresh()

        def on_cancel():
            dialog.open = False
            self.app.page.update()

        # 定位按钮，显示当前城市
        location_hint = ft.Row([
            ft.Icon(ft.Icons.MY_LOCATION, size=14, color=ft.Colors.BLUE),
            ft.Text(
                f"已定位到：{addr}" if addr else "定位失败，请手动输入",
                size=12,
                color=ft.Colors.BLUE if addr else ft.Colors.GREY_500,
            ),
        ], spacing=4)

        dialog = ft.AlertDialog(
            title=ft.Text("编辑地址" if is_edit else "新增地址", weight="bold"),
            content=ft.Container(
                content=ft.Column([
                    location_hint,
                    ft.Container(height=8),
                    address_field,
                    ft.Container(
                        content=tips_column,
                        border_radius=10,
                        bgcolor=ft.Colors.WHITE,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                        visible=True,
                    ),
                ], spacing=4),
                width=400,
                padding=ft.Padding(0, 10, 0, 0),
            ),
            actions=[
                ft.TextButton("取消", on_click=on_cancel),
                ft.Button(
                    "确认",
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                    on_click=on_confirm,
                ),
            ],
        )
        self.app.page.overlay.append(dialog)
        dialog.open = True
        self.app.page.update()

    def build_address_list(self, phone, refresh, drone_id=None, is_booking=False, selected_address=None, start_address=None, is_start=False):
        addresses = self.app.user_manager.get_addresses(phone)

        def on_delete(addr_id):
            self.app.user_manager.delete_address(phone, addr_id)
            refresh()

        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLUE, size=20),
                    ft.Text(
                        addr["address"], 
                        size=14,
                        expand=True
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_color=ft.Colors.BLUE,
                        on_click=lambda _, addr=addr: self.app.page.run_task(self.show_address_dialog, phone, refresh, addr),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda _, id=addr["id"]: on_delete(id),
                    ),
                    ft.TextButton(
                        "设为默认" if index else "默认地址",
                        on_click=lambda _, id=addr["id"]: (
                            self.app.user_manager.set_default_address(phone, id),
                            refresh()
                        ) if index else None,
                        style=ft.ButtonStyle(color=ft.Colors.BLUE),
                    )
                ]),
                padding=ft.Padding(20, 15, 10, 15),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                on_click=lambda _, addr=addr["address"]: self.goto("order", drone_id=drone_id, is_booking=is_booking, selected_address=addr if not is_start else selected_address, start_address=addr if is_start else start_address) if drone_id else None
            )
            for index, addr in enumerate(addresses)
        ], spacing=12)

    def build_addresses(self):
        """常用地址页面"""
        phone = self.app.config.get("last_user")

        list_container = ft.Container(expand=True)

        def refresh():
            list_container.content = self.build_address_list(phone, refresh)
            self.app.page.update()

        refresh()

        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda: self.goto("settings")),
                    ft.Text("常用地址", size=20, weight="bold", expand=True),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=ft.Colors.BLUE,
                        on_click=lambda: self.app.page.run_task(self.show_address_dialog, phone, refresh),
                    ),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            ft.Container(
                content=ft.Column([
                    list_container,
                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=20,
            ),
        ], expand=True)

    def build_privacy_settings(self):
        """隐私设置页面"""

        def show_document(title, filename):
            content = FileReader.read_txt(filename)

            def close_dialog():
                dialog.open = False
                self.app.page.update()

            dialog = ft.AlertDialog(
                title=ft.Text(title, weight="bold"),
                content=ft.Container(
                    content=ft.Text(content, selectable=True),
                    width=500,
                    height=400,
                    padding=20,
                ),
                actions=[ft.TextButton("关闭", on_click=close_dialog)],
                scrollable=True,
            )
            self.app.page.overlay.append(dialog)
            dialog.open = True
            self.app.page.update()

        def show_delete_dialog():
            def on_confirm():
                phone = self.app.config.get("last_user")
                self.app.user_manager.delete(phone)
                self.app.config.logout()
                confirm_dialog.open = False
                self.app.page.update()
                self.goto("profile")

            def on_cancel():
                confirm_dialog.open = False
                self.app.page.update()

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("删除账号", weight="bold"),
                content=ft.Text("此操作不可逆，账号及所有数据将被永久删除，确认继续？"),
                actions=[
                    ft.TextButton("取消", on_click=on_cancel),
                    ft.Button(
                        "确认删除",
                        bgcolor=ft.Colors.RED_400,
                        color=ft.Colors.WHITE,
                        on_click=on_confirm,
                    ),
                ],
            )
            self.app.page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            self.app.page.update()

        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.goto("settings")),
                    ft.Text("隐私设置", size=20, weight="bold", expand=True),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            ft.Container(
                content=ft.Column([

                    # ========== 隐私说明 ==========
                    ft.Container(
                        content=ft.Text("隐私说明", size=16, weight="bold", color=ft.Colors.BLUE_700),
                        padding=ft.Padding.only(left=5, top=20, bottom=10),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PRIVACY_TIP_OUTLINED),
                        title=ft.Text("隐私政策"),
                        subtitle=ft.Text("了解我们如何收集和使用您的数据"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                        on_click=lambda: show_document("隐私政策", "privacy_policy_text.txt"),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED),
                        title=ft.Text("用户协议"),
                        subtitle=ft.Text("查看用户服务协议"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                        on_click=lambda: show_document("用户协议", "user_agreement_text.txt"),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED),
                        title=ft.Text("应用权限说明"),
                        subtitle=ft.Text("定位、存储等权限的使用说明"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                        on_click=lambda: show_document("应用权限说明", "app_permission_text.txt"),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.CHILD_CARE),
                        title=ft.Text("未成年人保护"),
                        subtitle=ft.Text("未成年人使用须知"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                        on_click=lambda: show_document("未成年人保护", "minor_protection_text.txt"),
                    ),

                    # ========== 账号与数据 ==========
                    ft.Container(
                        content=ft.Text("账号与数据", size=16, weight="bold", color=ft.Colors.BLUE_700),
                        padding=ft.Padding.only(left=5, top=25, bottom=10),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DELETE_FOREVER_OUTLINED, color=ft.Colors.RED_400),
                        title=ft.Text("删除账号", color=ft.Colors.RED_400),
                        subtitle=ft.Text("永久删除账号及所有数据"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                        on_click=show_delete_dialog,
                    ),

                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=ft.Padding.symmetric(horizontal=20),
            ),
        ], expand=True)

    def build_help_center(self):
        """帮助中心页面"""

        faqs = [
            {
                "question": "如何租赁无人机？",
                "answer": "在首页选择心仪的无人机型号，点击立即租赁，填写收货地址和租赁时长，完成支付后无人机将从就近机库配送到您指定的地址。"
            },
            {
                "question": "租赁费用如何计算？",
                "answer": "租赁费用按天计算，不同机型价格不同。订单确认后费用将一次性扣除，超时使用将按小时补收费用。"
            },
            {
                "question": "如何归还无人机？",
                "answer": "租赁到期前，您可以在订单页面申请上门回收，无人机将自动飞回就近机库。请确保设备电量不低于20%。"
            },
            {
                "question": "设备损坏怎么办？",
                "answer": "如因正常使用造成损坏，请在订单页面提交报修申请，我们将安排检测。人为损坏将根据损坏程度收取相应赔偿费用。"
            },
            {
                "question": "哪些区域禁止飞行？",
                "answer": "机场净空区、军事禁区、政府机关上空等敏感区域禁止飞行。飞行高度一般不超过120米。请在飞行前查阅当地法规，违规飞行责任自负。"
            },
            {
                "question": "如何申请退款？",
                "answer": "租赁开始前可申请全额退款。租赁开始后如遇设备故障，可申请部分退款。请在订单页面提交退款申请，客服将在1-3个工作日内处理。"
            },
            {
                "question": "忘记密码怎么办？",
                "answer": "在登录页面点击忘记密码，通过绑定手机号验证身份后即可重置密码。"
            }
        ]

        def build_faq_item(faq):
            expanded = {"value": False}
            answer_container = ft.Container(
                content=ft.Text(faq["answer"], size=13, color=ft.Colors.GREY_700),
                padding=ft.Padding(15, 0, 15, 15),
                visible=False,
            )
            chevron = ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400, size=20)

            def on_toggle(e):
                expanded["value"] = not expanded["value"]
                answer_container.visible = expanded["value"]
                chevron.name = ft.Icons.EXPAND_LESS if expanded["value"] else ft.Icons.CHEVRON_RIGHT
                self.app.page.update()

            return ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.BLUE, size=18),
                            ft.Text(faq["question"], size=14, weight="bold", expand=True),
                            chevron,
                        ], spacing=10),
                        padding=ft.Padding(15, 12, 15, 12),
                        on_click=on_toggle,
                        ink=True,
                    ),
                    answer_container,
                ], spacing=0),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
            )

        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.goto("settings")),
                    ft.Text("帮助中心", size=20, weight="bold", expand=True),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            ft.Container(
                content=ft.Column([

                    # ========== 常见问题 ==========
                    ft.Container(
                        content=ft.Text("常见问题", size=16, weight="bold", color=ft.Colors.BLUE_700),
                        padding=ft.Padding.only(left=5, top=10, bottom=10),
                    ),
                    ft.Column([
                        build_faq_item(faq) for faq in faqs
                    ], spacing=10),

                    # ========== 联系客服 ==========
                    ft.Container(
                        content=ft.Text("联系客服", size=16, weight="bold", color=ft.Colors.BLUE_700),
                        padding=ft.Padding.only(left=5, top=25, bottom=10),
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PHONE_OUTLINED, color=ft.Colors.BLUE, size=20),
                                ft.Text("客服电话", size=14, color=ft.Colors.GREY_700, width=80),
                                ft.Text("400-888-9999", size=14, weight="bold"),
                            ], spacing=10),
                            ft.Divider(height=1, color=ft.Colors.GREY_200),
                            ft.Row([
                                ft.Icon(ft.Icons.EMAIL_OUTLINED, color=ft.Colors.BLUE, size=20),
                                ft.Text("客服邮箱", size=14, color=ft.Colors.GREY_700, width=80),
                                ft.Text("support@dronegoo.com", size=14, weight="bold"),
                            ], spacing=10),
                            ft.Divider(height=1, color=ft.Colors.GREY_200),
                            ft.Row([
                                ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.BLUE, size=20),
                                ft.Text("服务时间", size=14, color=ft.Colors.GREY_700, width=80),
                                ft.Text("每日 09:00 - 21:00", size=14, weight="bold"),
                            ], spacing=10),
                        ], spacing=12),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    ),

                    ft.Container(height=20),
                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=ft.Padding.symmetric(horizontal=20),
            ),
        ], expand=True)

    def build_settings(self):
        """构建设置页"""
        return ft.Column([
            # 顶部导航栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda: self.goto("profile")),
                    ft.Text("设置", size=20, weight="bold", expand=True),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            # 设置内容
            ft.Container(
                content=ft.Column([
                    # ==================== 账户相关 ====================
                    ft.Container(
                        content=ft.Text("账户", size=16, weight="bold", color=ft.Colors.BLUE_700),
                        padding=ft.Padding.only(left=20, top=20, bottom=10)
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON_OUTLINE),
                        title=ft.Text("个人信息"),
                        subtitle=ft.Text("修改昵称、头像、联系方式"),
                        on_click=lambda: self.goto("personal_info")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.LOCK_OUTLINE),
                        title=ft.Text("修改密码"),
                        subtitle=ft.Text("定期修改以保护账号安全"),
                        on_click=lambda: self.goto("change_password")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PHONE_ANDROID),
                        title=ft.Text("手机换绑"),
                        subtitle=ft.Text("更换绑定的手机号码"),
                        on_click=lambda _: self.goto("change_phone")
                    ),

                    # ==================== 租赁服务 ====================
                    ft.Container(
                        content=ft.Text("租赁偏好", size=16, weight="bold", color=ft.Colors.BLUE_700),
                        padding=ft.Padding.only(left=20, top=25, bottom=10)
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.LOCATION_ON_OUTLINED),
                        title=ft.Text("常用地址"),
                        subtitle=ft.Text("取机/还机地址管理"),
                        on_click=lambda: self.goto("addresses")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED),
                        title=ft.Text("租赁通知"),
                        subtitle=ft.Text("到期提醒、订单状态"),
                        trailing=ft.Switch(
                            value=self.app.config.get("notify_enabled"),
                            on_change=lambda e: self.app.config.set("notify_enabled", e.control.value)
                            )
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.HISTORY),
                        title=ft.Text("租赁记录"),
                        subtitle=ft.Text("查看历史租赁订单"),
                        on_click=lambda: self.goto("orders")
                    ),

                    # ==================== 其他设置 ====================
                    ft.Container(
                        content=ft.Text("其他", size=16, weight="bold", color=ft.Colors.BLUE_700),
                        padding=ft.Padding.only(left=20, top=25, bottom=10)
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.CACHED),
                        title=ft.Text("清除缓存"),
                        subtitle=ft.Text("释放空间"),
                        on_click=lambda: self.show_snackbar("缓存已清除", ft.Colors.GREEN_400)
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PRIVACY_TIP_OUTLINED),
                        title=ft.Text("隐私设置"),
                        subtitle=ft.Text("数据使用与权限"),
                        on_click=lambda: self.goto("privacy_settings")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.HELP_OUTLINE),
                        title=ft.Text("帮助中心"),
                        subtitle=ft.Text("常见问题与客服"),
                        on_click=lambda: self.goto("help_center")
                    ),
                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
            )
        ], expand=True)

    def build_profile(self):
        """构建我的页面"""
        phone = self.app.config.get("last_user")
        username = self.app.user_manager.get(phone).get("nick_name") if phone else "游客"
        is_logged_in = bool(phone)

        def on_logout_click():
            """退出登录"""
            self.app.config.logout()
            self.goto("profile")
        
        user_card = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.CircleAvatar(foreground_image_src=FileReader.read_img(f"{phone}.png"), radius=40),
                    width=70,
                    height=70,
                    bgcolor=ft.Colors.BLUE_100,
                    border_radius=35,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text(username, size=20, weight="bold"),
                    ft.Text(
                        "会员用户" if is_logged_in else "点击登录",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    on_click=lambda _, is_logged_in=is_logged_in: self.goto("settings") if is_logged_in else self.show_snackbar("请先登录", ft.Colors.RED_400),
                ),
            ]),
            bgcolor=ft.Colors.BLUE_50,
            padding=20,
            border_radius=15,
            on_click=lambda: self.goto("login") if not is_logged_in else None,
        )
        
        menu_items = ft.Container(
            content=ft.Row([
                self.build_menu_item(ft.Icons.RECEIPT_LONG, "我的订单"),
                self.build_menu_item(ft.Icons.FAVORITE, "收藏夹"),
                self.build_menu_item(ft.Icons.CARD_GIFTCARD, "优惠券"),
                self.build_menu_item(ft.Icons.HEADSET_MIC, "客服"),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            padding=ft.Padding.symmetric(vertical=20),
        )
        
        settings_section = ft.Column([
            ft.Container(
                content=ft.Text("设置", size=16, weight="bold"),
                padding=ft.Padding.only(left=20, top=10, bottom=10),
            ),
            self._list_item(ft.Icons.LANGUAGE, "语言设置", "中文"),
            self._list_item(ft.Icons.DARK_MODE_OUTLINED, "深色模式", "关闭"),
            self._list_item(ft.Icons.INFO_OUTLINE, "关于我们"),
        ])
        
        logout_section = ft.Column([
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Container(
                content=ft.TextButton(
                    "退出登录",
                    icon=ft.Icons.LOGOUT,
                    on_click=lambda: on_logout_click(),
                    style=ft.ButtonStyle(color=ft.Colors.RED_400),
                ),
                alignment=ft.Alignment.CENTER,
            ),
        ]) if is_logged_in else ft.Container()
        
        return ft.Column([
            user_card,
            menu_items,
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            settings_section,
            logout_section,
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    def build_forget(self):
        """忘记密码页面"""
        phone_field = ft.TextField(
            label="手机号",
            hint_text="请输入注册手机号",
            prefix_icon=ft.Icons.PHONE,
            border_radius=10,
            width=350,
            keyboard_type=ft.KeyboardType.PHONE,
        )

        new_password_field = ft.TextField(
            label="新密码",
            hint_text="请输入新密码（至少6位）",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            width=350,
            visible=False,
        )

        confirm_password_field = ft.TextField(
            label="确认新密码",
            hint_text="请再次输入新密码",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            width=350,
            visible=False,
        )

        verified = False
        def on_submit():
            nonlocal verified
            if not verified:
                # 第一步：验证手机号
                phone = phone_field.value
                if not phone:
                    self.show_snackbar("请输入手机号", ft.Colors.RED_400)
                    return

                phone_pattern = r"^1[3-9]\d{9}$"
                if not re.match(phone_pattern, phone):
                    self.show_snackbar("请输入正确的11位手机号码", ft.Colors.RED_400)
                    return

                if not self.app.user_manager.contains(phone):
                    self.show_snackbar("该手机号未注册", ft.Colors.RED_400)
                    return

                # 验证通过，展示密码输入框
                verified = True
                phone_field.read_only = True
                new_password_field.visible = True
                confirm_password_field.visible = True
                submit_btn.content = "确认重置"
                self.app.page.update()

            else:
                # 第二步：重置密码
                new_pwd = new_password_field.value
                confirm = confirm_password_field.value
                phone = phone_field.value

                if not new_pwd:
                    self.show_snackbar("请输入新密码", ft.Colors.RED_400)
                    return

                if len(new_pwd) < 6:
                    self.show_snackbar("新密码至少需要6位", ft.Colors.RED_400)
                    return

                if new_pwd != confirm:
                    self.show_snackbar("两次输入的密码不一致", ft.Colors.RED_400)
                    return

                self.app.user_manager.update_password(phone, new_pwd)
                self.show_snackbar("密码重置成功，请重新登录", ft.Colors.GREEN_400)
                self.goto("login")

        submit_btn = ft.Button(
            "验证手机号",
            width=350, height=55,
            bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            on_click=on_submit
        )

        return ft.Container(
            content=ft.Column([
                # 顶部栏
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.goto("login")),
                        ft.Text("忘记密码", size=20, weight="bold"),
                    ]),
                    padding=ft.Padding.only(left=10, right=20, top=20, bottom=10),
                ),

                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.LOCK_RESET, size=80, color=ft.Colors.BLUE),
                            alignment=ft.Alignment.CENTER,
                        ),

                        ft.Container(height=20),

                        ft.Text("重置密码", size=24, weight="bold", text_align=ft.TextAlign.CENTER),
                        ft.Text(
                            "验证注册手机号后即可设置新密码",
                            size=14, color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),

                        ft.Container(height=30),

                        phone_field,
                        ft.Container(height=10),
                        new_password_field,
                        ft.Container(height=10),
                        confirm_password_field,

                        ft.Container(height=30),

                        submit_btn,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    padding=20,
                ),
            ], spacing=0),
            expand=True,
            bgcolor=ft.Colors.WHITE,
        )

    def build_login(self):
        """构建登录页面"""
        phone_number_field = ft.TextField(
            label="手机号",
            hint_text="请输入手机号",
            prefix_icon=ft.Icons.PERSON,
            border_radius=10,
        )
        
        password_field = ft.TextField(
            label="密码",
            hint_text="请输入密码",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=10,
        )
        
        def on_login_submit():
            phone_number = phone_number_field.value
            password = password_field.value
            
            if not phone_number:
                self.show_snackbar("请输入手机号", ft.Colors.RED_400)
                return
            
            if not password:
                self.show_snackbar("请输入密码", ft.Colors.RED_400)
                return

            # 登录成功
            if self.app.user_manager.verify_login(phone_number, password):
                self.app.config.set("last_user", phone_number)
            else:
                self.show_snackbar("手机号或密码错误", ft.Colors.RED_400)
                return
            
            # 返回"我的"页面
            self.goto("profile")

        return ft.Container(
            content=ft.Column([
                # 顶部返回按钮
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda: self.goto("profile"),
                        ),
                        ft.Text("登录", size=20, weight="bold"),
                    ]),
                    padding=ft.Padding.only(left=10, right=20, top=20, bottom=10),
                ),
                
                # 登录表单区域
                ft.Container(
                    content=ft.Column([
                        # Logo 或图标
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.ACCOUNT_CIRCLE,
                                size=100,
                                color=ft.Colors.BLUE,
                            ),
                            alignment=ft.Alignment.CENTER,
                        ),
                        
                        ft.Container(height=30),
                        
                        # 欢迎文本
                        ft.Text(
                            "欢迎回来",
                            size=28,
                            weight="bold",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "登录您的 DroneGo 账户",
                            size=14,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        
                        ft.Container(height=40),
                        
                        # 输入框
                        phone_number_field,
                        ft.Container(height=15),
                        password_field,
                        
                        ft.Container(height=10),
                        
                        # 忘记密码
                        ft.Container(
                            content=ft.TextButton(
                                "忘记密码？",
                                on_click=lambda: self.goto("forget"),
                            ),
                            alignment=ft.Alignment.CENTER_RIGHT,
                        ),
                        
                        ft.Container(height=20),
                        
                        # 登录按钮
                        ft.Button(
                            "登录",
                            width=float("inf"),
                            height=50,
                            on_click=on_login_submit,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                        ),
                        
                        ft.Container(height=20),
                        
                        # 注册提示
                        ft.Row([
                            ft.Text("还没有账号？", size=14, color=ft.Colors.GREY_600),
                            ft.TextButton(
                                "立即注册",
                                on_click=lambda: self.goto("register"),
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                    expand=True,
                ),
            ], spacing=0),
            expand=True,
            bgcolor=ft.Colors.WHITE,
        )

    def build_register(self):
        """构建注册页面"""
        phone_number_field = ft.TextField(
            label="手机号",
            hint_text="请输入手机号",
            prefix_icon=ft.Icons.PERSON,
            border_radius=10,
        )
        
        password_field = ft.TextField(
            label="密码",
            hint_text="请输入密码（至少6位）",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=10,
        )
        
        confirm_password_field = ft.TextField(
            label="确认密码",
            hint_text="请再次输入密码",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_radius=10,
        )
        
        def show_document(title, filename):
            """显示协议文档"""
            content = FileReader.read_txt(filename)
            
            def close_dialog(e):
                dialog.open = False
                self.app.page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text(title, weight="bold"),
                content=ft.Container(
                    content=ft.Text(content, selectable=True),
                    width=500,
                    height=400,
                    padding=20,
                ),
                actions=[ft.TextButton("关闭", on_click=close_dialog)],
                scrollable=True,
            )
            self.app.page.overlay.append(dialog)
            dialog.open = True
            self.app.page.update()
        
        # 协议勾选区域（文本可点击）
        agree_checkbox = ft.Checkbox(value=False)
        
        agree_row = ft.Row([
            agree_checkbox,
            ft.Text("我已阅读并同意", size=13, color=ft.Colors.GREY_700),
            ft.TextButton(
                "《用户协议》",
                on_click=lambda: show_document("用户协议", "user_agreement_text.txt"),
                style=ft.ButtonStyle(
                    padding=0,
                ),
            ),
            ft.Text("和", size=13, color=ft.Colors.GREY_700),
            ft.TextButton(
                "《隐私政策》",
                on_click=lambda: show_document("隐私政策", "privacy_policy_text.txt"),
                style=ft.ButtonStyle(
                    padding=0,
                ),
            ),
        ], spacing=0, wrap=True)
        
        def on_register_submit():
            phone_number = phone_number_field.value
            password = password_field.value
            confirm_password = confirm_password_field.value

            # 验证手机号
            if not phone_number:
                self.show_snackbar("请输入手机号", ft.Colors.RED_400)
                return

            phone_pattern = r"^1[3-9]\d{9}$"
            if not re.match(phone_pattern, phone_number):
                self.show_snackbar("请输入正确的11位手机号码", ft.Colors.RED_400)
                return
            
            if self.app.user_manager.contains(phone_number):
                self.show_snackbar("手机号已注册，请登录", ft.Colors.RED_400)
                return

            # 验证密码
            if not password:
                self.show_snackbar("请输入密码", ft.Colors.RED_400)
                return
            
            if len(password) < 6:
                self.show_snackbar("密码至少需要6位", ft.Colors.RED_400)
                return
            
            # 验证确认密码
            if password != confirm_password:
                self.show_snackbar("两次输入的密码不一致", ft.Colors.RED_400)
                return
            
            # 检查协议勾选
            if not agree_checkbox.value:
                self.show_snackbar("请先阅读并同意用户协议", ft.Colors.RED_400)
                return
            
            # 注册成功
            self.app.user_manager.add(phone_number, f"用户{phone_number}", password)

            self.app.config.set("last_user", phone_number)

            snackbar = ft.SnackBar(
                content=ft.Text(f"注册成功！欢迎 用户{phone_number}"),
                bgcolor=ft.Colors.GREEN_400,
            )
            self.app.page.overlay.append(snackbar)
            snackbar.open = True
            self.app.page.update()

            self.goto("profile")
        
        return ft.Container(
            content=ft.Column([
                # 顶部返回按钮
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda: self.goto("login"),
                        ),
                        ft.Text("注册", size=20, weight="bold"),
                    ]),
                    padding=ft.Padding.only(left=10, right=20, top=20, bottom=10),
                ),
                
                # 注册表单区域
                ft.Container(
                    content=ft.Column([
                        # Logo
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.PERSON_ADD,
                                size=80,
                                color=ft.Colors.BLUE,
                            ),
                            alignment=ft.Alignment.CENTER,
                        ),
                        
                        ft.Container(height=20),
                        
                        # 标题
                        ft.Text(
                            "创建账户",
                            size=28,
                            weight="bold",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "加入 DroneGo 开启飞行之旅",
                            size=14,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        
                        ft.Container(height=30),
                        
                        # 输入框
                        phone_number_field,
                        ft.Container(height=15),
                        password_field,
                        ft.Container(height=15),
                        confirm_password_field,
                        
                        ft.Container(height=20),
                        
                        # 协议勾选（文本可点击）
                        agree_row,
                        
                        ft.Container(height=25),
                        
                        # 注册按钮
                        ft.Button(
                            "注册",
                            width=float("inf"),
                            height=50,
                            on_click=on_register_submit,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                        ),
                        
                        ft.Container(height=20),
                        
                        # 登录提示
                        ft.Row([
                            ft.Text("已有账号？", size=14, color=ft.Colors.GREY_600),
                            ft.TextButton(
                                "立即登录",
                                on_click=lambda: self.goto("login"),
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
                    padding=30,
                    expand=True,
                ),
            ], spacing=0),
            expand=True,
            bgcolor=ft.Colors.WHITE,
        )

    def build_address_picker(self, drone_id: str, is_booking: bool, selected_address=None, start_address=None, is_start=False):
        """地址选择页"""
        phone = self.app.config.get("last_user")

        list_container = ft.Container(expand=True)

        def refresh():
            list_container.content = self.build_address_list(phone, refresh, drone_id, is_booking, selected_address, start_address, is_start)
            self.app.page.update()

        refresh()

        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda: self.goto("order", drone_id=drone_id, is_booking=is_booking, selected_address=selected_address, start_address=start_address),
                    ),
                    ft.Text("选择地址", size=20, weight="bold", expand=True),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=ft.Colors.BLUE,
                        on_click=lambda: self.app.page.run_task(self.show_address_dialog, phone, refresh),
                    ),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            ft.Container(
                content=ft.Column([
                    list_container,
                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=20,
            ),
        ], expand=True)

    def calc_distance(self, loc1: str, loc2: str) -> float:
        """计算两点直线距离（km），坐标格式 'lng,lat'"""
        lng1, lat1 = map(float, loc1.split(","))
        lng2, lat2 = map(float, loc2.split(","))
        return geodesic((lat1, lng1), (lat2, lng2)).km

    def build_order(self, drone_id: str, is_booking: bool = False, selected_address: str = None, start_address: str = None):
        """下单页"""
        drone = self.app.drone_manager.get_by_id(drone_id)
        phone = self.app.config.get("last_user")
        addresses = self.app.user_manager.get_addresses(phone)

        # 默认选第一个地址
        if selected_address is None:
            selected_address = addresses[0]["address"] if addresses else ""

        # --- 地址选择 ---
        start_address_display = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLUE, size=20),
                ft.Text(
                    start_address or "请选择装货地址",
                    size=14,
                    expand=True,
                    color=ft.Colors.BLACK if start_address else ft.Colors.GREY_400,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
            ]),
            padding=ft.Padding(15, 12, 15, 12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=10,
            on_click=lambda: self.goto("address_picker", drone_id=drone_id, is_booking=is_booking, selected_address=selected_address, start_address=start_address, is_start=True),
            ink=True
        )

        address_display = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLUE, size=20),
                ft.Text(
                    selected_address or "请选择收货地址",
                    size=14,
                    expand=True,
                    color=ft.Colors.BLACK if selected_address else ft.Colors.GREY_400,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
            ]),
            padding=ft.Padding(15, 12, 15, 12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=10,
            on_click=lambda: self.goto("address_picker", drone_id=drone_id, is_booking=is_booking, selected_address=selected_address, start_address=start_address, is_start=False),
            ink=True
        )

        # --- 预约时间（仅预约租赁显示）---
        start_field = ft.TextField(
            label="预约开始时间",
            value=datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
            read_only=True,
            border_radius=10,
            hint_text="点击选择时间",
            prefix_icon=ft.Icons.CALENDAR_MONTH,
            visible=is_booking,
            width=310,
        )

        def update_start_field():
            dt = datetime.datetime.combine(date_picker.value.astimezone(), time_picker.value).astimezone()
            now = datetime.datetime.now().astimezone()

            if dt < now:
                dt = now

            start_field.value = dt.strftime("%Y-%m-%d %H:%M")
            start_field.update()

        date_picker = ft.DatePicker(
            value=datetime.datetime.now().astimezone(),
            on_change=update_start_field,
            first_date=datetime.datetime.now().astimezone(),
            last_date=datetime.datetime.now().astimezone() + datetime.timedelta(days=30),
        )

        time_picker = ft.TimePicker(
            on_change=update_start_field,
            confirm_text="确认",
            cancel_text="取消",
            help_text="选择时间",
        )

        start_row = ft.Row([
            start_field,
            ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                icon_color=ft.Colors.BLUE,
                on_click=lambda: self.app.page.show_dialog(date_picker),
                visible=is_booking,
                tooltip="选择日期",
            ),
            ft.IconButton(
                icon=ft.Icons.ACCESS_TIME,
                icon_color=ft.Colors.BLUE,
                on_click=lambda: self.app.page.show_dialog(time_picker),
                visible=is_booking,
                tooltip="选择时间",
            ),
        ], spacing=0)

        def get_price():
            if start_address is not None and selected_address is not None:
                if start_address == selected_address:
                    return "装收货地址不应相同"

                start_location = self.app.user_manager.get_location_by_address(phone, start_address)
                selected_location = self.app.user_manager.get_location_by_address(phone, selected_address)
                unit_price = drone["price"]

                dist = self.calc_distance(start_location, selected_location)
                total = unit_price * dist / 100.0

                if dist <= 3:
                    base = 6
                elif dist <= 6:
                    base = 9
                elif dist <= 10:
                    base = 13
                elif dist <= 15:
                    base = 18
                else:
                    base = 30

                return f"¥{(base + total):.2f}"

            else:
                return "¥待计算"

        # --- 价格计算 ---
        price_text = ft.Text(get_price(), size=22, color=ft.Colors.RED_700, weight="bold")

        # --- 下单 ---
        def on_submit():
            if not start_address:
                self.show_snackbar("请选择装货地址", ft.Colors.RED_400)
                return

            if not selected_address:
                self.show_snackbar("请选择收货地址", ft.Colors.RED_400)
                return
            
            if start_address == selected_address:
                self.show_snackbar("装货地址不应和收货地址相同", ft.Colors.RED_400)
                return

            start = datetime.datetime.strptime(start_field.value, "%Y-%m-%d %H:%M")
            total = float(price_text.value[1:])

            order = {
                "id": datetime.datetime.now().astimezone().strftime("%Y%m%d%H%M%S"),
                "phone": phone,
                "drone_id": drone["id"],
                "drone_name": drone["name"],
                "start_address": start_address,
                "start_location": self.app.user_manager.get_location_by_address(phone, start_address),
                "address": selected_address,
                "location": self.app.user_manager.get_location_by_address(phone, selected_address),
                "start_time": start.strftime("%Y-%m-%d %H:%M"),
                "total_price": total,
                "status": "待配送",
                "created_at": datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
                "is_booking": is_booking,
            }

            self.app.user_manager.add_order(phone, order)
            self.show_snackbar("下单成功！", ft.Colors.GREEN_400)
            self.goto("orders", selected_index=1)

        return ft.Column([
            # 顶部栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda: self.goto("drone", drone_id=drone_id),
                    ),
                    ft.Text(
                        "预约租赁" if is_booking else "立即租赁",
                        size=20, weight="bold", expand=True,
                    ),
                ]),
                padding=ft.Padding(15, 20, 15, 15),
                bgcolor=ft.Colors.WHITE,
            ),

            ft.Container(
                content=ft.Column([
                    # ========== 机型信息 ==========
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(drone["images"][0], size=50),
                                width=80, height=80,
                                bgcolor=ft.Colors.BLUE_50,
                                border_radius=12,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column([
                                ft.Text(drone["name"], size=16, weight="bold"),
                                ft.Text(drone["specs"], size=13, color=ft.Colors.GREY_600),
                                ft.Text(f"¥{drone['price'] / 100.0}/千米", size=13, color=ft.Colors.RED_700),
                            ], spacing=4, expand=True),
                        ], spacing=15),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    ),

                    ft.Container(height=15),

                    # ========== 地址信息 ==========
                    ft.Container(
                        content=ft.Column([
                            ft.Text("地址信息", size=15, weight="bold"),
                            ft.Container(height=8),
                            start_address_display,
                            address_display
                        ]),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    ),

                    ft.Container(height=15),

                    # ========== 租赁设置 ==========
                    ft.Container(
                        content=ft.Column([
                            ft.Text("租赁设置", size=15, weight="bold"),
                            ft.Container(height=10),
                            start_row,
                        ]),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    ),

                    ft.Container(height=15),

                    # ========== 费用 ==========
                    ft.Container(
                        content=ft.Row([
                            ft.Text("预计费用", size=15, weight="bold", expand=True),
                            price_text,
                        ]),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    ),

                    ft.Container(height=25),

                    # ========== 提交 ==========
                    ft.Button(
                        "确认下单",
                        width=float("inf"),
                        height=55,
                        bgcolor=ft.Colors.BLUE,
                        color=ft.Colors.WHITE,
                        on_click=on_submit,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    ),

                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=20,
            ),
        ], expand=True)

    def build_drone_detail(self, drone_id: str):
        """构建无人机详情页"""
        drone = self.app.drone_manager.get_by_id(drone_id)

        # 顶部导航栏
        top_bar = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda: self.goto("home"),
                ),
                ft.Text("商品详情", size=18, weight="bold", expand=True)
            ]),
            padding=ft.Padding.only(left=10, right=10, top=20, bottom=10),
            bgcolor=ft.Colors.WHITE,
        )
        
        # 图片轮播区（简化版，用大emoji代替）
        image_section = ft.Container(
            content=ft.Column([
                ft.Text(drone["images"][0], size=120),
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=8,
                            height=8,
                            border_radius=4,
                            bgcolor=ft.Colors.BLUE,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=10,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.BLUE_50,
            padding=30,
        )
        
        # 价格和标题
        title_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(drone["tag"], size=12, color="white"),
                        bgcolor=ft.Colors.BLUE,
                        padding=ft.Padding.symmetric(vertical=4, horizontal=10),
                        border_radius=4,
                    ),
                    ft.Container(
                        content=ft.Text(f"已售 {drone['sales']}", size=12, color=ft.Colors.GREY_600),
                    ),
                ], spacing=10),
                ft.Container(height=10),
                ft.Text(drone["name"], size=24, weight="bold"),
                ft.Container(height=10),
                ft.Row([
                    ft.Column([
                        ft.Text(f"¥{drone["price"] / 100.0}/千米", size=32, color=ft.Colors.RED_700),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.START),
                    ft.Text(
                        f"原价 ¥{drone['original_price'] / 100.0}",
                        size=14,
                        color=ft.Colors.GREY_500,
                        style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                    ),
                ], spacing=15, alignment=ft.MainAxisAlignment.START),
            ]),
            padding=20,
            bgcolor=ft.Colors.WHITE,
        )
        
        # 规格参数
        specs_section = ft.Container(
            content=ft.Column([
                ft.Text("产品特性", size=18, weight="bold"),
                ft.Container(height=10),
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=20, color=ft.Colors.GREEN),
                        ft.Text(feature, size=14),
                    ], spacing=10) for feature in drone["features"]
                ], spacing=8),
            ]),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            margin=ft.Margin.only(top=10),
        )
        
        # 商品描述
        description_section = ft.Container(
            content=ft.Column([
                ft.Text("商品介绍", size=18, weight="bold"),
                ft.Container(height=10),
                ft.Text(
                    drone["description"],
                    size=14,
                    color=ft.Colors.GREY_700,
                ),
            ]),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            margin=ft.Margin.only(top=10),
        )
        
        # 库存信息
        stock_section = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=16, color=ft.Colors.GREY_600),
                ft.Text(
                    f"库存：{drone['stock']} 件",
                    size=14,
                    color=ft.Colors.GREY_600,
                ),
            ], spacing=5),
            padding=ft.Padding.symmetric(horizontal=20, vertical=10),
            bgcolor=ft.Colors.WHITE,
            margin=ft.Margin.only(top=10),
        )
        
        def on_rent_now():
            self.goto("order", drone_id=drone["id"], is_booking=False)

        def on_book():
            self.goto("order", drone_id=drone["id"], is_booking=True)

        bottom_bar = ft.Container(
            content=ft.Row([
                ft.OutlinedButton(
                    "预约租赁",
                    icon=ft.Icons.CALENDAR_MONTH,
                    on_click=on_book,
                    expand=True,
                    height=50,
                ),
                ft.Button(
                    "立即租赁",
                    icon=ft.Icons.FLIGHT_TAKEOFF,
                    on_click=on_rent_now,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                    expand=True,
                    height=50,
                ),
            ], spacing=10),
            padding=ft.Padding.all(15),
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.BLACK_12,
                offset=ft.Offset(0, -2),
            ),
        )
        
        # 主内容区（可滚动）
        main_content = ft.Column([
            ft.Column([
                image_section,
                title_section,
                specs_section,
                description_section,
                stock_section,
            ], scroll=ft.ScrollMode.AUTO, expand=True),
        ], spacing=0, expand=True)
        
        # 组装页面（主内容 + 底部栏）
        return ft.Column([
            top_bar,
            main_content,
            bottom_bar,
        ], spacing=0, expand=True)

    def build_menu_item(self, icon, label):
        def on_menu_click(label):
            if label == "我的订单":
                return self.goto("orders")
            elif label == "收藏夹":
                pass
            elif label == "优惠卷":
                pass
            else:
                pass

        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=28, color=ft.Colors.BLUE_700),
                ft.Text(label, size=11, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            on_click=lambda: on_menu_click(label),
            padding=10,
            ink=True,
        )

    def _list_item(self, icon, title, trailing_text=None):
        def on_settings_click(title):
            print(f"设置: {title}")

        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=22, color=ft.Colors.GREY_700),
                ft.Text(title, size=15, expand=True),
                ft.Text(
                    trailing_text,
                    size=13,
                    color=ft.Colors.GREY_500,
                ) if trailing_text else ft.Container(),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color=ft.Colors.GREY_400),
            ], spacing=15),
            padding=ft.Padding.symmetric(horizontal=20, vertical=15),
            on_click=lambda: on_settings_click(title),
            ink=True,
        )

class App:
    def __init__(self):
        self.AMAP_KEY = keyvals.AMAP_KEY
        self.config = Config()
        self.user_manager = UserManager()
        self.drone_manager = DroneManager()
        self.page = None
        self.view_builder = ViewBuilder(self)

    def before_main(self, page: ft.Page):
        self.page = page
        page.title = "DroneGo"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0

        if not self.config.get("agreed"):
            def on_agree_click():
                self.config.set("agreed", True)
                page.controls.clear()
                self.main(page)

            # 协议文档内容
            user_agreement_text = FileReader.read_txt("user_agreement_text.txt")

            privacy_policy_text = FileReader.read_txt("privacy_policy_text.txt")

            # 显示文档的对话框
            def show_document(title, content):
                def close_dialog(e):
                    dialog.open = False
                    page.update()

                dialog = ft.AlertDialog(
                    title=ft.Text(title, weight="bold"),
                    content=ft.Container(
                        content=ft.Text(content, selectable=True),
                        width=500,
                        height=400,
                        padding=20,
                    ),
                    actions=[
                        ft.TextButton("关闭", on_click=close_dialog),
                    ],
                    scrollable=True,
                )
                page.overlay.append(dialog)
                dialog.open = True
                page.update()

            # 构建全屏协议界面
            agreement_view = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PRIVACY_TIP, size=80, color=ft.Colors.BLUE),
                    ft.Text("DroneGo", size=28, weight="bold"),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "欢迎来到 DroneGo！",
                                size=16,
                                weight="bold",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=10),
                            ft.Text(
                                "为了保障您的权益，请仔细阅读并同意：",
                                size=14,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=15),
                            ft.Row([
                                ft.TextButton(
                                    "《用户协议》",
                                    on_click=lambda: show_document("用户协议", user_agreement_text),
                                ),
                                ft.Text("和", size=14),
                                ft.TextButton(
                                    "《隐私政策》",
                                    on_click=lambda: show_document("隐私政策", privacy_policy_text),
                                ),
                            ], alignment="center"),
                            ft.Container(height=10),
                            ft.Text(
                                "我们承诺保护您的飞行轨迹与个人数据安全",
                                size=12,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ], horizontal_alignment="center"),
                        padding=20,
                    ),
                    ft.Container(height=20),
                    ft.Row([
                        ft.OutlinedButton("退出应用", on_click=lambda: sys.exit()),
                        ft.Button("同意并继续", on_click=on_agree_click, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                    ], alignment="center", spacing=20),
                ], horizontal_alignment="center", alignment="center"),
                expand=True,
                bgcolor=ft.Colors.WHITE,
                padding=50,
            )
            
            page.add(agreement_view)
            
        else:
            self.main(page)

    def main(self, page: ft.Page):
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
                ft.NavigationBarDestination(icon=ft.Icons.EXPLORE_OUTLINED, selected_icon=ft.Icons.EXPLORE, label="首页"),
                ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT_OUTLINED, selected_icon=ft.Icons.LIST_ALT, label="订单"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="我的"),
            ],
        )

        # 加载首页
        page.add(self.view_builder.build_home())
        page.run_task(self.order_checker)

    async def order_checker(self):
        while True:
            phone = self.config.get("last_user")

            if not phone:
                await asyncio.sleep(10)
                continue

            now = datetime.datetime.now().astimezone()
            for order in self.user_manager.get_orders(phone):
                status = order.get("status")
                start = datetime.datetime.strptime(order["start_time"], "%Y-%m-%d %H:%M").astimezone()

                if status == "待配送" and now >= start:
                    self.user_manager.update_order_status(phone, order["id"], "租赁中")

            await asyncio.sleep(30)

    def __call__(self, *args, **kwds):
        self.before_main(*args, **kwds)

# 启动应用
if __name__ == "__main__":
    app = App()
    ft.run(app)