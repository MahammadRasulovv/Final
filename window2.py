import flet as ft
import httpx
import threading
import time

APPBAR_BG = "#F9A825"
PAGE_BG   = "#FEF5DB"
HEADER_BG = "#373747"
BTN_COLOR = "#F9A825"
TF_BORDER = "#DBDBDB"
TEXT_DK   = "#212121"
TEXT_SEC  = "#757575"
TF_COLOR  = "#F9A825"
ROW_ODD   = "#F5F5F5"
ROW_EVEN  = "#FFFFFF"
SUCCESS   = "#2E7D32"
ERROR_C   = "#C62828"

BASE_URL = "http://127.0.0.1:8000"

COL_STYLE = ft.TextStyle(color="white", weight=ft.FontWeight.BOLD, size=13)


def make_tf(label):
    return ft.TextField(
        label=label,
        expand=True,
        border_color=TF_BORDER,
        focused_border_color=BTN_COLOR,
        text_size=13,
        color=TEXT_DK,
        cursor_color=BTN_COLOR,
        label_style=ft.TextStyle(color=TEXT_SEC),
    )


def api_get(endpoint):
    try:
        r = httpx.get(f"{BASE_URL}/{endpoint}", timeout=5)
        r.raise_for_status()
        return r.json(), None
    except httpx.ConnectError:
        return None, "Server bağlantisi yoxdur."
    except Exception as ex:
        return None, str(ex)


def api_post(endpoint, payload):
    try:
        r = httpx.post(f"{BASE_URL}/{endpoint}", json=payload, timeout=5)
        if r.status_code == 400:
            return None, r.json().get("detail", "Xəta")
        r.raise_for_status()
        return r.json(), None
    except httpx.ConnectError:
        return None, "Server bağlantisi yoxdur."
    except Exception as ex:
        return None, str(ex)


def api_delete(endpoint, record_id):
    try:
        r = httpx.delete(f"{BASE_URL}/{endpoint}/{record_id}", timeout=5)
        if r.status_code == 404:
            return None, r.json().get("detail", "Tapilmadi")
        r.raise_for_status()
        return r.json(), None
    except httpx.ConnectError:
        return None, "Server bağlantisi yoxdur."
    except Exception as ex:
        return None, str(ex)


def build_table(rows, columns):
    data_rows = []
    for i, row in enumerate(rows):
        data_rows.append(
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(row.get(c, "")), color=TEXT_DK, size=13))
                       for c in columns],
                color=ROW_ODD if i % 2 == 0 else ROW_EVEN,
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
        columns=[ft.DataColumn(ft.Text(c, style=COL_STYLE)) for c in columns],
        rows=data_rows,
    )


def window2(page: ft.Page, go_back):

    banner = ft.Container(
        visible=False,
        border_radius=8,
        padding=ft.Padding.symmetric(vertical=12, horizontal=16),
        content=ft.Row(spacing=8, controls=[
            ft.Icon(ft.Icons.CHECK_CIRCLE, color="white", size=18),
            ft.Text("", color="white", weight=ft.FontWeight.BOLD, size=13),
        ]),
    )

    def show_banner(msg, is_error=False):
        banner.bgcolor = ERROR_C if is_error else SUCCESS
        banner.content.controls[0].name = ft.Icons.ERROR if is_error else ft.Icons.CHECK_CIRCLE
        banner.content.controls[1].value = msg
        banner.visible = True
        page.update()
        def hide():
            time.sleep(3)
            banner.visible = False
            page.update()
        threading.Thread(target=hide, daemon=True).start()

    # ── Driver tab ───────────────────────────────────────────────
    drv_id   = make_tf("DriverID")
    drv_name = make_tf("FullName")
    drv_ph   = make_tf("Phone")
    drv_veh  = make_tf("VehicleType")
    drv_tbl  = ft.Ref[ft.Column]()

    DRV_COLS = ["DriverID", "FullName", "Phone", "VehicleType"]

    def drv_refresh():
        data, err = api_get("drivers")
        if err:
            show_banner(err, is_error=True); return
        drv_tbl.current.controls = [build_table(data, DRV_COLS)]
        page.update()

    def drv_add(e):
        drv_id.error_text = drv_name.error_text = None
        if not drv_id.value or not drv_name.value:
            drv_id.error_text   = "Tələb olunur" if not drv_id.value   else None
            drv_name.error_text = "Tələb olunur" if not drv_name.value else None
            page.update(); return
        try:
            did = int(drv_id.value)
        except ValueError:
            drv_id.error_text = "Rəqəm olmalidir"; page.update(); return
        _, err = api_post("drivers", {"DriverID": did, "FullName": drv_name.value,
                                       "Phone": drv_ph.value, "VehicleType": drv_veh.value})
        if err:
            show_banner(err, is_error=True); return
        for f in [drv_id, drv_name, drv_ph, drv_veh]:
            f.value = f.error_text = None
        drv_refresh()
        show_banner("Driver əlavə edildi!")

    def drv_del(e):
        drv_id.error_text = None
        if not drv_id.value:
            drv_id.error_text = "ID daxil et"; page.update(); return
        try:
            did = int(drv_id.value)
        except ValueError:
            drv_id.error_text = "Rəqəm olmalidir"; page.update(); return
        _, err = api_delete("drivers", did)
        if err:
            show_banner(err, is_error=True); return
        drv_id.value = drv_id.error_text = None
        drv_refresh()
        show_banner("Driver silindi!")

    drv_init, _ = api_get("drivers")

    driver_view = ft.Container(
        expand=True,
        padding=ft.Padding.all(14),
        bgcolor=PAGE_BG,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            controls=[
                ft.Text("GET /drivers", color=BTN_COLOR, weight=ft.FontWeight.BOLD, size=13),
                ft.Container(
                    border=ft.Border.all(1, HEADER_BG), border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Row(expand=True, controls=[
                        ft.Column(ref=drv_tbl, expand=True,
                                  controls=[build_table(drv_init or [], DRV_COLS)]),
                    ]),
                ),
                ft.Divider(color=ft.Colors.TRANSPARENT, height=4),
                ft.Text("POST /drivers", color=BTN_COLOR, weight=ft.FontWeight.BOLD, size=13),
                ft.Row([drv_id, drv_name], spacing=10),
                ft.Row([drv_ph, drv_veh],  spacing=10),
                ft.Row(spacing=10, controls=[
                    ft.ElevatedButton("POST Add", expand=True, bgcolor=BTN_COLOR, color="white",
                        height=46, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=drv_add),
                    ft.ElevatedButton("DELETE", expand=True, bgcolor="#B71C1C", color="white",
                        height=46, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=drv_del),
                ]),
                banner,
            ],
        ),
    )

    #  Customers tab
    cst_id   = make_tf("CustomerID")
    cst_name = make_tf("FullName")
    cst_ph   = make_tf("Phone")
    cst_mail = make_tf("Email")
    cst_tbl  = ft.Ref[ft.Column]()

    CST_COLS = ["CustomerID", "FullName", "Phone", "Email"]

    def cst_refresh():
        data, err = api_get("customers")
        if err:
            show_banner(err, is_error=True); return
        cst_tbl.current.controls = [build_table(data, CST_COLS)]
        page.update()

    def cst_add(e):
        cst_id.error_text = cst_name.error_text = None
        if not cst_id.value or not cst_name.value:
            cst_id.error_text   = "Tələb olunur" if not cst_id.value   else None
            cst_name.error_text = "Tələb olunur" if not cst_name.value else None
            page.update(); return
        try:
            cid = int(cst_id.value)
        except ValueError:
            cst_id.error_text = "Rəqəm olmalidir"; page.update(); return
        _, err = api_post("customers", {"CustomerID": cid, "FullName": cst_name.value,
                                         "Phone": cst_ph.value, "Email": cst_mail.value})
        if err:
            show_banner(err, is_error=True); return
        for f in [cst_id, cst_name, cst_ph, cst_mail]:
            f.value = f.error_text = None
        cst_refresh()
        show_banner("Customer əlavə edildi!")

    def cst_del(e):
        cst_id.error_text = None
        if not cst_id.value:
            cst_id.error_text = "ID daxil et"; page.update(); return
        try:
            cid = int(cst_id.value)
        except ValueError:
            cst_id.error_text = "Rəqəm olmalidir"; page.update(); return
        _, err = api_delete("customers", cid)
        if err:
            show_banner(err, is_error=True); return
        cst_id.value = cst_id.error_text = None
        cst_refresh()
        show_banner("Customer silindi!")

    cst_init, _ = api_get("customers")

    customer_view = ft.Container(
        expand=True,
        padding=ft.Padding.all(14),
        bgcolor=PAGE_BG,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            controls=[
                ft.Text("GET /customers", color=BTN_COLOR, weight=ft.FontWeight.BOLD, size=13),
                ft.Container(
                    border=ft.Border.all(1, HEADER_BG), border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Row(expand=True, controls=[
                        ft.Column(ref=cst_tbl, expand=True,
                                  controls=[build_table(cst_init or [], CST_COLS)]),
                    ]),
                ),
                ft.Divider(color=ft.Colors.TRANSPARENT, height=4),
                ft.Text("POST /customers", color=BTN_COLOR, weight=ft.FontWeight.BOLD, size=13),
                ft.Row([cst_id, cst_name], spacing=10),
                ft.Row([cst_ph, cst_mail],  spacing=10),
                ft.Row(spacing=10, controls=[
                    ft.ElevatedButton("POST Add", expand=True, bgcolor=BTN_COLOR, color="white",
                        height=46, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=cst_add),
                    ft.ElevatedButton("DELETE", expand=True, bgcolor="#B71C1C", color="white",
                        height=46, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=cst_del),
                ]),
            ],
        ),
    )

    # ── Rides tab ────────────────────────────────────────────────
    rd_id   = make_tf("RideID")
    rd_drv  = make_tf("DriverID")
    rd_cst  = make_tf("CustomerID")
    rd_pick = make_tf("PickUP")
    rd_fare = make_tf("Fare")
    rd_tbl  = ft.Ref[ft.Column]()

    RD_COLS = ["RideID", "DriverID", "CustomerID", "PickUP", "Fare"]

    def rd_refresh():
        data, err = api_get("rides")
        if err:
            show_banner(err, is_error=True); return
        rd_tbl.current.controls = [build_table(data, RD_COLS)]
        page.update()

    def rd_add(e):
        rd_id.error_text = None
        if not rd_id.value:
            rd_id.error_text = "Tələb olunur"; page.update(); return
        try:
            rid  = int(rd_id.value)
            did  = int(rd_drv.value)  if rd_drv.value  else 0
            cid  = int(rd_cst.value)  if rd_cst.value  else 0
            fare = float(rd_fare.value) if rd_fare.value else 0.0
        except ValueError:
            rd_id.error_text = "Rəqəm yoxlanişi uğursuz"; page.update(); return
        _, err = api_post("rides", {"RideID": rid, "DriverID": did, "CustomerID": cid,
                                     "PickUP": rd_pick.value or "", "Fare": fare})
        if err:
            show_banner(err, is_error=True); return
        for f in [rd_id, rd_drv, rd_cst, rd_pick, rd_fare]:
            f.value = f.error_text = None
        rd_refresh()
        show_banner("Ride əlavə edildi!")

    def rd_del(e):
        rd_id.error_text = None
        if not rd_id.value:
            rd_id.error_text = "ID daxil et"; page.update(); return
        try:
            rid = int(rd_id.value)
        except ValueError:
            rd_id.error_text = "Rəqəm olmalıdır"; page.update(); return
        _, err = api_delete("rides", rid)
        if err:
            show_banner(err, is_error=True); return
        rd_id.value = rd_id.error_text = None
        rd_refresh()
        show_banner("Ride silindi!")

    rd_init, _ = api_get("rides")

    ride_view = ft.Container(
        expand=True,
        padding=ft.Padding.all(14),
        bgcolor=PAGE_BG,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            controls=[
                ft.Text("GET /rides", color=BTN_COLOR, weight=ft.FontWeight.BOLD, size=13),
                ft.Container(
                    border=ft.Border.all(1, HEADER_BG), border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Row(expand=True, controls=[
                        ft.Column(ref=rd_tbl, expand=True,
                                  controls=[build_table(rd_init or [], RD_COLS)]),
                    ]),
                ),
                ft.Divider(color=ft.Colors.TRANSPARENT, height=4),
                ft.Text("POST /rides", color=BTN_COLOR, weight=ft.FontWeight.BOLD, size=13),
                ft.Row([rd_id, rd_drv],   spacing=10),
                ft.Row([rd_cst, rd_pick], spacing=10),
                rd_fare,
                ft.Row(spacing=10, controls=[
                    ft.ElevatedButton("POST Add", expand=True, bgcolor=BTN_COLOR, color="white",
                        height=46, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=rd_add),
                    ft.ElevatedButton("DELETE", expand=True, bgcolor="#B71C1C", color="white",
                        height=46, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=rd_del),
                ]),
            ],
        ),
    )

    #   Layout
    content = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                bgcolor=APPBAR_BG,
                padding=ft.Padding.symmetric(horizontal=8, vertical=10),
                shadow=ft.BoxShadow(blur_radius=4, color="#22000000", offset=ft.Offset(0, 2)),
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=TEXT_DK,
                                  on_click=lambda _: go_back()),
                    ft.Text("Add Driver", color=TEXT_DK, size=18,
                            weight=ft.FontWeight.BOLD, expand=True,
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(width=48),
                ]),
            ),

            ft.Tabs(
                length=3,
                expand=True,
                content=ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        ft.TabBar(tabs=[
                            ft.Tab(label="Drivers"),
                            ft.Tab(label="Customers"),
                            ft.Tab(label="Rides"),
                        ]),
                        ft.TabBarView(
                            expand=True,
                            controls=[driver_view, customer_view, ride_view],
                        ),
                    ],
                ),
            ),
        ],
    )

    return content
