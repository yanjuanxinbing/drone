"""个人信息编辑页。"""

import datetime
import flet as ft

from file import FileReader, FileWriter


def build_personal_info(app, **kwargs):
    """个人信息编辑页面"""
    phone = app.config.get("last_user")
    username = app.user_manager.get(phone)["nick_name"]
    gender_val = app.user_manager.get(phone)["gender"]
    birthday_val = app.user_manager.get(phone)["birthday"]

    user_avatar = ft.CircleAvatar(
        content=ft.Icon(ft.Icons.PERSON, size=40),
        radius=50,
        foreground_image_src=FileReader.read_img(f"{phone}.png")
    )

    file_picker = ft.FilePicker()

    async def select(_):
        files = await file_picker.pick_files(
            file_type=ft.FilePickerFileType.IMAGE,
            with_data=True
        )
        if files:
            user_avatar.foreground_image_src = files[0].bytes
            user_avatar.update()

    nickname_field = ft.TextField(
        label="昵称", value=username, border_radius=10, width=350
    )

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

    birthday_field = ft.TextField(
        label="出生日期",
        value=birthday_val,
        read_only=True,
        border_radius=10,
        width=310,
        hint_text="点击图标选择日期",
    )

    def on_date_change(e):
        picked_date = e.control.value
        local_date = picked_date.astimezone()
        selected_date_str = local_date.strftime("%Y-%m-%d")
        birthday_field.value = selected_date_str
        birthday_field.update()

    date_picker = ft.DatePicker(
        value=datetime.datetime.strptime(birthday_val, "%Y-%m-%d") if birthday_val else None,
        on_change=on_date_change,
        first_date=datetime.datetime(1900, 1, 1),
        last_date=datetime.datetime.now().astimezone(),
    )

    def on_save_click(_):
        new_nickname = nickname_field.value.strip()
        if not new_nickname:
            app.view_builder.show_snackbar("昵称不能为空", ft.Colors.RED_400)
            return

        avatar_bytes = user_avatar.foreground_image_src
        if avatar_bytes is not None:
            FileWriter.save_avatar(f"{phone}.png", avatar_bytes)

        app.user_manager.update_value(phone, new_nickname, gender_dropdown.value, birthday_field.value)
        app.view_builder.show_snackbar("个人信息已保存", ft.Colors.GREEN_400)

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: app.view_builder.goto("settings")),
                ft.Text("个人信息", size=20, weight="bold", expand=True),
            ]),
            padding=ft.Padding(15, 20, 15, 15),
            bgcolor=ft.Colors.WHITE,
        ),

        ft.Container(
            content=ft.Column([
                ft.Container(height=20),
                ft.Column([
                    user_avatar,
                    ft.TextButton("更换头像", icon=ft.Icons.CAMERA_ALT_OUTLINED, on_click=select),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                ft.Column([
                    nickname_field,
                    gender_dropdown,
                    ft.Row([
                        birthday_field,
                        ft.IconButton(
                            icon=ft.Icons.CALENDAR_MONTH,
                            on_click=lambda: app.page.show_dialog(date_picker),
                            icon_color=ft.Colors.BLUE,
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                ft.Container(height=30),
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
