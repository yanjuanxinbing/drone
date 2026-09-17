"""帮助中心页。"""

import flet as ft

# 帮助中心 FAQ 数据（保持原状）
FAQS = [
    {
        "question": "如何租赁无人机？",
        "answer": "在首页选择心仪的无人机型号，点击立即租赁，填写收货地址和租赁时长，完成支付后无人机将从就近机库配送到您指定的地址。"
    },
    {
        "question": "租赁费用如何计算？",
        "answer": "租赁费用按天计算，不同机型价格不同。订单确认后费用将一次性扣除，超时使用将按小时补收费用。"
    },
    {
        "question": "如何归还无人机？",
        "answer": "租赁到期前，您可以在订单页面申请上门回收，无人机将自动飞回就近机库。请确保设备电量不低于20%。"
    },
    {
        "question": "设备损坏怎么办？",
        "answer": "如因正常使用造成损坏，请在订单页面提交报修申请，我们将安排检测。人为损坏将根据损坏程度收取相应赔偿费用。"
    },
    {
        "question": "哪些区域禁止飞行？",
        "answer": "机场净空区、军事禁区、政府机关上空等敏感区域禁止飞行。飞行高度一般不超过120米。请在飞行前查阅当地法规，违规飞行责任自负。"
    },
    {
        "question": "如何申请退款？",
        "answer": "租赁开始前可申请全额退款。租赁开始后如遇设备故障，可申请部分退款。请在订单页面提交退款申请，客服将在1-3个工作日内处理。"
    },
    {
        "question": "忘记密码怎么办？",
        "answer": "在登录页面点击忘记密码，通过绑定手机号验证身份后即可重置密码。"
    }
]


def build_help_center(app, **kwargs):
    """帮助中心页面"""

    def build_faq_item(faq):
        expanded = {"value": False}
        answer_container = ft.Container(
            content=ft.Text(faq["answer"], size=13, color=ft.Colors.GREY_700),
            padding=ft.Padding(15, 0, 15, 15),
            visible=False,
        )
        chevron = ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400, size=20)

        def on_toggle(_):
            expanded["value"] = not expanded["value"]
            answer_container.visible = expanded["value"]
            chevron.name = ft.Icons.EXPAND_LESS if expanded["value"] else ft.Icons.CHEVRON_RIGHT
            app.page.update()

        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.BLUE, size=18),
                        ft.Text(faq["question"], size=14, weight="bold", expand=True),
                        chevron,
                    ], spacing=10),
                    padding=ft.Padding(15, 12, 15, 12),
                    on_click=on_toggle,
                    ink=True,
                ),
                answer_container,
            ], spacing=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
        )

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: app.view_builder.goto("settings")),
                ft.Text("帮助中心", size=20, weight="bold", expand=True),
            ]),
            padding=ft.Padding(15, 20, 15, 15),
            bgcolor=ft.Colors.WHITE,
        ),

        ft.Container(
            content=ft.Column([

                ft.Container(
                    content=ft.Text("常见问题", size=16, weight="bold", color=ft.Colors.BLUE_700),
                    padding=ft.Padding.only(left=5, top=10, bottom=10),
                ),
                ft.Column([
                    build_faq_item(faq) for faq in FAQS
                ], spacing=10),

                ft.Container(
                    content=ft.Text("联系客服", size=16, weight="bold", color=ft.Colors.BLUE_700),
                    padding=ft.Padding.only(left=5, top=25, bottom=10),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PHONE_OUTLINED, color=ft.Colors.BLUE, size=20),
                            ft.Text("客服电话", size=14, color=ft.Colors.GREY_700, width=80),
                            ft.Text("400-888-9999", size=14, weight="bold"),
                        ], spacing=10),
                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                        ft.Row([
                            ft.Icon(ft.Icons.EMAIL_OUTLINED, color=ft.Colors.BLUE, size=20),
                            ft.Text("客服邮箱", size=14, color=ft.Colors.GREY_700, width=80),
                            ft.Text("support@dronegoo.com", size=14, weight="bold"),
                        ], spacing=10),
                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                        ft.Row([
                            ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.BLUE, size=20),
                            ft.Text("服务时间", size=14, color=ft.Colors.GREY_700, width=80),
                            ft.Text("每日 09:00 - 21:00", size=14, weight="bold"),
                        ], spacing=10),
                    ], spacing=12),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK_12),
                ),

                ft.Container(height=20),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=ft.Padding.symmetric(horizontal=20),
        ),
    ], expand=True)
