"""设置页。"""

import flet as ft


def build_settings(app, **kwargs):
    """构建设置页"""
    return ft.Column([
        # 顶部导航栏
        ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda: app.view_builder.goto("profile"),
                ),
                ft.Text("设置", size=20, weight="bold", expand=True),
            ]),
            padding=ft.Padding(15, 20, 15, 15),
            bgcolor=ft.Colors.WHITE,
        ),

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
                    on_click=lambda: app.view_builder.goto("personal_info")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOCK_OUTLINE),
                    title=ft.Text("修改密码"),
                    subtitle=ft.Text("定期修改以保护账号安全"),
                    on_click=lambda: app.view_builder.goto("change_password")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PHONE_ANDROID),
                    title=ft.Text("手机换绑"),
                    subtitle=ft.Text("更换绑定的手机号码"),
                    on_click=lambda _: app.view_builder.goto("change_phone")
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
                    on_click=lambda: app.view_builder.goto("addresses")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED),
                    title=ft.Text("租赁通知"),
                    subtitle=ft.Text("到期提醒、订单状态"),
                    trailing=ft.Switch(
                        value=app.config.get("notify_enabled"),
                        on_change=lambda e: app.config.set("notify_enabled", e.control.value)
                    )
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HISTORY),
                    title=ft.Text("租赁记录"),
                    subtitle=ft.Text("查看历史租赁订单"),
                    on_click=lambda: app.view_builder.goto("orders")
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
                    on_click=lambda: app.view_builder.show_snackbar("缓存已清除", ft.Colors.GREEN_400)
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PRIVACY_TIP_OUTLINED),
                    title=ft.Text("隐私设置"),
                    subtitle=ft.Text("数据使用与权限"),
                    on_click=lambda: app.view_builder.goto("privacy_settings")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HELP_OUTLINE),
                    title=ft.Text("帮助中心"),
                    subtitle=ft.Text("常见问题与客服"),
                    on_click=lambda: app.view_builder.goto("help_center")
                ),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    ], expand=True)
