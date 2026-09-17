"""登录页。"""

import flet as ft


def build_login(app, **kwargs):
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

    def on_login_submit(_):
        phone_number = phone_number_field.value
        password = password_field.value

        if not phone_number:
            app.view_builder.show_snackbar("请输入手机号", ft.Colors.RED_400)
            return

        if not password:
            app.view_builder.show_snackbar("请输入密码", ft.Colors.RED_400)
            return

        if app.user_manager.verify_login(phone_number, password):
            app.config.set("last_user", phone_number)
        else:
            app.view_builder.show_snackbar("手机号或密码错误", ft.Colors.RED_400)
            return

        app.view_builder.goto("profile")

    return ft.Container(
        content=ft.Column([
            # 顶部返回按钮
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda: app.view_builder.goto("profile"),
                    ),
                    ft.Text("登录", size=20, weight="bold"),
                ]),
                padding=ft.Padding.only(left=10, right=20, top=20, bottom=10),
            ),

            # 登录表单区域
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.ACCOUNT_CIRCLE,
                            size=100,
                            color=ft.Colors.BLUE,
                        ),
                        alignment=ft.Alignment.CENTER,
                    ),

                    ft.Container(height=30),

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

                    phone_number_field,
                    ft.Container(height=15),
                    password_field,

                    ft.Container(height=10),

                    ft.Container(
                        content=ft.TextButton(
                            "忘记密码？",
                            on_click=lambda: app.view_builder.goto("forget"),
                        ),
                        alignment=ft.Alignment.CENTER_RIGHT,
                    ),

                    ft.Container(height=20),

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

                    ft.Row([
                        ft.Text("还没有账号？", size=14, color=ft.Colors.GREY_600),
                        ft.TextButton(
                            "立即注册",
                            on_click=lambda: app.view_builder.goto("register"),
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
