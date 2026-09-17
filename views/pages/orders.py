"""订单列表页（含 build_order_card 与 build_tab_content）。"""

import flet as ft

from views.components import ORDER_STATUSES, STATUS_COLOR, STATUS_ICON, show_cancel_order_dialog


def build_orders(app, selected_index=None, **kwargs):
    """构建订单页"""
    phone = app.config.get("last_user")

    if not phone:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=100, color=ft.Colors.GREY_400),
                ft.Text("请先登录", size=20, weight="bold"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER),
            expand=True,
        )

    tabs_container = ft.Container(expand=True)
    selected_index = selected_index or 0

    def build_order_card(phone, order, refresh):
        def on_cancel(_):
            def confirm_cancel():
                app.user_manager.update_order_status(phone, order["id"], "已取消")
                refresh()

            show_cancel_order_dialog(app, on_confirm=confirm_cancel)

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(order["drone_name"], size=15, weight="bold", expand=True),
                    ft.Container(
                        content=ft.Text(
                            order["status"], size=12, color=ft.Colors.WHITE,
                        ),
                        bgcolor=STATUS_COLOR[order["status"]],
                        padding=ft.Padding.symmetric(vertical=3, horizontal=10),
                        border_radius=12,
                    ),
                ]),
                ft.Divider(height=10, color=ft.Colors.GREY_200),
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, size=14, color=ft.Colors.GREY_500),
                    ft.Text(
                        f"{order['start_time']}",
                        size=12, color=ft.Colors.GREY_600,
                    ),
                ], spacing=6),
                ft.Row([
                    ft.Icon(ft.Icons.LOCATION_ON, size=14, color=ft.Colors.GREY_500),
                    ft.Text(order["start_address"], size=12, color=ft.Colors.GREY_600, expand=True, max_lines=1),
                ], spacing=6),
                ft.Row([
                    ft.Icon(ft.Icons.LOCATION_ON, size=14, color=ft.Colors.GREY_500),
                    ft.Text(order["address"], size=12, color=ft.Colors.GREY_600, expand=True, max_lines=1),
                ], spacing=6),
                ft.Divider(height=10, color=ft.Colors.GREY_200),
                ft.Row([
                    ft.Text(f"¥{order['total_price']}", size=18,
                            color=ft.Colors.RED_700, weight="bold", expand=True),
                    ft.TextButton(
                        "取消订单",
                        on_click=on_cancel,
                        style=ft.ButtonStyle(color=ft.Colors.RED_400),
                        visible=order.get("status") == "待配送",
                    ),
                    ft.TextButton(
                        "查看详情",
                        on_click=lambda _, oid=order["id"]: app.view_builder.goto("order_detail", order_id=oid),
                        style=ft.ButtonStyle(color=ft.Colors.BLUE),
                    ),
                ]),
            ], spacing=6),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
        )

    def build_tab_content(phone, status, refresh):
        orders = [o for o in app.user_manager.get_orders(phone) if o.get("status") == status]

        if not orders:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=80, color=ft.Colors.GREY_400),
                    ft.Text("暂无订单", size=16, color=ft.Colors.GREY_600)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER),
                expand=True
            )

        return ft.Column([
            build_order_card(phone, o, refresh) for o in reversed(orders)
        ], spacing=12, scroll=ft.ScrollMode.AUTO)

    def refresh():
        tabs_container.content = build_tabs()
        app.page.update()

    def build_tabs():
        tab_contents = [build_tab_content(phone, label, refresh) for label in ORDER_STATUSES]

        def build_tab_row():
            def on_tab_click(idx):
                nonlocal selected_index
                selected_index = idx
                tab_bar.content = build_tab_row()
                content_container.content = tab_contents[idx]
                tab_bar.update()
                content_container.update()

            return ft.Row([
                ft.Container(
                    content=ft.Text(
                        label,
                        size=14,
                        weight="bold" if i == selected_index else "normal",
                        color=ft.Colors.BLUE if i == selected_index else ft.Colors.GREY_600,
                    ),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                    border=ft.Border(
                        bottom=ft.BorderSide(
                            2, ft.Colors.BLUE if i == selected_index else ft.Colors.TRANSPARENT
                        )
                    ),
                    on_click=lambda _, idx=i: on_tab_click(idx),
                    ink=True,
                )
                for i, label in enumerate(ORDER_STATUSES)
            ], spacing=0)

        tab_bar = ft.Container(
            content=build_tab_row(),
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK_12, offset=ft.Offset(0, 2)),
        )

        content_container = ft.Container(
            content=tab_contents[selected_index],
            expand=True,
            padding=ft.Padding.symmetric(horizontal=15, vertical=15),
        )

        return ft.Column([
            tab_bar,
            content_container,
        ], expand=True, spacing=0)

    refresh()

    return ft.Column([
        ft.Container(
            content=ft.Text("我的订单", size=20, weight="bold"),
            padding=ft.Padding(20, 25, 20, 15),
            bgcolor=ft.Colors.WHITE,
        ),
        tabs_container,
    ], expand=True, spacing=0)
