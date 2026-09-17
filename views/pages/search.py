"""搜索结果页。"""

import flet as ft

from views.components import build_card


def build_search(app, keyword: str, **kwargs):
    """搜索结果页"""
    results = app.drone_manager.search(keyword)

    if results:
        content = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=250,
            child_aspect_ratio=0.75,
            spacing=15,
            run_spacing=15,
            controls=[
                build_card(
                    app,
                    drone_id=drone["id"],
                    name=drone["name"],
                    price=str(drone["price"]),
                    tag=drone["tag"],
                    specs=drone["specs"],
                ) for drone in results
            ],
        )
    else:
        content = ft.Container(
            content=ft.Column([
                ft.Text("🔍", size=80),
                ft.Container(height=10),
                ft.Text("没有找到相关机型", size=18, weight="bold"),
                ft.Container(height=8),
                ft.Text(
                    f"试试其他关键词？",
                    size=14,
                    color=ft.Colors.GREY_600,
                ),
                ft.Container(height=20),
                ft.OutlinedButton(
                    "返回首页",
                    icon=ft.Icons.HOME_OUTLINED,
                    on_click=lambda: app.view_builder.goto("home"),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER),
            expand=True,
        )

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda: app.view_builder.goto("home")),
                ft.TextField(
                    value=keyword,
                    prefix_icon=ft.Icons.SEARCH,
                    border_radius=15,
                    filled=True,
                    expand=True,
                    on_submit=lambda e: app.view_builder.goto("search", keyword=e.control.value),
                ),
            ], spacing=5),
            padding=ft.Padding(10, 20, 20, 15),
            bgcolor=ft.Colors.WHITE,
        ),

        ft.Container(
            content=ft.Text(
                f"{keyword} 共 {len(results)} 个结果" if results else f"未找到 {keyword}",
                size=13,
                color=ft.Colors.GREY_600,
            ),
            padding=ft.Padding.symmetric(horizontal=20, vertical=8),
        ),

        ft.Container(
            content=content,
            padding=ft.Padding.symmetric(horizontal=20),
            expand=True,
        ),
    ], expand=True)
