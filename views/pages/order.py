"""下单页（含价格档位常量）。"""

import datetime
import flet as ft

from routemanager import RouteManager
from views.components import calc_distance

# 价格档位（距离上限 km, 起步价 ¥）
PRICE_TIERS = [(3, 6), (6, 9), (10, 13), (15, 18), (float("inf"), 30)]


def _calc_base_price(distance_km: float) -> int:
    for limit, base in PRICE_TIERS:
        if distance_km <= limit:
            return base
    return PRICE_TIERS[-1][1]


def build_order(app, drone_id: str, is_booking: bool = False,
                selected_address: str = None, start_address: str = None, **kwargs):
    """下单页"""
    drone = app.drone_manager.get_by_id(drone_id)
    phone = app.config.get("last_user")
    addresses = app.user_manager.get_addresses(phone)

    # 默认选第一个地址
    if selected_address is None:
        selected_address = addresses[0]["address"] if addresses else ""

    start_address_display = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLUE, size=20),
            ft.Text(
                start_address or "请选择装货地址",
                size=14,
                expand=True,
                color=ft.Colors.BLACK if start_address else ft.Colors.GREY_400,
            ),
            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
        ]),
        padding=ft.Padding(15, 12, 15, 12),
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        on_click=lambda: app.view_builder.goto(
            "address_picker",
            drone_id=drone_id, is_booking=is_booking,
            selected_address=selected_address, start_address=start_address, is_start=True,
        ),
        ink=True
    )

    address_display = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLUE, size=20),
            ft.Text(
                selected_address or "请选择收货地址",
                size=14,
                expand=True,
                color=ft.Colors.BLACK if selected_address else ft.Colors.GREY_400,
            ),
            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
        ]),
        padding=ft.Padding(15, 12, 15, 12),
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        on_click=lambda: app.view_builder.goto(
            "address_picker",
            drone_id=drone_id, is_booking=is_booking,
            selected_address=selected_address, start_address=start_address, is_start=False,
        ),
        ink=True
    )

    start_field = ft.TextField(
        label="预约开始时间",
        value=datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
        read_only=True,
        border_radius=10,
        hint_text="点击选择时间",
        prefix_icon=ft.Icons.CALENDAR_MONTH,
        visible=is_booking,
        width=310,
    )

    def update_start_field(_):
        dt = datetime.datetime.combine(date_picker.value.astimezone(), time_picker.value).astimezone()
        now = datetime.datetime.now().astimezone()

        if dt < now:
            dt = now

        start_field.value = dt.strftime("%Y-%m-%d %H:%M")
        start_field.update()

    date_picker = ft.DatePicker(
        value=datetime.datetime.now().astimezone(),
        on_change=update_start_field,
        first_date=datetime.datetime.now().astimezone(),
        last_date=datetime.datetime.now().astimezone() + datetime.timedelta(days=30),
    )

    time_picker = ft.TimePicker(
        on_change=update_start_field,
        confirm_text="确认",
        cancel_text="取消",
        help_text="选择时间",
    )

    start_row = ft.Row([
        start_field,
        ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            icon_color=ft.Colors.BLUE,
            on_click=lambda: app.page.show_dialog(date_picker),
            visible=is_booking,
            tooltip="选择日期",
        ),
        ft.IconButton(
            icon=ft.Icons.ACCESS_TIME,
            icon_color=ft.Colors.BLUE,
            on_click=lambda: app.page.show_dialog(time_picker),
            visible=is_booking,
            tooltip="选择时间",
        ),
    ], spacing=0)

    def get_price():
        if start_address is not None and selected_address is not None:
            if start_address == selected_address:
                return "装收货地址不应相同"

            start_location = app.user_manager.get_location_by_address(phone, start_address)
            selected_location = app.user_manager.get_location_by_address(phone, selected_address)
            unit_price = drone["price"]

            dist = calc_distance(start_location, selected_location)
            total = unit_price * dist / 100.0

            base = _calc_base_price(dist)
            return f"¥{(base + total):.2f}"

        return "¥待计算"

    price_text = ft.Text(get_price(), size=22, color=ft.Colors.RED_700, weight="bold")

    def on_submit(_):
        if not start_address:
            app.view_builder.show_snackbar("请选择装货地址", ft.Colors.RED_400)
            return

        if not selected_address:
            app.view_builder.show_snackbar("请选择收货地址", ft.Colors.RED_400)
            return

        if start_address == selected_address:
            app.view_builder.show_snackbar("装货地址不应和收货地址相同", ft.Colors.RED_400)
            return

        start_location = app.user_manager.get_location_by_address(phone, start_address)
        location = app.user_manager.get_location_by_address(phone, selected_address)

        if RouteManager.in_nfz(start_location.split(",")):
            app.view_builder.show_snackbar("装货地址在禁飞区内", ft.Colors.RED_400)
            return

        if RouteManager.in_nfz(location.split(",")):
            app.view_builder.show_snackbar("卸货地址在禁飞区内", ft.Colors.RED_400)
            return

        start = datetime.datetime.strptime(start_field.value, "%Y-%m-%d %H:%M")
        total = float(price_text.value[1:])

        order = {
            "id": datetime.datetime.now().astimezone().strftime("%Y%m%d%H%M%S"),
            "phone": phone,
            "drone_id": drone["id"],
            "drone_name": drone["name"],
            "start_address": start_address,
            "start_location": start_location,
            "address": selected_address,
            "location": location,
            "start_time": start.strftime("%Y-%m-%d %H:%M"),
            "total_price": total,
            "status": "待配送",
            "created_at": datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
            "is_booking": is_booking,
        }

        app.user_manager.add_order(phone, order)
        app.view_builder.show_snackbar("下单成功！", ft.Colors.GREEN_400)
        app.view_builder.goto("orders", selected_index=1)

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda: app.view_builder.goto("drone", drone_id=drone_id),
                ),
                ft.Text(
                    "预约租赁" if is_booking else "立即租赁",
                    size=20, weight="bold", expand=True,
                ),
            ]),
            padding=ft.Padding(15, 20, 15, 15),
            bgcolor=ft.Colors.WHITE,
        ),

        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(drone["images"][0], size=50),
                            width=80, height=80,
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=12,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column([
                            ft.Text(drone["name"], size=16, weight="bold"),
                            ft.Text(drone["specs"], size=13, color=ft.Colors.GREY_600),
                            ft.Text(f"¥{drone['price'] / 100.0}/千米", size=13, color=ft.Colors.RED_700),
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
                        ft.Text("地址信息", size=15, weight="bold"),
                        ft.Container(height=8),
                        start_address_display,
                        address_display
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                ),

                ft.Container(height=15),

                ft.Container(
                    content=ft.Column([
                        ft.Text("租赁设置", size=15, weight="bold"),
                        ft.Container(height=10),
                        start_row,
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    visible=is_booking
                ),

                ft.Container(height=15, visible=is_booking),

                ft.Container(
                    content=ft.Row([
                        ft.Text("预计费用", size=15, weight="bold", expand=True),
                        price_text,
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                ),

                ft.Container(height=25),

                ft.Button(
                    "确认下单",
                    width=float("inf"),
                    height=55,
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                    on_click=on_submit,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                ),

            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=20,
        ),
    ], expand=True)
