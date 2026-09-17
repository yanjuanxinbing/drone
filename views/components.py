"""共享 UI 构件、常量、工具与弹窗。"""

import aiohttp
import flet as ft
import flet_geolocator as ftg
from file import FileReader
from geopy.distance import geodesic
from routemanager import RouteManager

# ─── 常量 ────────────────────────────────────────────────────────────────
STATUS_COLOR = {
    "待配送": ft.Colors.ORANGE,
    "租赁中": ft.Colors.BLUE,
    "已完成": ft.Colors.GREEN,
    "已取消": ft.Colors.GREY_500,
}

STATUS_ICON = {
    "待配送": ft.Icons.LOCAL_SHIPPING_OUTLINED,
    "租赁中": ft.Icons.FLIGHT,
    "已完成": ft.Icons.CHECK_CIRCLE_OUTLINE,
    "已取消": ft.Icons.CANCEL_OUTLINED,
}

LEVEL_COLORS = {
    2: ft.Colors.RED_400,
    3: ft.Colors.ORANGE_400,
    7: ft.Colors.YELLOW_600,
    8: ft.Colors.BLUE_400,
}

ORDER_STATUSES = ["租赁中", "待配送", "已完成", "已取消"]

PHONE_PATTERN = r"^1[3-9]\d{9}$"


# ─── 异步地图/定位工具（纯函数，参数注入 AMAP_KEY） ────────────────────
async def get_current_location(amap_key: str) -> str:
    gl = ftg.Geolocator()
    pos = await gl.get_current_position()
    lat, lng = pos.latitude, pos.longitude

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://restapi.amap.com/v3/assistant/coordinate/convert",
            params={
                "key": amap_key,
                "locations": f"{lng:.6f},{lat:.6f}",
                "coordsys": "gps"
            }
        ) as resp:
            data = await resp.json()
            pos = data.get("locations")
            lng_str, lat_str = pos.split(",")
            lng = f"{float(lng_str):.6f}"
            lat = f"{float(lat_str):.6f}"
            return f"{lng},{lat}"


async def get_addr_citycode(amap_key: str, location: str) -> tuple[str, str]:
    """定位获取当前位置和 citycode"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://restapi.amap.com/v3/geocode/regeo",
                params={"key": amap_key, "location": location}
            ) as resp:
                data = await resp.json()
                if data.get("status") == "1":
                    return (
                        data.get("regeocode").get("formatted_address"),
                        data.get("regeocode").get("addressComponent").get("citycode")
                    )
    except Exception as e:
        print(f"定位失败: {e}")


async def search_tips(amap_key: str, keyword: str, location: str, citycode: str) -> list:
    """输入提示补全"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://restapi.amap.com/v3/assistant/inputtips",
                params={
                    "key": amap_key,
                    "keywords": keyword,
                    "location": location,
                    "city": citycode
                }
            ) as resp:
                data = await resp.json()
                if data.get("status") == "1":
                    return data.get("tips", [])
                return []
    except Exception as e:
        print(f"输入提示失败: {e}")
        return []


def calc_distance(loc1: str, loc2: str) -> float:
    """计算两点直线距离（km），坐标格式 'lng,lat'"""
    lng1, lat1 = map(float, loc1.split(","))
    lng2, lat2 = map(float, loc2.split(","))
    return geodesic((lat1, lng1), (lat2, lng2)).km


# ─── 通用弹窗 ────────────────────────────────────────────────────────────
def close_dialog(dialog, page):
    """统一关闭 AlertDialog。"""
    dialog.open = False
    page.update()


def show_document_dialog(app, title: str, content: str):
    """统一协议文档弹窗（统一了三处重复的 show_document）。"""
    page = app.page

    dialog = ft.AlertDialog(
        title=ft.Text(title, weight="bold"),
        content=ft.Container(
            content=ft.Text(content, selectable=True),
            width=500,
            height=400,
            padding=20,
        ),
        actions=[ft.TextButton("关闭", on_click=lambda _: close_dialog(dialog, page))],
        scrollable=True,
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def show_cancel_order_dialog(app, on_confirm):
    """统一取消订单 AlertDialog。"""
    page = app.page

    def confirm_cancel():
        on_confirm()
        close_dialog(dialog, page)

    dialog = ft.AlertDialog(
        title=ft.Text("取消订单", weight="bold"),
        content=ft.Text("确认取消该订单？此操作不可撤销。"),
        actions=[
            ft.TextButton("返回", on_click=lambda _: close_dialog(dialog, page)),
            ft.Button(
                "确认取消",
                bgcolor=ft.Colors.RED_400,
                color=ft.Colors.WHITE,
                on_click=confirm_cancel,
            ),
        ],
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


# ─── 通用 UI 构件 ────────────────────────────────────────────────────────
def build_card(app, drone_id, name, price, tag, specs):
    """无人机卡片（home / search 共享）。"""
    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text("🚁", size=50),
                alignment=ft.Alignment.CENTER,
                height=100,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=12,
            ),
            ft.Text(name, weight="bold", size=16),
            ft.Text(specs, size=12, color=ft.Colors.GREY_600, max_lines=1),
            ft.Row([
                ft.Text(f"¥ {price}", color=ft.Colors.BLUE_700, weight="bold", size=16),
                ft.Container(
                    content=ft.Text(tag, size=10, color="white"),
                    bgcolor=ft.Colors.BLUE,
                    padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                    border_radius=4,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]),
        padding=12,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK_12),
        on_click=lambda: app.view_builder.goto("drone", drone_id=drone_id)
    )


def build_menu_item(app, icon, label):
    """profile 顶栏菜单项。"""
    def on_menu_click():
        if label == "我的订单":
            app.view_builder.goto("orders")

    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, size=28, color=ft.Colors.BLUE_700),
            ft.Text(label, size=11, text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        on_click=on_menu_click,
        padding=10,
        ink=True,
    )


def build_list_item(app, icon, title, trailing_text=None):
    """profile 设置列表项（与原 _list_item 等价）。"""
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=22, color=ft.Colors.GREY_700),
            ft.Text(title, size=15, expand=True),
            ft.Text(
                trailing_text, size=13, color=ft.Colors.GREY_500,
            ) if trailing_text else ft.Container(),
            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color=ft.Colors.GREY_400),
        ], spacing=15),
        padding=ft.Padding.symmetric(horizontal=20, vertical=15),
        ink=True,
    )


def make_pin(icon, bg_color):
    """生成一个带针脚的地图标记。"""
    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Icon(icon, color=ft.Colors.WHITE, size=16),
                width=32, height=32,
                bgcolor=bg_color,
                border_radius=16,
                alignment=ft.Alignment.CENTER,
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.3, bg_color), spread_radius=2),
            ),
            ft.Container(width=2, height=8, bgcolor=bg_color),
            ft.Container(width=6, height=6, bgcolor=ft.Colors.with_opacity(0.4, bg_color), border_radius=3),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
        alignment=ft.Alignment.CENTER,
    )
