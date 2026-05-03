import re
import sys
import flet as ft
import datetime
from config import Config
from usermanager import UserManager
from dronemanager import DroneManager
from file import FileReader, FileWriter

class ViewBuilder:
    """视图构建器 - 只负责生成 UI"""
    def __init__(self, app: App):
        self.app = app

    def goto(self, name, drone_id=None):
        """通用页面跳转"""
        self.app.page.controls.clear()
        
        if name == "home":
            self.app.page.navigation_bar.selected_index = 0
            view = self.build_home()
        elif name == "orders":
            self.app.page.navigation_bar.selected_index = 1
            view = self.build_orders()
        elif name == "profile":
            self.app.page.navigation_bar.selected_index = 2
            view = self.build_profile()
        elif name == "login":
            view = self.build_login()
        elif name == "register":
            view = self.build_register()
        elif name == "forget":
            print("忘记密码")
        elif name == "drone":
            view = self.build_drone_detail(drone_id)
        elif name == "settings":
            view = self.build_settings()
        elif name == "personal_info":
            view = self.build_personal_info()

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
            #TODO
            print(f"搜索: {e.control.value}")

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

        categories = ft.Row(
            [
                self._category_item("📷", "航拍摄影"),
                self._category_item("🏗️", "工业巡检"),
                self._category_item("📐", "测绘勘察"),
                self._category_item("🎮", "自拍娱乐"),
            ],
            scroll=ft.ScrollMode.HIDDEN,
            alignment=ft.MainAxisAlignment.CENTER,
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
                self._drone_card(
                    drone_id=drone["id"],
                    name=drone["name"],
                    price=str(drone["price"]),
                    tag=drone["tag"],
                    specs=drone["specs"]
                ) for drone in hot_drones
            ],
        )

        return ft.Column([
            header,
            search_bar,
            ft.Container(height=10),
            categories,
            ft.Container(
                content=ft.Text("推荐机型", size=18, weight="bold"),
                padding=ft.Padding.symmetric(horizontal=20)
            ),
            ft.Container(content=drone_grid, padding=20, expand=True),
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def build_orders(self):
        """构建订单页"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=100, color=ft.Colors.GREY_400),
                ft.Text("订单页面", size=20, weight="bold"),
                ft.Text("暂无订单", size=14, color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            expand=True,
        )

    def build_personal_info(self):
        """个人信息编辑页面"""
        # 1. 获取现有配置数据
        username = self.app.config.get("last_name")
        gender_val = self.app.config.get("last_gender")
        birthday_val = self.app.config.get("last_birthday")

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

        # --- 交互事件处理 ---
        # 日期选择器逻辑
        def on_date_change(e):
            if e.control.value:
                picked_date: datetime.datetime = e.control.value
                local_date = picked_date.astimezone(None)
                selected_date_str = local_date.strftime("%Y-%m-%d")
                birthday_field.value = selected_date_str
                birthday_field.update()

        date_picker = ft.DatePicker(
            value = datetime.datetime.strptime(birthday_val, "%Y-%m-%d") if birthday_val else None,
            on_change=on_date_change,
            first_date=datetime.datetime(1900, 1, 1),
            last_date=datetime.datetime.now(),
        )
        # 将选择器加入页面 overlay
        self.app.page.overlay.append(date_picker)

        def on_save_click():
            new_nickname = nickname_field.value.strip()
            if not new_nickname:
                self.show_snackbar("昵称不能为空", ft.Colors.RED_400)
                return

            usermanager = UserManager()

            # 保存所有信息到配置
            self.app.config.set("last_name", new_nickname)
            self.app.config.set("last_gender", gender_dropdown.value)
            self.app.config.set("last_birthday", birthday_field.value)
            
            usermanager.update_value(self.app.config.get("last_user"), new_nickname, gender_dropdown.value, birthday_field.value)

            self.show_snackbar("个人信息已保存", ft.Colors.GREEN_400)

        def on_change_avatar(e):
            self.show_snackbar("头像更换功能开发中", ft.Colors.BLUE_400)

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
                        ft.Container(content=ft.Text("👤", size=80), width=120, height=120, 
                                    bgcolor=ft.Colors.BLUE_100, border_radius=60, alignment=ft.Alignment.CENTER),
                        ft.TextButton("更换头像", icon=ft.Icons.CAMERA_ALT_OUTLINED, on_click=on_change_avatar),
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
                        on_click=lambda: print("修改密码")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PAYMENTS_OUTLINED),
                        title=ft.Text("支付方式"),
                        subtitle=ft.Text("银行卡、支付宝、微信"),
                        on_click=lambda: print("支付方式管理")
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
                        on_click=lambda: print("地址管理")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED),
                        title=ft.Text("租赁通知"),
                        subtitle=ft.Text("到期提醒、订单状态"),
                        trailing=ft.Switch(value=True),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.HISTORY),
                        title=ft.Text("租赁记录"),
                        subtitle=ft.Text("查看历史租赁订单"),
                        on_click=lambda: self.goto("orders")  # 直接跳到订单页
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
                        on_click=lambda: print("隐私设置")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.HELP_OUTLINE),
                        title=ft.Text("帮助中心"),
                        subtitle=ft.Text("常见问题与客服"),
                        on_click=lambda: print("帮助中心")
                    ),
                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
            )
        ], expand=True)

    def build_profile(self):
        """构建我的页面"""
        username = self.app.config.get("last_name") or "游客"
        is_logged_in = bool(self.app.config.get("last_name"))

        def on_logout_click():
            """退出登录"""
            self.app.config.logout()
            self.goto("profile")
        
        user_card = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("👤", size=40),
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
                    on_click=lambda: self.goto("settings"),
                ),
            ]),
            bgcolor=ft.Colors.BLUE_50,
            padding=20,
            border_radius=15,
            on_click=lambda: self.goto("login") if not is_logged_in else None,
        )
        
        menu_items = ft.Container(
            content=ft.Row([
                self._menu_item(ft.Icons.RECEIPT_LONG, "我的订单"),
                self._menu_item(ft.Icons.FAVORITE, "收藏夹"),
                self._menu_item(ft.Icons.CARD_GIFTCARD, "优惠券"),
                self._menu_item(ft.Icons.HEADSET_MIC, "客服"),
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
            
            user_manager = UserManager()

            # 登录成功
            if user_manager.verify_login(phone_number, password):
                self.app.config.set("last_user", phone_number)
                self.app.config.set("last_name", user_manager.users[phone_number]["nick_name"])
                self.app.config.set("last_gender", user_manager.users[phone_number]["gender"])
                self.app.config.set("last_birthday", user_manager.users[phone_number]["birthday"])
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

            user_manager = UserManager()

            # 验证手机号
            if not phone_number:
                self.show_snackbar("请输入手机号", ft.Colors.RED_400)
                return

            phone_pattern = r"^1[3-9]\d{9}$"
            if not re.match(phone_pattern, phone_number):
                self.show_snackbar("请输入正确的11位手机号码", ft.Colors.RED_400)
                return
            
            if user_manager.contains(phone_number):
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
            user_manager.add(phone_number, f"用户{phone_number}", password)

            self.app.config.set("last_user", phone_number)
            self.app.config.set("last_name", f"用户{phone_number}")
            self.app.config.set("last_gender", "保密")
            self.app.config.set("last_birthday", "")

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

    def build_drone_detail(self, drone_id: str):
        """构建无人机详情页"""
        drone = self.app.drone_manager.get_by_id(drone_id)
        
        if not drone:
            # 如果找不到无人机，显示错误页面
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=100, color=ft.Colors.GREY_400),
                    ft.Text("无人机不存在", size=20, weight="bold"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
            )

        def on_add_to_cart(e):
            """加入购物车"""
            snackbar = ft.SnackBar(
                content=ft.Text(f"已将 {drone['name']} 加入购物车"),
                bgcolor=ft.Colors.GREEN_400,
            )
            self.app.page.overlay.append(snackbar)
            snackbar.open = True
            self.app.page.update()
        
        def on_buy_now(e):
            """立即购买"""
            snackbar = ft.SnackBar(
                content=ft.Text("跳转到支付页面（功能开发中）"),
                bgcolor=ft.Colors.BLUE_400,
            )
            self.app.page.overlay.append(snackbar)
            snackbar.open = True
            self.app.page.update()
        
        # 顶部导航栏
        top_bar = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda: self.goto("home"),
                ),
                ft.Text("商品详情", size=18, weight="bold", expand=True),
                ft.IconButton(
                    icon=ft.Icons.SHOPPING_CART_OUTLINED,
                    on_click=lambda: print("打开购物车"),
                ),
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
                        ft.Text(f"¥{drone["price"]}", size=32, color=ft.Colors.RED_700),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.START),
                    ft.Text(
                        f"原价 ¥{drone['original_price']}",
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
        
        # 底部操作栏
        bottom_bar = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.FAVORITE_BORDER,
                    icon_color=ft.Colors.GREY_700,
                    on_click=lambda: print("收藏"),
                ),
                ft.OutlinedButton(
                    "加入购物车",
                    icon=ft.Icons.SHOPPING_CART_OUTLINED,
                    on_click=on_add_to_cart,
                    expand=True,
                    height=50,
                ),
                ft.Button(
                    "立即购买",
                    on_click=on_buy_now,
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

    # --- 组件工厂方法 ---
    def _category_item(self, icon, name):
        def on_category_click(name):
            print(f"分类: {name}")

        return ft.Container(
            content=ft.Column([
                ft.Text(icon, size=25),
                ft.Text(name, size=12, weight=ft.FontWeight.W_500),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=lambda: on_category_click(name),
            padding=10,
            width=80,
            border_radius=10,
            ink=True,
        )

    def _drone_card(self, drone_id, name, price, tag, specs):
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
            on_click=lambda: self.goto("drone", drone_id)
        )

    def _menu_item(self, icon, label):
        def on_menu_click(label):
            print(f"点击: {label}")

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
        self.config = Config()
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

    def __call__(self, *args, **kwds):
        self.before_main(*args, **kwds)

# 启动应用
if __name__ == "__main__":
    app = App()
    ft.run(app)