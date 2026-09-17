"""视图路由器：goto + show_snackbar + 启动入口。"""

import flet as ft
from views.pages import ROUTES


class ViewBuilder:
    """视图构建器 - 只负责路由分发"""

    def __init__(self, app):
        self.app = app

    def start(self):
        """启动入口（替代 App.main 中直接 page.add(build_home())）。"""
        return ROUTES["home"][0](self.app)

    def goto(self, name, **kwargs):
        """通用页面跳转"""
        if name not in ROUTES:
            print(f"未知路由: {name}")
            return

        self.app.page.controls.clear()
        nav_index = ROUTES[name][2]
        if nav_index is not None:
            self.app.page.navigation_bar.selected_index = nav_index

        builder, arg_map, _ = ROUTES[name]
        call_kwargs = {target: kwargs.get(src) for src, target in arg_map.items()}
        view = builder(self.app, **call_kwargs)

        self.app.page.add(view)
        self.app.page.update()

    def show_snackbar(self, text, color):
        snackbar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=color
        )
        self.app.page.overlay.append(snackbar)
        snackbar.open = True
        self.app.page.update()
