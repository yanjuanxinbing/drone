"""修改密码页。"""

import flet as ft


def build_change_password(app, **kwargs):
    """修改密码页面"""
    phone = app.config.get("last_user")

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

    def on_save_click(_):
        current = current_password_field.value
        new_pwd = new_password_field.value
        confirm = confirm_password_field.value

        if not current:
            app.view_builder.show_snackbar("请输入当前密码", ft.Colors.RED_400)
            return

        if not app.user_manager.verify_login(phone, current):
            app.view_builder.show_snackbar("当前密码错误", ft.Colors.RED_400)
            return

        if not new_pwd:
            app.view_builder.show_snackbar("请输入新密码", ft.Colors.RED_400)
            return

        if len(new_pwd) < 6:
            app.view_builder.show_snackbar("新密码至少需要6位", ft.Colors.RED_400)
            return

        if new_pwd == current:
            app.view_builder.show_snackbar("新密码不能与当前密码相同", ft.Colors.RED_400)
            return

        if new_pwd != confirm:
            app.view_builder.show_snackbar("两次输入的密码不一致", ft.Colors.RED_400)
            return

        app.user_manager.update_password(phone, new_pwd)
        app.view_builder.show_snackbar("密码修改成功", ft.Colors.GREEN_400)

        current_password_field.value = ""
        new_password_field.value = ""
        confirm_password_field.value = ""
        app.page.update()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: app.view_builder.goto("settings")),
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
