"""所有页面模块的统一入口 + 路由表。

ROUTES[name] = (builder_fn, {external_kw: builder_kw}, nav_index_or_None)
"""

from . import (
    home, search, orders, order_detail, order,
    drone_detail, play_rent,
    profile, settings, personal_info, change_password, change_phone,
    login, register, forget,
    addresses, address_picker,
    privacy_settings, help_center,
    agreement,
)

ROUTES = {
    "home":             (home.build_home,                {}, 0),
    "orders":           (orders.build_orders,            {"selected_index": "selected_index"}, 1),
    "order_detail":     (order_detail.build_order_detail, {"order_id": "order_id"}, None),
    "profile":          (profile.build_profile,          {}, 2),
    "login":            (login.build_login,              {}, None),
    "register":         (register.build_register,        {}, None),
    "forget":           (forget.build_forget,            {}, None),
    "drone":            (drone_detail.build_drone_detail, {"drone_id": "drone_id"}, None),
    "order":            (order.build_order,
                         {"drone_id": "drone_id",
                          "is_booking": "is_booking",
                          "selected_address": "selected_address",
                          "start_address": "start_address"}, None),
    "search":           (search.build_search,            {"keyword": "keyword"}, None),
    "settings":         (settings.build_settings,        {}, None),
    "personal_info":    (personal_info.build_personal_info, {}, None),
    "change_password":  (change_password.build_change_password, {}, None),
    "change_phone":     (change_phone.build_change_phone, {}, None),
    "addresses":        (addresses.build_addresses,      {}, None),
    "privacy_settings": (privacy_settings.build_privacy_settings, {}, None),
    "help_center":      (help_center.build_help_center,  {}, None),
    "address_picker":   (address_picker.build_address_picker,
                         {"drone_id": "drone_id",
                          "is_booking": "is_booking",
                          "selected_address": "selected_address",
                          "start_address": "start_address",
                          "is_start": "is_start"}, None),
    "play_rent":        (play_rent.build_play_rent,      {}, None),
}
