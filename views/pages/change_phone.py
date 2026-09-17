"""手机换绑页。"""

import re
import flet as ft

from views.components import PHONE_PATTERN


def build_change_phone(app, **kwargs):
    """手机换绑页面"""
    phone = app.config.get("last_user")

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

    def on_save_click(_):
        new_phone = new_phone_field.value
        password = password_field.value

        if not password:
            app.view_builder.show_snackbar("请输入当前密码", ft.Colors.RED_400)
            return

        if not app.user_manager.verify_login(phone, password):
            app.view_builder.show_snackbar("密码错误", ft.Colors.RED_400)
            return

        if not new_phone:
            app.view_builder.show_snackbar("请输入新手机号", ft.Colors.RED_400)
            return

        if not re.match(PHONE_PATTERN, new_phone):
            app.view_builder.show_snackbar("请输入正确的11位手机号码", ft.Colors.RED_400)
            return

        if new_phone == phone:
            app.view_builder.show_snackbar("新手机号不能与当前手机号相同", ft.Colors.RED_400)
            return

        if not app.user_manager.update_key(phone, new_phone):
            app.view_builder.show_snackbar("该手机号已被注册", ft.Colors.RED_400)
            return

        app.config.set("last_user", new_phone)
        app.view_builder.show_snackbar("手机号换绑成功", ft.Colors.GREEN_400)
        app.view_builder.goto("settings")

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: app.view_builder.goto("settings")),
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
