"""订单详情页（含地图）。"""

import flet as ft
import flet_map as ftm

from routemanager import RouteManager
from views.components import (
    LEVEL_COLORS,
    ORDER_STATUSES,
    STATUS_COLOR,
    STATUS_ICON,
    close_dialog,
    make_pin,
    show_cancel_order_dialog,
)


def build_map_layers(app, start_gps, end_gps):
    """根据大疆解析出的 zones 数据，构建 Flet Map 的图层列表"""
    polygon_markers = []
    circle_markers = []

    zones = RouteManager.get_nfz(start_gps[0], start_gps[1], end_gps[0], end_gps[1])

    for zone in zones:
        color = LEVEL_COLORS.get(zone["level"])
        opacity = 0.25 if zone["level"] == 2 else 0.4

        if zone["geometry"]["type"] == "polygon":
            pts = zone["geometry"]["points"]
            coordinates = [
                ftm.MapLatitudeLongitude(lat, lng)
                for lat, lng in pts
            ]

            polygon_markers.append(
                ftm.PolygonMarker(
                    coordinates=coordinates,
                    color=ft.Colors.with_opacity(opacity, color),
                    border_color=color,
                    border_stroke_width=2
                )
            )

        elif zone["geometry"]["type"] == "circle":
            center_lat, center_lng = zone["geometry"]["center"]
            radius = zone["geometry"]["radius"]

            circle_markers.append(
                ftm.CircleMarker(
                    coordinates=ftm.MapLatitudeLongitude(center_lat, center_lng),
                    radius=radius,
                    use_radius_in_meter=True,
                    color=ft.Colors.with_opacity(opacity, color),
                    border_color=color,
                    border_stroke_width=2,
                )
            )

    layers = [
        ftm.TileLayer(
            url_template="https://webrd01.is.autonavi.com/appmaptile?size=1&scale=1&style=8&x={x}&y={y}&z={z}",
        ),
        ftm.PolygonLayer(polygons=polygon_markers),
        ftm.CircleLayer(circles=circle_markers),
        ftm.MarkerLayer(
            markers=[
                ftm.Marker(
                    content=make_pin(ft.Icons.FLIGHT_TAKEOFF, ft.Colors.GREEN_600),
                    coordinates=ftm.MapLatitudeLongitude(start_gps[0], start_gps[1]),
                    width=36,
                    height=50,
                ),
                ftm.Marker(
                    content=make_pin(ft.Icons.FLIGHT_LAND, ft.Colors.RED_500),
                    coordinates=ftm.MapLatitudeLongitude(end_gps[0], end_gps[1]),
                    width=36,
                    height=50,
                ),
                ftm.Marker(
                    content=make_pin(ft.Icons.FLIGHT_LAND, ft.Colors.BLUE_500),
                    coordinates=ftm.MapLatitudeLongitude(
                        app.drone_controller.get_state()["lat"],
                        app.drone_controller.get_state()["lon"]
                    ),
                    width=36,
                    height=50,
                ),
            ]
        ),
    ]

    return layers


def build_order_detail(app, order_id: str, **kwargs):
    """订单详情页（含地图）"""
    phone = app.config.get("last_user")
    order = app.user_manager.get_order_by_id(phone, order_id)
    drone = app.drone_manager.get_by_id(order["drone_id"])

    current = order.get("status")
    all_statuses = ["待配送", "租赁中", "已完成"]  # 时间线步骤（不含"已取消"）

    start = app.user_manager.get_location_by_address(phone, order["start_address"])
    START_LNG = float(start.split(",")[0])
    START_LAT = float(start.split(",")[1])

    end = app.user_manager.get_location_by_address(phone, order["address"])
    END_LNG = float(end.split(",")[0])
    END_LAT = float(end.split(",")[1])

    CENTER_LAT = (START_LAT + END_LAT) / 2
    CENTER_LNG = (START_LNG + END_LNG) / 2

    map_widget = ftm.Map(
        height=220,
        initial_center=ftm.MapLatitudeLongitude(CENTER_LAT, CENTER_LNG),
        initial_zoom=13,
        min_zoom=3,
        max_zoom=18,
        layers=build_map_layers(app, (START_LAT, START_LNG), (END_LAT, END_LNG))
    )

    map_legend = ft.Row([
        ft.Row([
            ft.Container(width=10, height=10, bgcolor=ft.Colors.GREEN_600, border_radius=5),
            ft.Text("装货地址", size=11, color=ft.Colors.GREY_600),
        ], spacing=4),
        ft.Row([
            ft.Container(width=10, height=10, bgcolor=ft.Colors.RED_500, border_radius=5),
            ft.Text("收货地址", size=11, color=ft.Colors.GREY_600),
        ], spacing=4),
        ft.Row([
            ft.Container(width=10, height=10, bgcolor=ft.Colors.RED_400, border_radius=2),
            ft.Text("禁飞区", size=11, color=ft.Colors.GREY_600),
        ], spacing=4),
        ft.Row([
            ft.Container(width=10, height=10, bgcolor=ft.Colors.ORANGE_400, border_radius=2),
            ft.Text("警示区", size=11, color=ft.Colors.GREY_600),
        ], spacing=4)
    ], spacing=16)

    def build_timeline():
        if current == "已取消":
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CANCEL_OUTLINED, color=ft.Colors.RED_400, size=20),
                    ft.Text("订单已取消", size=14, color=ft.Colors.RED_400),
                ], spacing=8),
                padding=ft.Padding.symmetric(vertical=10),
            )

        nodes = []
        for i, s in enumerate(all_statuses):
            is_done = all_statuses.index(current) >= i if current in all_statuses else False
            nodes.append(
                ft.Column([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.CHECK_CIRCLE if is_done else ft.Icons.RADIO_BUTTON_UNCHECKED,
                            color=ft.Colors.BLUE if is_done else ft.Colors.GREY_400,
                            size=20,
                        ),
                    ),
                    ft.Text(s, size=11, color=ft.Colors.BLUE if is_done else ft.Colors.GREY_400),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
            )
            if i < len(all_statuses) - 1:
                nodes.append(
                    ft.Container(
                        width=50, height=2,
                        bgcolor=ft.Colors.BLUE if all_statuses.index(current) > i else ft.Colors.GREY_300,
                        margin=ft.Margin.only(bottom=18),
                    )
                )

        return ft.Row(nodes, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def on_cancel(_):
        def confirm_cancel():
            app.user_manager.update_order_status(phone, order_id, "已取消")
            app.view_builder.goto("order_detail", order_id=order_id)

        show_cancel_order_dialog(app, on_confirm=confirm_cancel)

    def info_row(icon, label, value):
        return ft.Row([
            ft.Icon(icon, size=16, color=ft.Colors.GREY_500),
            ft.Text(label, size=13, color=ft.Colors.GREY_600, width=70),
            ft.Text(value, size=13, expand=True),
        ], spacing=10)

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda: app.view_builder.goto("orders", selected_index=ORDER_STATUSES.index(current)),
                ),
                ft.Text("订单详情", size=20, weight="bold", expand=True),
            ]),
            padding=ft.Padding(15, 20, 15, 15),
            bgcolor=ft.Colors.WHITE,
        ),

        ft.Container(
            content=ft.Column([

                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(
                                STATUS_ICON.get(current, ft.Icons.INFO),
                                color=STATUS_COLOR.get(current, ft.Colors.GREY_400),
                                size=28,
                            ),
                            ft.Column([
                                ft.Text(current, size=18, weight="bold",
                                        color=STATUS_COLOR.get(current, ft.Colors.GREY_400)),
                                ft.Text(f"订单号：{order['id']}", size=11, color=ft.Colors.GREY_500),
                            ], spacing=2, expand=True),
                        ], spacing=12),
                        ft.Container(height=15),
                        build_timeline(),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                ),

                ft.Container(height=15),

                ft.Container(
                    content=ft.Column([
                        ft.Text("飞行路线", size=15, weight="bold"),
                        ft.Container(height=10),
                        ft.Container(
                            content=map_widget,
                            border_radius=10,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        ),
                        ft.Container(height=8),
                        map_legend,
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                ),

                ft.Container(height=15),

                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(drone["images"][0] if drone else "🚁", size=50),
                            width=80, height=80,
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=12,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column([
                            ft.Text(order["drone_name"], size=16, weight="bold"),
                            ft.Text(drone["specs"] if drone else "", size=13, color=ft.Colors.GREY_600),
                        ], spacing=4, expand=True),
                    ], spacing=15),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                ),

                ft.Container(height=15),

                ft.Container(
                    content=ft.Column([
                        ft.Text("租赁信息", size=15, weight="bold"),
                        ft.Container(height=10),
                        info_row(ft.Icons.FLIGHT_TAKEOFF, "装货地址", order["start_address"]),
                        ft.Divider(height=12, color=ft.Colors.GREY_100),
                        info_row(ft.Icons.FLIGHT_LAND, "收货地址", order["address"]),
                        ft.Divider(height=12, color=ft.Colors.GREY_100),
                        info_row(ft.Icons.PLAY_CIRCLE_OUTLINE, "开始时间", order["start_time"]),
                        ft.Divider(height=12, color=ft.Colors.GREY_100),
                        info_row(ft.Icons.CALENDAR_TODAY, "下单时间", order["created_at"]),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                ),

                ft.Container(height=15),

                ft.Container(
                    content=ft.Column([
                        ft.Text("费用明细", size=15, weight="bold"),
                        ft.Container(height=10),
                        ft.Row([
                            ft.Text("租赁费用", size=14, color=ft.Colors.GREY_600, expand=True),
                            ft.Text(f"¥{order['total_price']}", size=14),
                        ]),
                        ft.Divider(height=12, color=ft.Colors.GREY_100),
                        ft.Row([
                            ft.Text("实付金额", size=15, weight="bold", expand=True),
                            ft.Text(f"¥{order['total_price']}", size=20,
                                    color=ft.Colors.RED_700, weight="bold"),
                        ]),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                ),

                ft.Container(height=25),

                ft.Button(
                    "取消订单",
                    width=float("inf"),
                    height=55,
                    bgcolor=ft.Colors.RED_400,
                    color=ft.Colors.WHITE,
                    on_click=on_cancel,
                    visible=current == "待配送",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                ),

                ft.Container(height=10),

            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=20,
        ),
    ], expand=True)
