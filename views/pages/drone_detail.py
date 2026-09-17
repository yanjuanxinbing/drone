"""无人机详情页。"""

import flet as ft


def build_drone_detail(app, drone_id: str, **kwargs):
    """构建无人机详情页"""
    drone = app.drone_manager.get_by_id(drone_id)

    top_bar = ft.Container(
        content=ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda: app.view_builder.goto("home"),
            ),
            ft.Text("商品详情", size=18, weight="bold", expand=True)
        ]),
        padding=ft.Padding.only(left=10, right=10, top=20, bottom=10),
        bgcolor=ft.Colors.WHITE,
    )

    image_section = ft.Container(
        content=ft.Column([
            ft.Text(drone["images"][0], size=120),
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        width=8,
                        height=8,
                        border_radius=4,
                        bgcolor=ft.Colors.BLUE,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=10,
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.BLUE_50,
        padding=30,
    )

    title_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text(drone["tag"], size=12, color="white"),
                    bgcolor=ft.Colors.BLUE,
                    padding=ft.Padding.symmetric(vertical=4, horizontal=10),
                    border_radius=4,
                ),
                ft.Container(
                    content=ft.Text(f"已售 {drone['sales']}", size=12, color=ft.Colors.GREY_600),
                ),
            ], spacing=10),
            ft.Container(height=10),
            ft.Text(drone["name"], size=24, weight="bold"),
            ft.Container(height=10),
            ft.Row([
                ft.Column([
                    ft.Text(f"¥{drone['price'] / 100.0}/千米", size=32, color=ft.Colors.RED_700),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.START),
                ft.Text(
                    f"原价 ¥{drone['original_price'] / 100.0}",
                    size=14,
                    color=ft.Colors.GREY_500,
                    style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                ),
            ], spacing=15, alignment=ft.MainAxisAlignment.START),
        ]),
        padding=20,
        bgcolor=ft.Colors.WHITE,
    )

    specs_section = ft.Container(
        content=ft.Column([
            ft.Text("产品特性", size=18, weight="bold"),
            ft.Container(height=10),
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=20, color=ft.Colors.GREEN),
                    ft.Text(feature, size=14),
                ], spacing=10) for feature in drone["features"]
            ], spacing=8),
        ]),
        padding=20,
        bgcolor=ft.Colors.WHITE,
        margin=ft.Margin.only(top=10),
    )

    description_section = ft.Container(
        content=ft.Column([
            ft.Text("商品介绍", size=18, weight="bold"),
            ft.Container(height=10),
            ft.Text(
                drone["description"],
                size=14,
                color=ft.Colors.GREY_700,
            ),
        ]),
        padding=20,
        bgcolor=ft.Colors.WHITE,
        margin=ft.Margin.only(top=10),
    )

    stock_section = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=16, color=ft.Colors.GREY_600),
            ft.Text(
                f"库存：{drone['stock']} 件",
                size=14,
                color=ft.Colors.GREY_600,
            ),
        ], spacing=5),
        padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        bgcolor=ft.Colors.WHITE,
        margin=ft.Margin.only(top=10),
    )

    def on_rent_now(_):
        app.view_builder.goto("order", drone_id=drone["id"], is_booking=False)

    def on_book(_):
        app.view_builder.goto("order", drone_id=drone["id"], is_booking=True)

    bottom_bar = ft.Container(
        content=ft.Row([
            ft.OutlinedButton(
                "预约租赁",
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=on_book,
                expand=True,
                height=50,
            ),
            ft.Button(
                "立即租赁",
                icon=ft.Icons.FLIGHT_TAKEOFF,
                on_click=on_rent_now,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                expand=True,
                height=50,
            ),
        ], spacing=10),
        padding=ft.Padding.all(15),
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.BLACK_12,
            offset=ft.Offset(0, -2),
        ),
    )

    main_content = ft.Column([
        ft.Column([
            image_section,
            title_section,
            specs_section,
            description_section,
            stock_section,
        ], scroll=ft.ScrollMode.AUTO, expand=True),
    ], spacing=0, expand=True)

    return ft.Column([
        top_bar,
        main_content,
        bottom_bar,
    ], spacing=0, expand=True)
