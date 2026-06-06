# LinguaApp — Agent Context File
> Son yenilənmə: 2026-06-06

## Context
Bu fayl AI agentə LinguaApp layihəsini sürətlə başa salır. Hər yeni task üçün bu faylı oxu, sonra dəyişiklik et.

---

## Layihə Strukturu

```
c:\Users\Admin\Desktop\sample\
├── test.py        # Flet frontend (UI)
├── api.py         # FastAPI backend (server)
├── db.sqlite      # SQLite database (server ilk dəfə işləyəndə avtomatik yaranır)
└── .venv\         # Python 3.12.10 virtual environment
```

**İşlətmək üçün — iki ayrı terminal lazımdır:**
```powershell
# Terminal 1 — backend
.venv\Scripts\python.exe -m uvicorn api:app --reload

# Terminal 2 — frontend
.venv\Scripts\python.exe test.py
```

---

## Quraşdırılmış Paketlər

| Paket | Versiya | Rol |
|-------|---------|-----|
| Python | 3.12.10 | Runtime |
| flet | 0.85.2 | UI framework |
| httpx | 0.28.1 | HTTP client |
| fastapi | (qurulmalıdır) | Backend framework |
| uvicorn | (qurulmalıdır) | ASGI server |
| pydantic | fastapi ilə gəlir | Data validation |
| sqlite3 | stdlib (quraşdırma lazım deyil) | Database driver |

---

## Data Modeli

Tək obyekt — **language record:**
```python
{
    "id": int,           # unikal ID
    "name": str,         # dil adı (məs. "Spanish")
    "difficulty": str,   # səviyyə (məs. "Beginner", "Intermediate", "Advanced")
    "total": int         # ümumi dərs sayı (məs. 50)
}
```

Başlanğıc data (api.py — `db.sqlite` yoxdursa avtomatik yazılır, restart-da **qalır**):
```python
{"id": 1, "name": "Spanish",  "difficulty": "Beginner",     "total": 50}
{"id": 2, "name": "Japanese", "difficulty": "Advanced",     "total": 80}
{"id": 3, "name": "French",   "difficulty": "Intermediate", "total": 60}
```

**SQLite cədvəl strukturu (`languages` table):**
```sql
CREATE TABLE languages (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL,
    difficulty TEXT    NOT NULL DEFAULT '',
    total      INTEGER NOT NULL DEFAULT 0
)
```

---

## API Endpoints (`http://127.0.0.1:8000`)

| Method | Path | Payload | Response | Xəta |
|--------|------|---------|----------|------|
| GET | `/languages` | — | `[{id,name,difficulty,total}, ...]` | 500 |
| POST | `/languages` | `{id,name,difficulty?,total?}` | yaradılan obyekt (201) | 400 — ID mövcuddur |
| DELETE | `/languages/{lang_id}` | — | silinən obyekt | 404 — tapılmadı |

**Yeni endpoint əlavə etmək üçün `api.py`-a bax.** Şablon (PUT nümunəsi):
```python
@app.put("/languages/{lang_id}")
def update_language(lang_id: int, lang: LanguageIn):
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM languages WHERE id = ?", (lang_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"ID {lang_id} tapılmadı")
        conn.execute(
            "UPDATE languages SET name=?, difficulty=?, total=? WHERE id=?",
            (lang.name, lang.difficulty, lang.total, lang_id),
        )
    return {**lang.model_dump(), "id": lang_id}
```

**`api.py`-dakı köməkçi funksiyalar:**
```python
@contextmanager
def get_conn():          # hər sorğu üçün connection aç/bağla, auto-commit
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # nəticəni dict kimi istifadə etməyə imkan verir
    ...

def init_db():           # server başlayanda: cədvəl yoxdursa yarat, seed data yaz
    ...
```

---

## Rəng Sabitləri (`test.py` yuxarısında)

```python
PRIMARY   = "#6A1B9A"   # tünd bənövşəyi — header, düymə
ACCENT    = "#AB47BC"   # açıq bənövşəyi — focus, icon
PINK_BTN  = "#E91E8C"   # çəhrayı — DELETE düyməsi, API label
SUCCESS   = "#E91E8C"   # çəhrayı — uğur banner (PINK_BTN ilə eynidir)
ROW_ODD   = "#F3E5F5"   # çox açıq bənövşəyi — cütdüzlü sır
ROW_EVEN  = "#FFFFFF"   # ağ — tək sıra
HEADER_BG = "#7B1FA2"   # orta bənövşəyi — cədvəl başlığı
TEXT_DK   = "#212121"   # tünd boz — əsas mətn
TEXT_SEC  = "#757575"   # orta boz — ikinci dərəcəli mətn
API_LABEL = "#E91E8C"   # çəhrayı — endpoint label mətni
```

---

## UI Strukturu (`test.py`)

```
ft.Stack (root)
├── Container (Window 1 — visible=True)
│   └── window1()
│       ├── Header (PRIMARY, "LinguaApp" + menu icon → go_to_add())
│       ├── Body Container (3 tab görünüşü)
│       │   ├── languages_view()  — GET /languages cədvəli + BottomSheet
│       │   ├── progress_view()   — placeholder
│       │   └── lessons_view()    — placeholder
│       └── NavigationBar (3 tab: Languages / My Progress / Lessons)
│
└── Container (Window 2 — visible=False)
    └── window2()
        ├── Header (PRIMARY, geri ox + "Add Language")
        ├── GET /languages cədvəli (read-only)
        ├── 4 TextField: LanguageID, LanguageName, Difficulty, TotalLessons
        ├── ElevatedButton "POST Add" (PRIMARY)
        ├── ElevatedButton "DELETE"   (PINK_BTN)
        └── Banner (uğur/xəta mesajı, 3 saniyə görünür)
```

**Naviqasiya:**
- Menu düyməsi → `go_to_add()` → Window 2 görünür, Window 1 gizlənir
- Geri ox → `go_back()` → Window 1 görünür, cədvəl yenilənir

---

## Flet 0.85.2 — Düzgün Sintaksis

**VACIB:** `ft.padding` və `ft.border` **modul**dur, **class** deyil. Metodlar class-dadır:

```python
# DÜZGÜN ✅
ft.Padding.all(14)
ft.Padding.symmetric(horizontal=16, vertical=12)
ft.Padding(left=20, top=8, right=20, bottom=24)

ft.Border.all(0)
ft.Border.all(1, "#E1BEE7")

# YANLIŞ ❌
ft.padding.all(14)      # AttributeError
ft.border.all(1, ...)   # AttributeError
```

**BottomSheet:**
```python
# 0.85.2-də show_dialog() ilə aç:
page.show_dialog(bottom_sheet)
# open=True işləmir
```

**App başlatma:**
```python
ft.run(main)          # ✅ düzgün
ft.app(target=main)   # ❌ deprecated (DeprecationWarning)
```

**Ref ilə imperativ yeniləmə:**
```python
col_ref = ft.Ref[ft.Column]()
# Dəyişdirmək üçün:
col_ref.current.controls = [yeni_kontrol]
page.update()
```

**TextField fabrikası (`make_tf`):**
```python
def make_tf(label):
    return ft.TextField(
        label=label, expand=True,
        border_color=ACCENT, focused_border_color=PRIMARY,
        text_size=13, color=TEXT_DK, cursor_color=PRIMARY,
        label_style=ft.TextStyle(color="#9E9E9E"),
    )
```

**DataTable şablonu:**
```python
ft.DataTable(
    expand=True, width=float("inf"),
    bgcolor=ft.Colors.TRANSPARENT,
    border=ft.Border.all(0),
    heading_row_color=HEADER_BG,
    heading_row_height=40,
    data_row_min_height=36, data_row_max_height=48,
    column_spacing=16,
    columns=[ft.DataColumn(ft.Text("Ad", style=COL_STYLE)), ...],
    rows=[
        ft.DataRow(
            color=ROW_ODD if i%2==0 else ROW_EVEN,
            cells=[ft.DataCell(ft.Text(str(r["id"]), color=TEXT_DK, size=13)), ...],
        )
        for i, r in enumerate(rows)
    ],
)
```

---

## Tez-tez Dəyişdirilən Yerlər

| Nə dəyişmək istəyirsən | Hara bax |
|------------------------|----------|
| Rənglər | `test.py` — yuxarı 15 sətir |
| Yeni API endpoint | `api.py` — `@app.METHOD` dekoratoru |
| Yeni TextField əlavə et | `window2()` — `make_tf()` + `ft.Row` içinə əlavə et |
| Yeni cədvəl sütunu | `build_table()` / `build_clickable_table()` — columns + rows |
| Tab əlavə et | `window1()` — `views` list + `NavigationBar destinations` |
| Data modeli dəyiş | `api.py` — `LanguageIn` class + `languages` list |
| BottomSheet məzmunu | `window1()` — `bs_title`, `bs_subtitle` dəyərləri |

---

## Məlum Məhdudiyyətlər

- API **SQLite**-dır — data `db.sqlite` faylında qalır, restart-da **silinmir**
- "My Progress" və "Lessons" tabları **placeholder**dır — funksionallıq yoxdur
- Banner auto-hide **threading** ilə — `time.sleep(3)` daemon thread-də işləyir
- CORS **tam açıqdır** (`allow_origins=["*"]`)
- httpx timeout **sabit** — 5 saniyə
