"""我的页面。"""

import flet as ft

from file import FileReader
from views.components import build_list_item, build_menu_item


def build_profile(app, **kwargs):
    """构建我的页面"""
    phone = app.config.get("last_user")
    username = app.user_manager.get(phone).get("nick_name") if phone else "游客"
    is_logged_in = bool(phone)

    def on_logout_click(_):
        """退出登录"""
        app.config.logout()
        app.view_builder.goto("profile")

    user_card = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.CircleAvatar(
                    foreground_image_src=FileReader.read_img(f"{phone}.png") if phone else None,
                    radius=40
                ),
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
                on_click=lambda _: app.view_builder.goto("settings") if is_logged_in
                else app.view_builder.show_snackbar("请先登录", ft.Colors.RED_400),
            ),
        ]),
        bgcolor=ft.Colors.BLUE_50,
        padding=20,
        border_radius=15,
        on_click=lambda: app.view_builder.goto("login") if not is_logged_in else None,
    )

    menu_items = ft.Container(
        content=ft.Row([
            build_menu_item(app, ft.Icons.RECEIPT_LONG, "我的订单"),
            build_menu_item(app, ft.Icons.FAVORITE, "收藏夹"),
            build_menu_item(app, ft.Icons.HEADSET_MIC, "客服"),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        padding=ft.Padding.symmetric(vertical=20),
    )

    settings_section = ft.Column([
        ft.Container(
            content=ft.Text("设置", size=16, weight="bold"),
            padding=ft.Padding.only(left=20, top=10, bottom=10),
        ),
        build_list_item(app, ft.Icons.LANGUAGE, "实名认证",
                        "已认证" if phone and app.user_manager.realname(phone) else "未认证"),
        build_list_item(app, ft.Icons.AIRPLANEMODE_ACTIVE, "飞手认证",
                        "已认证" if phone and app.user_manager.pilot(phone) else "未认证"),
        build_list_item(app, ft.Icons.INFO_OUTLINE, "关于我们"),
    ])

    logout_section = ft.Column([
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=ft.TextButton(
                "退出登录",
                icon=ft.Icons.LOGOUT,
                on_click=on_logout_click,
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
