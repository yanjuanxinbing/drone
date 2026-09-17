"""常用地址页（含 build_address_list 与 show_address_dialog）。"""

import asyncio
import flet as ft

from views.components import (
    get_addr_citycode,
    get_current_location,
    search_tips,
)


async def show_address_dialog(app, phone, refresh, existing=None):
    """新增或编辑地址弹窗"""
    is_edit = existing is not None

    location = await get_current_location(app.AMAP_KEY)
    addr, citycode = await get_addr_citycode(app.AMAP_KEY, location)

    tips_column = ft.Column([], spacing=0)
    debounce_task = None
    selected_location_box = {"value": None}

    address_field = ft.TextField(
        label="搜索地址",
        hint_text="输入地址关键词...",
        value=existing["address"] if is_edit else "",
        border_radius=10,
        width=400,
        prefix_icon=ft.Icons.SEARCH,
    )

    async def on_input_change(_):
        tips_column.controls.clear()

        keyword = address_field.value
        if not keyword:
            app.page.update()
            return

        nonlocal debounce_task
        if debounce_task:
            debounce_task.cancel()

        async def delayed_search():
            await asyncio.sleep(0.5)
            tips = await search_tips(app.AMAP_KEY, keyword, location, citycode)

            for tip in tips[:6]:
                name = tip.get("name", "")
                district = tip.get("district", "")
                address = tip.get("address", "")
                tip_location = tip.get("location")
                full = f"{district}{name}" if not address else f"{district}{name} {address}"

                def on_tip_click(_,
                                 f=full, l=tip_location,
                                 tips_column=tips_column,
                                 addr_field=address_field,
                                 sel=selected_location_box):
                    addr_field.value = f
                    sel["value"] = l
                    tips_column.controls.clear()
                    app.page.update()

                tips_column.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(name, size=14, weight="bold"),
                            ft.Text(f"{district} {address}", size=12, color=ft.Colors.GREY_600),
                        ], spacing=2),
                        padding=ft.Padding(15, 10, 15, 10),
                        on_click=on_tip_click,
                        ink=True,
                        border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
                    )
                )

            app.page.update()

        debounce_task = app.page.run_task(delayed_search)

    address_field.on_change = on_input_change

    def on_confirm(_):
        address = address_field.value
        if not address:
            app.view_builder.show_snackbar("请选择或输入地址", ft.Colors.RED_400)
            return

        if is_edit:
            app.user_manager.update_address(phone, existing["id"], address, selected_location_box["value"])
            app.view_builder.show_snackbar("地址已更新", ft.Colors.GREEN_400)
        else:
            app.user_manager.add_address(phone, address, selected_location_box["value"])
            app.view_builder.show_snackbar("地址已添加", ft.Colors.GREEN_400)

        dialog.open = False
        app.page.update()
        refresh()

    def on_cancel(_):
        dialog.open = False
        app.page.update()

    location_hint = ft.Row([
        ft.Icon(ft.Icons.MY_LOCATION, size=14, color=ft.Colors.BLUE),
        ft.Text(
            f"已定位到：{addr}" if addr else "定位失败，请手动输入",
            size=12,
            color=ft.Colors.BLUE if addr else ft.Colors.GREY_500,
        ),
    ], spacing=4)

    dialog = ft.AlertDialog(
        title=ft.Text("编辑地址" if is_edit else "新增地址", weight="bold"),
        content=ft.Container(
            content=ft.Column([
                location_hint,
                ft.Container(height=8),
                address_field,
                ft.Container(
                    content=tips_column,
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                    visible=True,
                ),
            ], spacing=4),
            width=400,
            padding=ft.Padding(0, 10, 0, 0),
        ),
        actions=[
            ft.TextButton("取消", on_click=on_cancel),
            ft.Button(
                "确认",
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                on_click=on_confirm,
            ),
        ],
    )
    app.page.overlay.append(dialog)
    dialog.open = True
    app.page.update()


def build_address_list(app, phone, refresh, drone_id=None, is_booking=False,
                       selected_address=None, start_address=None, is_start=False):
    addresses = app.user_manager.get_addresses(phone)

    def on_delete(addr_id):
        app.user_manager.delete_address(phone, addr_id)
        refresh()

    def on_item_click(addr):
        if not drone_id:
            return
        app.view_builder.goto(
            "order",
            drone_id=drone_id, is_booking=is_booking,
            selected_address=addr if not is_start else selected_address,
            start_address=addr if is_start else start_address,
        )

    def make_row(index, addr):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLUE, size=20),
                ft.Text(addr["address"], size=14, expand=True),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    icon_color=ft.Colors.BLUE,
                    on_click=lambda _, a=addr: app.page.run_task(show_address_dialog, app, phone, refresh, a),
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_400,
                    on_click=lambda _, id=addr["id"]: on_delete(id),
                ),
                ft.TextButton(
                    "设为默认" if index else "默认地址",
                    on_click=lambda _, id=addr["id"]: (
                        app.user_manager.set_default_address(phone, id),
                        refresh()
                    ) if index else None,
                    style=ft.ButtonStyle(color=ft.Colors.BLUE),
                )
            ]),
            padding=ft.Padding(20, 15, 10, 15),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
            on_click=lambda _, a=addr["address"]: on_item_click(a),
        )

    return ft.Column([make_row(i, a) for i, a in enumerate(addresses)], spacing=12)


def build_addresses(app, **kwargs):
    """常用地址页面"""
    phone = app.config.get("last_user")

    list_container = ft.Container(expand=True)

    def refresh():
        list_container.content = build_address_list(app, phone, refresh)
        app.page.update()

    refresh()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda: app.view_builder.goto("settings")),
                ft.Text("常用地址", size=20, weight="bold", expand=True),
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
