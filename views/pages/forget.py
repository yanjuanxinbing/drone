"""忘记密码页。"""

import re
import flet as ft

from views.components import PHONE_PATTERN


def build_forget(app, **kwargs):
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

    submit_btn = ft.Button(
        "验证手机号",
        width=350, height=55,
        bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
    )

    verified = {"value": False}

    def on_submit(_):
        if not verified["value"]:
            # 第一步：验证手机号
            phone = phone_field.value
            if not phone:
                app.view_builder.show_snackbar("请输入手机号", ft.Colors.RED_400)
                return

            if not re.match(PHONE_PATTERN, phone):
                app.view_builder.show_snackbar("请输入正确的11位手机号码", ft.Colors.RED_400)
                return

            if not app.user_manager.contains(phone):
                app.view_builder.show_snackbar("该手机号未注册", ft.Colors.RED_400)
                return

            verified["value"] = True
            phone_field.read_only = True
            new_password_field.visible = True
            confirm_password_field.visible = True
            submit_btn.content = "确认重置"
            app.page.update()
        else:
            # 第二步：重置密码
            new_pwd = new_password_field.value
            confirm = confirm_password_field.value
            phone = phone_field.value

            if not new_pwd:
                app.view_builder.show_snackbar("请输入新密码", ft.Colors.RED_400)
                return

            if len(new_pwd) < 6:
                app.view_builder.show_snackbar("新密码至少需要6位", ft.Colors.RED_400)
                return

            if new_pwd != confirm:
                app.view_builder.show_snackbar("两次输入的密码不一致", ft.Colors.RED_400)
                return

            app.user_manager.update_password(phone, new_pwd)
            app.view_builder.show_snackbar("密码重置成功，请重新登录", ft.Colors.GREEN_400)
            app.view_builder.goto("login")

    submit_btn.on_click = on_submit

    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda: app.view_builder.goto("login"),
                    ),
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
