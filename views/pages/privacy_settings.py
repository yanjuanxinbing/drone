"""隐私设置页。"""

import flet as ft

from file import FileReader
from views.components import close_dialog, show_document_dialog


def build_privacy_settings(app, **kwargs):
    """隐私设置页面"""

    def show_delete_dialog(_):
        def on_confirm(_):
            phone = app.config.get("last_user")
            app.user_manager.delete(phone)
            app.config.logout()
            close_dialog(confirm_dialog, app.page)
            app.view_builder.goto("profile")

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("删除账号", weight="bold"),
            content=ft.Text("此操作不可逆，账号及所有数据将被永久删除，确认继续？"),
            actions=[
                ft.TextButton("取消", on_click=lambda _: close_dialog(confirm_dialog, app.page)),
                ft.Button(
                    "确认删除",
                    bgcolor=ft.Colors.RED_400,
                    color=ft.Colors.WHITE,
                    on_click=on_confirm,
                ),
            ],
        )
        app.page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        app.page.update()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: app.view_builder.goto("settings")),
                ft.Text("隐私设置", size=20, weight="bold", expand=True),
            ]),
            padding=ft.Padding(15, 20, 15, 15),
            bgcolor=ft.Colors.WHITE,
        ),

        ft.Container(
            content=ft.Column([

                ft.Container(
                    content=ft.Text("隐私说明", size=16, weight="bold", color=ft.Colors.BLUE_700),
                    padding=ft.Padding.only(left=5, top=20, bottom=10),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PRIVACY_TIP_OUTLINED),
                    title=ft.Text("隐私政策"),
                    subtitle=ft.Text("了解我们如何收集和使用您的数据"),
                    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                    on_click=lambda: show_document_dialog(
                        app, "隐私政策",
                        FileReader.read_txt("privacy_policy_text.txt")
                    ),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED),
                    title=ft.Text("用户协议"),
                    subtitle=ft.Text("查看用户服务协议"),
                    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                    on_click=lambda: show_document_dialog(
                        app, "用户协议",
                        FileReader.read_txt("user_agreement_text.txt")
                    ),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED),
                    title=ft.Text("应用权限说明"),
                    subtitle=ft.Text("定位、存储等权限的使用说明"),
                    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                    on_click=lambda: show_document_dialog(
                        app, "应用权限说明",
                        FileReader.read_txt("app_permission_text.txt")
                    ),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CHILD_CARE),
                    title=ft.Text("未成年人保护"),
                    subtitle=ft.Text("未成年人使用须知"),
                    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                    on_click=lambda: show_document_dialog(
                        app, "未成年人保护",
                        FileReader.read_txt("minor_protection_text.txt")
                    ),
                ),

                ft.Container(
                    content=ft.Text("账号与数据", size=16, weight="bold", color=ft.Colors.BLUE_700),
                    padding=ft.Padding.only(left=5, top=25, bottom=10),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DELETE_FOREVER_OUTLINED, color=ft.Colors.RED_400),
                    title=ft.Text("删除账号", color=ft.Colors.RED_400),
                    subtitle=ft.Text("永久删除账号及所有数据"),
                    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                    on_click=show_delete_dialog,
                ),

            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=ft.Padding.symmetric(horizontal=20),
        ),
    ], expand=True)
