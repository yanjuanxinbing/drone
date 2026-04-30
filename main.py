import re
import sys
import flet as ft
from config import Config
from usermanager import UserManager
from file import FileReader, FileWriter

class EventHandler:
    """事件处理器 - 持有 App 实例引用"""
    def __init__(self, app: App):
        self.app = app
    
    # --- 导航事件 ---
    def on_nav_change(self, e):
        """底部导航栏切换"""
        index = e.control.selected_index
        self.app.page.controls.clear()
        
        if index == 0:
            view = self.app.view_builder.build_home()
        elif index == 1:
            view = self.app.view_builder.build_orders()
        elif index == 2:
            view = self.app.view_builder.build_profile()
        
        self.app.page.add(view)
        self.app.page.update()
    
    # --- 首页事件 ---
    def on_search(self, e):
        print(f"搜索: {e.control.value}")
    
    def on_category_click(self, name):
        print(f"分类: {name}")
    
    def on_drone_click(self, name):
        print(f"无人机: {name}")
    
    # --- 我的页面事件 ---
    def on_menu_click(self, label):
        print(f"点击: {label}")
    
    def on_settings_click(self, title):
        print(f"设置: {title}")
    
    def on_login_click(self):
        """跳转到登录页面"""
        self.app.page.controls.clear()
        view = self.app.view_builder.build_login()
        self.app.page.add(view)
        self.app.page.update()
    
    def on_register_click(self):
        """跳转到注册页面"""
        self.app.page.controls.clear()
        view = self.app.view_builder.build_register()
        self.app.page.add(view)
        self.app.page.update()
    
    def on_forget_click(self):
        #TODO
        pass

    def on_nav_change_to_profile(self):
        """直接跳转到我的页面（不通过导航栏）"""
        self.app.page.controls.clear()
        # 更新导航栏选中状态
        self.app.page.navigation_bar.selected_index = 2
        view = self.app.view_builder.build_profile()
        self.app.page.add(view)
        self.app.page.update()
    
    def on_logout_click(self):
        """退出登录"""
        self.app.config.set("last_user", "")
        self.app.config.set("last_name", "")
        print("已退出登录")
        self._refresh_profile()
    
    def _refresh_profile(self):
        """刷新我的页面"""
        self.app.page.controls.clear()
        view = self.app.view_builder.build_profile()
        self.app.page.add(view)
        self.app.page.update()

class ViewBuilder:
    """视图构建器 - 只负责生成 UI"""
    def __init__(self, app: App):
        self.app = app
        self.handler = app.event_handler
    
    def build_home(self):
        """构建首页"""
        header = ft.Container(
            content=ft.Text("DroneGo", size=32, weight="bold", color="white"),
            bgcolor=ft.Colors.BLUE,
            padding=30,
            width=float("inf"),
            border_radius=ft.BorderRadius.only(bottom_left=30, bottom_right=30),
        )

        search_bar = ft.Container(
            content=ft.TextField(
                prefix_icon=ft.Icons.SEARCH,
                hint_text="搜索无人机型号...",
                border_radius=15,
                filled=True,
                on_submit=self.handler.on_search,
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

        drone_grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=250,
            child_aspect_ratio=0.75,
            spacing=15,
            run_spacing=15,
            controls=[
                self._drone_card("DJI Air 3S", "299", "热门", "46min续航/4K"),
                self._drone_card("Mavic 3 Pro", "499", "专业", "哈苏镜头/三摄"),
                self._drone_card("Autel EVO II", "699", "工业", "6K超清/测绘"),
                self._drone_card("Dobby Pocket", "99", "入门", "自拍/人脸跟踪"),
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

    def build_profile(self):
        """构建我的页面"""
        username = self.app.config.get("last_name") or "游客"
        is_logged_in = bool(self.app.config.get("last_name"))
        
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
                    on_click=lambda _: self.handler.on_settings_click("设置"),
                ),
            ]),
            bgcolor=ft.Colors.BLUE_50,
            padding=20,
            border_radius=15,
            on_click=lambda _: self.handler.on_login_click() if not is_logged_in else None,
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
                    on_click=lambda _: self.handler.on_logout_click(),
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
        
        def on_login_submit(e):
            phone_number = phone_number_field.value
            password = password_field.value
            
            def warn(text: str):
                snackbar = ft.SnackBar(
                    content=ft.Text(text),
                    bgcolor=ft.Colors.RED_400,
                )
                self.app.page.overlay.append(snackbar)
                snackbar.open = True
                self.app.page.update()
            
            if not phone_number:
                warn("请输入手机号")
                return
            
            if not password:
                warn("请输入密码")
                return
            
            user_manager = UserManager()

            # 登录成功
            if user_manager.verify_login(phone_number, password):
                self.app.config.set("last_user", phone_number)
            else:
                warn("手机号或密码错误")
                return
            
            # 返回"我的"页面
            self.handler.on_nav_change_to_profile()
        
        def on_back(e):
            # 返回"我的"页面
            self.handler.on_nav_change_to_profile()
        
        return ft.Container(
            content=ft.Column([
                # 顶部返回按钮
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=on_back,
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
                                on_click=lambda _: self.handler.on_forget_click(),
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
                                on_click=lambda _: self.handler.on_register_click(),
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
                on_click=lambda _: show_document("用户协议", "user_agreement_text.txt"),
                style=ft.ButtonStyle(
                    padding=0,
                ),
            ),
            ft.Text("和", size=13, color=ft.Colors.GREY_700),
            ft.TextButton(
                "《隐私政策》",
                on_click=lambda _: show_document("隐私政策", "privacy_policy_text.txt"),
                style=ft.ButtonStyle(
                    padding=0,
                ),
            ),
        ], spacing=0, wrap=True)
        
        def on_register_submit(e):
            phone_number = phone_number_field.value
            password = password_field.value
            confirm_password = confirm_password_field.value

            user_manager = UserManager()

            def warn(text: str):
                snackbar = ft.SnackBar(
                    content=ft.Text(text),
                    bgcolor=ft.Colors.RED_400,
                )
                self.app.page.overlay.append(snackbar)
                snackbar.open = True
                self.app.page.update()

            # 验证手机号
            if not phone_number:
                warn("请输入手机号")
                return

            phone_pattern = r"^1[3-9]\d{9}$"
            if not re.match(phone_pattern, phone_number):
                warn("请输入正确的11位手机号码")
                return
            
            if user_manager.contains(phone_number):
                warn("手机号已注册，请登录")
                return

            # 验证密码
            if not password:
                warn("请输入密码")
                return
            
            if len(password) < 6:
                warn("密码至少需要6位")
                return
            
            # 验证确认密码
            if password != confirm_password:
                warn("两次输入的密码不一致")
                return
            
            # 检查协议勾选
            if not agree_checkbox.value:
                warn("请先阅读并同意用户协议")
                return
            
            # 注册成功
            self.app.config.set("last_user", phone_number)
            self.app.config.set("last_name", f"用户{phone_number}")
            
            snackbar = ft.SnackBar(
                content=ft.Text(f"注册成功！欢迎 用户{phone_number}"),
                bgcolor=ft.Colors.GREEN_400,
            )
            self.app.page.overlay.append(snackbar)
            snackbar.open = True
            self.app.page.update()

            user_manager.add(phone_number, f"用户{phone_number}", password)
            self.handler.on_nav_change_to_profile()
        
        def on_back(e):
            self.handler.on_login_click()
        
        return ft.Container(
            content=ft.Column([
                # 顶部返回按钮
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=on_back,
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
                                on_click=on_back,
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

    # --- 组件工厂方法 ---
    def _category_item(self, icon, name):
        return ft.Container(
            content=ft.Column([
                ft.Text(icon, size=25),
                ft.Text(name, size=12, weight=ft.FontWeight.W_500),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=lambda _: self.handler.on_category_click(name),
            padding=10,
            width=80,
            border_radius=10,
            ink=True,
        )

    def _drone_card(self, name, price, tag, specs):
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
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12),
            on_click=lambda _: self.handler.on_drone_click(name),
        )

    def _menu_item(self, icon, label):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=28, color=ft.Colors.BLUE_700),
                ft.Text(label, size=11, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            on_click=lambda _: self.handler.on_menu_click(label),
            padding=10,
            ink=True,
        )

    def _list_item(self, icon, title, trailing_text=None):
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
            on_click=lambda _: self.handler.on_settings_click(title),
            ink=True,
        )

class App:
    def __init__(self):
        self.config = Config()
        self.page = None
        self.event_handler = EventHandler(self)
        self.view_builder = ViewBuilder(self)

    def before_main(self, page: ft.Page):
        self.page = page
        page.title = "DroneGo"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0

        if not self.config.get("agreed"):
            def on_agree_click(e):
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
                                    on_click=lambda _: show_document("用户协议", user_agreement_text),
                                ),
                                ft.Text("和", size=14),
                                ft.TextButton(
                                    "《隐私政策》",
                                    on_click=lambda _: show_document("隐私政策", privacy_policy_text),
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
                        ft.OutlinedButton("退出应用", on_click=lambda _: sys.exit()),
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
        # 设置底部导航栏
        page.navigation_bar = ft.NavigationBar(
            selected_index=0,
            on_change=self.event_handler.on_nav_change,
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