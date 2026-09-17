"""注册页。"""

import re
import flet as ft

from file import FileReader
from views.components import PHONE_PATTERN, show_document_dialog


def build_register(app, **kwargs):
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

    # 协议勾选区域（文本可点击）
    agree_checkbox = ft.Checkbox(value=False)

    agree_row = ft.Row([
        agree_checkbox,
        ft.Text("我已阅读并同意", size=13, color=ft.Colors.GREY_700),
        ft.TextButton(
            "《用户协议》",
            on_click=lambda: show_document_dialog(
                app, "用户协议",
                FileReader.read_txt("user_agreement_text.txt")
            ),
            style=ft.ButtonStyle(padding=0),
        ),
        ft.Text("和", size=13, color=ft.Colors.GREY_700),
        ft.TextButton(
            "《隐私政策》",
            on_click=lambda: show_document_dialog(
                app, "隐私政策",
                FileReader.read_txt("privacy_policy_text.txt")
            ),
            style=ft.ButtonStyle(padding=0),
        ),
    ], spacing=0, wrap=True)

    def on_register_submit(_):
        phone_number = phone_number_field.value
        password = password_field.value
        confirm_password = confirm_password_field.value

        if not phone_number:
            app.view_builder.show_snackbar("请输入手机号", ft.Colors.RED_400)
            return

        if not re.match(PHONE_PATTERN, phone_number):
            app.view_builder.show_snackbar("请输入正确的11位手机号码", ft.Colors.RED_400)
            return

        if app.user_manager.contains(phone_number):
            app.view_builder.show_snackbar("手机号已注册，请登录", ft.Colors.RED_400)
            return

        if not password:
            app.view_builder.show_snackbar("请输入密码", ft.Colors.RED_400)
            return

        if len(password) < 6:
            app.view_builder.show_snackbar("密码至少需要6位", ft.Colors.RED_400)
            return

        if password != confirm_password:
            app.view_builder.show_snackbar("两次输入的密码不一致", ft.Colors.RED_400)
            return

        if not agree_checkbox.value:
            app.view_builder.show_snackbar("请先阅读并同意用户协议", ft.Colors.RED_400)
            return

        app.user_manager.add(phone_number, f"用户{phone_number}", password)
        app.config.set("last_user", phone_number)

        snackbar = ft.SnackBar(
            content=ft.Text(f"注册成功！欢迎 用户{phone_number}"),
            bgcolor=ft.Colors.GREEN_400,
        )
        app.page.overlay.append(snackbar)
        snackbar.open = True
        app.page.update()

        app.view_builder.goto("profile")

    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda: app.view_builder.goto("login"),
                    ),
                    ft.Text("注册", size=20, weight="bold"),
                ]),
                padding=ft.Padding.only(left=10, right=20, top=20, bottom=10),
            ),

            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.PERSON_ADD,
                            size=80,
                            color=ft.Colors.BLUE,
                        ),
                        alignment=ft.Alignment.CENTER,
                    ),

                    ft.Container(height=20),

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

                    phone_number_field,
                    ft.Container(height=15),
                    password_field,
                    ft.Container(height=15),
                    confirm_password_field,

                    ft.Container(height=20),

                    agree_row,

                    ft.Container(height=25),

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

                    ft.Row([
                        ft.Text("已有账号？", size=14, color=ft.Colors.GREY_600),
                        ft.TextButton(
                            "立即登录",
                            on_click=lambda: app.view_builder.goto("login"),
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
