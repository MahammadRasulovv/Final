import flet as ft
import httpx

from window2 import window2

APPBAR_BG = "#F9A825"
PAGE_BG   = "#FEF5DB"
HEADER_BG = "#373747"
BTN_COLOR = "#FFFFFF"
TEXT_DK   = "#212121"
TEXT_SEC  = "#757575"
ROW_ODD   = "#F5F5F5"
ROW_EVEN  = "#FFFFFF"

BASE_URL = "http://127.0.0.1:8000"

COL_STYLE = ft.TextStyle(color=BTN_COLOR, weight=ft.FontWeight.BOLD, size=13)
DRV_COLS  = ["DriverID", "FullName", "Phone", "VehicleType"]


def api_get_drivers():
    try:
        r = httpx.get(f"{BASE_URL}/drivers", timeout=5)
        r.raise_for_status()
        return r.json(), None
    except httpx.ConnectError:
        return None, "Server bağlantisi yoxdur. api.py-ni işlət."
    except Exception as ex:
        return None, str(ex)


def api_get_vehicle_types():
    try:
        r = httpx.get(f"{BASE_URL}/vehicle-types", timeout=5)
        r.raise_for_status()
        return r.json(), None
    except Exception:
        return None, None


# WINDOW 1

def window1(page: ft.Page, go_to_add):

    bs_title    = ft.Text("", color=BTN_COLOR, weight=ft.FontWeight.BOLD, size=14)
    bs_subtitle = ft.Text("", color=TEXT_DK, size=13)
    bs_hint     = ft.Text("Tap drag handle to expand",
                          color=TEXT_SEC, italic=True, size=11)

    bottom_sheet = ft.BottomSheet(
        dismissible=True,
        show_drag_handle=True,
        bgcolor="white",
        content=ft.Container(
            padding=ft.Padding(left=20, top=8, right=20, bottom=24),
            content=ft.Column(tight=True, controls=[
                ft.Container(height=4),
                bs_title,
                ft.Container(height=4),
                bs_subtitle,
                ft.Container(height=6),
                bs_hint,
            ]),
        ),
        on_dismiss=lambda _: None,
    )

    def open_bs(row_data: dict):
        bs_title.value    = "DRIVER INFO"
        bs_subtitle.value = (f"{row_data['FullName']}  ·  {row_data['Phone']}  ·  "
                             f"{row_data['VehicleType']}")
        page.show_dialog(bottom_sheet)

    def build_driver_table(rows):
        data_rows = []
        for i, rd in enumerate(rows):
            data_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(rd["DriverID"]),    color=TEXT_DK, size=13)),
                        ft.DataCell(ft.Text(rd["FullName"],         color=TEXT_DK, size=13)),
                        ft.DataCell(ft.Text(rd["Phone"],            color=TEXT_DK, size=13)),
                        ft.DataCell(ft.Text(rd["VehicleType"],      color=TEXT_DK, size=13)),
                    ],
                    color=ROW_ODD if i % 2 == 0 else ROW_EVEN,
                    on_select_change=lambda _, d=rd: open_bs(d),
                )
            )
        return ft.DataTable(
            expand=True,
            width=float("inf"),
            bgcolor=ft.Colors.TRANSPARENT,
            border=ft.Border.all(0),
            heading_row_color=HEADER_BG,
            heading_row_height=40,
            data_row_min_height=36,
            data_row_max_height=48,
            column_spacing=16,
            columns=[ft.DataColumn(ft.Text(c, style=COL_STYLE)) for c in DRV_COLS],
            rows=data_rows,
        )

    table_col  = ft.Ref[ft.Column]()
    err_text   = ft.Ref[ft.Text]()
    body       = ft.Ref[ft.Container]()
    vt_text    = ft.Ref[ft.Text]()

    def refresh_drivers():
        data, err = api_get_drivers()
        if err:
            if err_text.current:
                err_text.current.value   = err
                err_text.current.visible = True
        else:
            if err_text.current:
                err_text.current.visible = False
            if table_col.current:
                table_col.current.controls = [build_driver_table(data or [])]
        vd, _ = api_get_vehicle_types()
        if vd and vt_text.current:
            vt_text.current.value = f"Vehicle types : {vd['count']}  ({', '.join(vd['types'])})"
        page.update()

    def drivers_view():
        init_data, init_err = api_get_drivers()
        vd, _ = api_get_vehicle_types()
        vt_label = f"Vehicle types : {vd['count']}  ({', '.join(vd['types'])})" if vd else "Vehicle types : 0"
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
            controls=[
                ft.Text(
                    ref=err_text,
                    value=init_err or "",
                    color="#C62828", size=12,
                    visible=bool(init_err),
                ),
                ft.Container(
                    border=ft.Border.all(1, HEADER_BG),
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Row(expand=True, controls=[
                        ft.Column(
                            ref=table_col,
                            expand=True,
                            controls=[build_driver_table(init_data or [])],
                        ),
                    ]),
                ),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border=ft.Border.all(1, "#DBDBDB"),
                    border_radius=8,
                    bgcolor=ROW_ODD,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Available Vehicle Types", color=TEXT_SEC, size=11),
                            ft.Text(
                                ref=vt_text,
                                value=vt_label,
                                color=TEXT_DK,
                                size=13,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                ),
            ],
        )

    def placeholder_view(icon, title, subtitle):
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Container(height=40),
                ft.Icon(icon, size=56, color=TEXT_SEC),
                ft.Text(title,    size=18, color=TEXT_DK),
                ft.Text(subtitle, color=TEXT_SEC, size=13,
                        text_align=ft.TextAlign.CENTER),
            ],
        )

    views = [
        drivers_view,
        lambda: placeholder_view(ft.Icons.DIRECTIONS_CAR, "My Trips",
                                 "Sürüşləriniz burada görünəcək."),
        lambda: placeholder_view(ft.Icons.PERSON, "Profile",
                                 "Profil məlumatlariniz burada olacaq."),
    ]

    def on_nav_change(e):
        idx = e.control.selected_index
        body.current.content = views[idx]()
        if idx == 0:
            refresh_drivers()
        else:
            page.update()

    content = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                bgcolor=APPBAR_BG,
                padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                shadow=ft.BoxShadow(blur_radius=4, color="#22000000", offset=ft.Offset(0, 2)),
                content=ft.Row([
                    ft.Text("TaxiGo", color="white", size=18,
                            weight=ft.FontWeight.BOLD, expand=True),
                    ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_color=BTN_COLOR,
                                  on_click=lambda _: go_to_add(),
                                  tooltip="Manage Drivers"),
                ]),
            ),

            ft.Container(
                ref=body,
                expand=True,
                padding=ft.Padding.all(14),
                bgcolor=PAGE_BG,
                content=drivers_view(),
            ),

            ft.NavigationBar(
                selected_index=0,
                bgcolor="white",
                indicator_color=ft.Colors.GREY_200,
                on_change=on_nav_change,
                destinations=[
                    ft.NavigationBarDestination(
                        icon=ft.Icons.DIRECTIONS_CAR_OUTLINED,
                        selected_icon=ft.Icons.DIRECTIONS_CAR,
                        label="Book Ride",
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                        selected_icon=ft.Icons.RECEIPT_LONG,
                        label="My Trips",
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.PERSON_OUTLINE,
                        selected_icon=ft.Icons.PERSON,
                        label="Profile",
                    ),
                ],
            ),
        ],
    )

    return content, refresh_drivers


# MAIN

def main(page: ft.Page):
    page.title   = "RideApp"
    page.bgcolor = PAGE_BG
    page.padding = 0
    page.window.width     = 420
    page.window.height    = 780
    page.window.resizable = True

    root = ft.Ref[ft.Stack]()

    def go_to_add():
        root.current.controls[1].visible = True
        root.current.controls[0].visible = False
        page.update()

    def go_back():
        root.current.controls[0].visible = True
        root.current.controls[1].visible = False
        refresh_w1()
        page.update()

    w1, refresh_w1 = window1(page, go_to_add)
    w2 = window2(page, go_back)

    page.add(
        ft.Stack(
            ref=root,
            expand=True,
            controls=[
                ft.Container(content=w1, expand=True, visible=True),
                ft.Container(content=w2, expand=True, visible=False),
            ],
        )
    )


ft.run(main)
