import flet as ft
import httpx

from window2 import window2

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


# ═══════════════════════════════════════════════════════════════
# WINDOW 1 — Main
# ═══════════════════════════════════════════════════════════════
def window1(page: ft.Page, go_to_add):

    bs_title    = ft.Text("", color=PRIMARY, weight=ft.FontWeight.BOLD, size=14)
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
        on_dismiss=lambda e: None,
    )

    def open_bs(row_data: dict):
        bs_title.value    = "BOTTOM SHEET"
        bs_subtitle.value = (f"{row_data['name']} · {row_data['difficulty']} · "
                             f"{row_data['total']} lessons total")
        page.show_dialog(bottom_sheet)

    def build_clickable_table(rows):
        data_rows = []
        for i, r in enumerate(rows):
            rd = r
            data_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(rd["id"]),    color=TEXT_DK, size=13)),
                        ft.DataCell(ft.Text(rd["name"],       color=TEXT_DK, size=13)),
                        ft.DataCell(ft.Text(rd["difficulty"], color=TEXT_DK, size=13)),
                        ft.DataCell(ft.Text(str(rd["total"]), color=TEXT_DK, size=13)),
                    ],
                    color=ROW_ODD if i % 2 == 0 else ROW_EVEN,
                    on_select_change=lambda e, d=rd: open_bs(d),
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
            columns=[
                ft.DataColumn(ft.Text("ID",         style=COL_STYLE)),
                ft.DataColumn(ft.Text("Name",       style=COL_STYLE)),
                ft.DataColumn(ft.Text("Difficulty", style=COL_STYLE)),
                ft.DataColumn(ft.Text("Lessons",    style=COL_STYLE)),
            ],
            rows=data_rows,
        )

    table_col = ft.Ref[ft.Column]()
    body      = ft.Ref[ft.Container]()
    err_text  = ft.Ref[ft.Text]()

    def refresh_main_table():
        data, err = api_get()
        if err:
            if err_text.current:
                err_text.current.value = err
                err_text.current.visible = True
        else:
            if err_text.current:
                err_text.current.visible = False
            if table_col.current:
                table_col.current.controls = [build_clickable_table(data)]
        page.update()

    def languages_view():
        init_data, init_err = api_get()
        init_rows = init_data if init_data else []

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
            controls=[
                ft.Container(
                    bgcolor="#FCE4EC", border_radius=6,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    content=ft.Text("GET /languages  →  loads data on open",
                                    color=PINK_BTN, size=11),
                ),
                ft.ProgressBar(value=1, color=PRIMARY, bgcolor="#E1BEE7"),

                ft.Text(
                    ref=err_text,
                    value=init_err or "",
                    color="#C62828", size=12,
                    visible=bool(init_err),
                ),

                ft.Container(
                    border=ft.Border.all(1, "#E1BEE7"),
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Row(expand=True, controls=[
                        ft.Column(
                            ref=table_col,
                            expand=True,
                            controls=[build_clickable_table(init_rows)],
                        ),
                    ]),
                ),
            ],
        )

    def progress_view():
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Container(height=40),
                ft.Icon(ft.Icons.BAR_CHART, size=56, color=ACCENT),
                ft.Text("My Progress", size=18, color=TEXT_SEC),
                ft.Text("İstifadəçinin tərəqqisi burada olacaq.",
                        color=TEXT_SEC, size=13, text_align=ft.TextAlign.CENTER),
            ],
        )

    def lessons_view():
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Container(height=40),
                ft.Icon(ft.Icons.SCHOOL, size=56, color=ACCENT),
                ft.Text("Lessons", size=18, color=TEXT_SEC),
                ft.Text("Dərslər siyahısı burada olacaq.",
                        color=TEXT_SEC, size=13, text_align=ft.TextAlign.CENTER),
            ],
        )

    views = [languages_view, progress_view, lessons_view]

    def on_nav_change(e):
        idx = e.control.selected_index
        body.current.content = views[idx]()
        if idx == 0:
            refresh_main_table()
        else:
            page.update()

    content = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                bgcolor=PRIMARY,
                padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                content=ft.Row([
                    ft.Text("LinguaApp", color="white", size=18,
                            weight=ft.FontWeight.BOLD, expand=True),
                    ft.IconButton(icon=ft.Icons.MENU, icon_color="white",
                                  on_click=lambda _: go_to_add(),
                                  tooltip="Add Language"),
                ]),
            ),

            ft.Container(
                ref=body,
                expand=True,
                padding=ft.Padding.all(14),
                content=languages_view(),
            ),

            ft.NavigationBar(
                selected_index=0,
                bgcolor="white",
                indicator_color=ft.Colors.PURPLE_100,
                on_change=on_nav_change,
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.LANGUAGE,    label="Languages"),
                    ft.NavigationBarDestination(icon=ft.Icons.LEADERBOARD, label="My Progress"),
                    ft.NavigationBarDestination(icon=ft.Icons.BOOK,        label="Lessons"),
                ],
            ),
        ],
    )

    return content, refresh_main_table


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main(page: ft.Page):
    page.title    = "LinguaApp"
    page.bgcolor  = "#F8F6FF"
    page.padding  = 0
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
