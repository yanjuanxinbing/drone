"""地址选择页（下单流程专用，依赖 addresses 模块）。"""

import flet as ft

from .addresses import build_address_list, show_address_dialog


def build_address_picker(app, drone_id: str, is_booking: bool,
                         selected_address=None, start_address=None,
                         is_start: bool = False, **kwargs):
    """地址选择页"""
    phone = app.config.get("last_user")

    list_container = ft.Container(expand=True)

    def refresh():
        list_container.content = build_address_list(
            app, phone, refresh,
            drone_id, is_booking, selected_address, start_address, is_start,
        )
        app.page.update()

    refresh()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda: app.view_builder.goto(
                        "order",
                        drone_id=drone_id, is_booking=is_booking,
                        selected_address=selected_address, start_address=start_address,
                    ),
                ),
                ft.Text("选择地址", size=20, weight="bold", expand=True),
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    icon_color=ft.Colors.BLUE,
                    on_click=lambda: app.page.run_task(show_address_dialog, app, phone, refresh),
                ),
            ]),
            padding=ft.Padding(15, 20, 15, 15),
            bgcolor=ft.Colors.WHITE,
        ),

        ft.Container(
            content=ft.Column([
                list_container,
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=20,
        ),
    ], expand=True)
