"""首页。"""

import flet as ft

from views.components import build_card


def build_home(app, **kwargs):
    """构建首页"""
    phone = app.config.get("last_user")
    header = ft.Container(
        content=ft.Text("DroneGo", size=32, weight="bold", color="white"),
        bgcolor=ft.Colors.BLUE,
        padding=30,
        width=float("inf"),
        border_radius=ft.BorderRadius.only(bottom_left=30, bottom_right=30),
    )

    def on_search(e):
        keyword = e.control.value
        if keyword:
            app.view_builder.goto("search", keyword=keyword)

    search_bar = ft.Container(
        content=ft.TextField(
            prefix_icon=ft.Icons.SEARCH,
            hint_text="搜索无人机型号...",
            border_radius=15,
            filled=True,
            on_submit=on_search,
            bgcolor=ft.Colors.WHITE,
        ),
        padding=ft.Padding.symmetric(horizontal=20),
        margin=ft.Margin.only(top=-25),
    )

    # 从数据文件获取热门无人机
    hot_drones = app.drone_manager.get_hot(limit=4)

    drone_grid = ft.GridView(
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
                price=str(f"{drone['price'] / 100.0}/千米"),
                tag=drone["tag"],
                specs=drone["specs"]
            ) for drone in hot_drones
        ],
    )

    play_banner = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.WHITE),
            ft.Text("全新功能：立即驾驶"),
        ]),
        bgcolor=ft.Colors.ORANGE,
        padding=15,
        border_radius=12,
        margin=ft.Margin.symmetric(horizontal=20),
        on_click=lambda: app.view_builder.goto("play_rent") if phone and app.user_manager.pilot(phone)
        else app.view_builder.show_snackbar("请先进行飞手认证", ft.Colors.RED_500)
    )

    return ft.Column([
        header,
        search_bar,
        play_banner,
        ft.Container(height=10),
        ft.Container(
            content=ft.Text("推荐机型", size=18, weight="bold"),
            padding=ft.Padding.symmetric(horizontal=20)
        ),
        ft.Container(content=drone_grid, padding=20, expand=True),
    ], scroll=ft.ScrollMode.AUTO, expand=True)
