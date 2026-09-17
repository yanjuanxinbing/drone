"""协议首启页（从 App.before_main 拆出）。"""

import sys
import flet as ft

from file import FileReader
from views.components import show_document_dialog


def build_agreement(app):
    """首次启动的协议同意页。"""

    def on_agree_click(_):
        app.config.set("agreed", True)
        app.page.controls.clear()
        app.main(app.page)

    user_agreement_text = FileReader.read_txt("user_agreement_text.txt")
    privacy_policy_text = FileReader.read_txt("privacy_policy_text.txt")

    return ft.Container(
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
                            on_click=lambda _: show_document_dialog(app, "用户协议", user_agreement_text),
                        ),
                        ft.Text("和", size=14),
                        ft.TextButton(
                            "《隐私政策》",
                            on_click=lambda _: show_document_dialog(app, "隐私政策", privacy_policy_text),
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
                ft.Button(
                    "同意并继续",
                    on_click=on_agree_click,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                ),
            ], alignment="center", spacing=20),
        ], horizontal_alignment="center", alignment="center"),
        expand=True,
        bgcolor=ft.Colors.WHITE,
        padding=50,
    )
