import flet as ft
import httpx
import threading
import time

PRIMARY   = "#6A1B9A"
ACCENT    = "#AB47BC"
PINK_BTN  = "#E91E8C"
SUCCESS   = "#E91E8C"
ROW_ODD   = "#F3E5F5"
ROW_EVEN  = "#FFFFFF"
HEADER_BG = "#7B1FA2"
TEXT_DK   = "#212121"
TEXT_SEC  = "#757575"
API_LABEL = "#E91E8C"

BASE_URL  = "http://127.0.0.1:8000"

COL_STYLE = ft.TextStyle(color="white", weight=ft.FontWeight.BOLD, size=13)


def make_tf(label):
    return ft.TextField(
        label=label,
        expand=True,
        border_color=ACCENT,
        focused_border_color=PRIMARY,
        text_size=13,
        color=TEXT_DK,
        cursor_color=PRIMARY,
        label_style=ft.TextStyle(color="#9E9E9E"),
    )


def api_get():
    try:
        r = httpx.get(f"{BASE_URL}/languages", timeout=5)
        r.raise_for_status()
        return r.json(), None
    except httpx.ConnectError:
        return None, "Server bağlantısı yoxdur. api.py-ni işlət."
    except Exception as ex:
        return None, str(ex)


def api_post(payload: dict):
    try:
        r = httpx.post(f"{BASE_URL}/languages", json=payload, timeout=5)
        if r.status_code == 400:
            return None, r.json().get("detail", "Xəta")
        r.raise_for_status()
        return r.json(), None
    except httpx.ConnectError:
        return None, "Server bağlantısı yoxdur."
    except Exception as ex:
        return None, str(ex)


def api_delete(lang_id: int):
    try:
        r = httpx.delete(f"{BASE_URL}/languages/{lang_id}", timeout=5)
        if r.status_code == 404:
            return None, r.json().get("detail", "Tapılmadı")
        r.raise_for_status()
        return r.json(), None
    except httpx.ConnectError:
        return None, "Server bağlantısı yoxdur."
    except Exception as ex:
        return None, str(ex)


def window2(page: ft.Page, go_back):

    tf_id    = make_tf("LanguageID")
    tf_name  = make_tf("LanguageName")
    tf_diff  = make_tf("Difficulty")
    tf_total = make_tf("TotalLessons")

    banner = ft.Container(
        visible=False,
        border_radius=8,
        padding=ft.Padding.symmetric(vertical=12, horizontal=16),
        content=ft.Row(spacing=8, controls=[
            ft.Icon(ft.Icons.CHECK_CIRCLE, color="white", size=18),
            ft.Text("", color="white", weight=ft.FontWeight.BOLD, size=13),
        ]),
    )

    table_col = ft.Ref[ft.Column]()

    def build_table(rows):
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
            columns=[
                ft.DataColumn(ft.Text("ID",         style=COL_STYLE)),
                ft.DataColumn(ft.Text("Name",       style=COL_STYLE)),
                ft.DataColumn(ft.Text("Difficulty", style=COL_STYLE)),
                ft.DataColumn(ft.Text("Lessons",    style=COL_STYLE)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(r["id"]),        color=TEXT_DK, size=13)),
                        ft.DataCell(ft.Text(r["name"],           color=TEXT_DK, size=13)),
                        ft.DataCell(ft.Text(r["difficulty"],     color=TEXT_DK, size=13)),
                        ft.DataCell(ft.Text(str(r["total"]),     color=TEXT_DK, size=13)),
                    ],
                    color=ROW_ODD if i % 2 == 0 else ROW_EVEN,
                )
                for i, r in enumerate(rows)
            ],
        )

    def refresh_table():
        data, err = api_get()
        if err:
            show_banner(err, is_error=True)
            return
        table_col.current.controls = [build_table(data)]
        page.update()

    def clear_form():
        for f in [tf_id, tf_name, tf_diff, tf_total]:
            f.value = ""
            f.error_text = None

    def show_banner(msg: str, is_error=False):
        banner.bgcolor = "#C62828" if is_error else SUCCESS
        banner.content.controls[0].name = ft.Icons.ERROR if is_error else ft.Icons.CHECK_CIRCLE
        banner.content.controls[1].value = msg
        banner.visible = True
        page.update()
        def hide():
            time.sleep(3)
            banner.visible = False
            page.update()
        threading.Thread(target=hide, daemon=True).start()

    def post_add(e):
        tf_id.error_text = tf_name.error_text = None
        if not tf_id.value or not tf_name.value:
            tf_id.error_text   = "Tələb olunur" if not tf_id.value   else None
            tf_name.error_text = "Tələb olunur" if not tf_name.value else None
            page.update()
            return
        try:
            new_id    = int(tf_id.value)
            new_total = int(tf_total.value) if tf_total.value else 0
        except ValueError:
            tf_id.error_text    = "Rəqəm olmalıdır" if not tf_id.value.isdigit()   else None
            tf_total.error_text = "Rəqəm olmalıdır" if tf_total.value and not tf_total.value.isdigit() else None
            page.update()
            return

        payload = {"id": new_id, "name": tf_name.value,
                   "difficulty": tf_diff.value, "total": new_total}
        result, err = api_post(payload)
        if err:
            show_banner(err, is_error=True)
            return
        clear_form()
        refresh_table()
        show_banner("Record added successfully!")

    def do_delete(e):
        tf_id.error_text = None
        if not tf_id.value:
            tf_id.error_text = "ID daxil et"
            page.update()
            return
        try:
            del_id = int(tf_id.value)
        except ValueError:
            tf_id.error_text = "Rəqəm olmalıdır"
            page.update()
            return
        result, err = api_delete(del_id)
        if err:
            show_banner(err, is_error=True)
            return
        clear_form()
        refresh_table()
        show_banner("Record deleted successfully!")

    init_data, _ = api_get()
    init_rows = init_data if init_data else []

    content = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                bgcolor=PRIMARY,
                padding=ft.Padding.symmetric(horizontal=8, vertical=10),
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white",
                                  on_click=lambda _: go_back()),
                    ft.Text("Add Language", color="white", size=18,
                            weight=ft.FontWeight.BOLD, expand=True,
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(width=48),
                ]),
            ),

            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=0,
                controls=[
                    ft.Container(
                        padding=ft.Padding.all(14),
                        content=ft.Column(spacing=10, controls=[

                            ft.Text("Table: Languages — GET /languages",
                                    color=API_LABEL, weight=ft.FontWeight.BOLD, size=13),
                            ft.ProgressBar(value=1, color=PRIMARY, bgcolor="#E1BEE7"),

                            ft.Container(
                                border=ft.Border.all(1, "#E1BEE7"),
                                border_radius=8,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                content=ft.Row(expand=True, controls=[
                                    ft.Column(
                                        ref=table_col,
                                        expand=True,
                                        controls=[build_table(init_rows)],
                                    ),
                                ]),
                            ),

                            ft.Divider(height=6, color=ft.Colors.TRANSPARENT),

                            ft.Text("Add New Record — POST /languages",
                                    color=API_LABEL, weight=ft.FontWeight.BOLD, size=13),

                            ft.Row([tf_id,   tf_name],  spacing=10),
                            ft.Row([tf_diff, tf_total], spacing=10),

                            ft.Divider(height=4, color=ft.Colors.TRANSPARENT),

                            ft.Row(spacing=10, controls=[
                                ft.ElevatedButton(
                                    "POST Add", expand=True,
                                    bgcolor=PRIMARY, color="white", height=46,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                    on_click=post_add,
                                ),
                                ft.ElevatedButton(
                                    "DELETE", expand=True,
                                    bgcolor=PINK_BTN, color="white", height=46,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                    on_click=do_delete,
                                ),
                            ]),

                            banner,
                        ]),
                    ),
                ],
            ),
        ],
    )

    return content
