import sqlite3
from contextlib import contextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="LinguaApp API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent / "db.sqlite"

SEED = [
    {"id": 1, "name": "Spanish",  "difficulty": "Beginner",     "total": 50},
    {"id": 2, "name": "Japanese", "difficulty": "Advanced",     "total": 80},
    {"id": 3, "name": "French",   "difficulty": "Intermediate", "total": 60},
]


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS languages (
                id         INTEGER PRIMARY KEY,
                name       TEXT    NOT NULL,
                difficulty TEXT    NOT NULL DEFAULT '',
                total      INTEGER NOT NULL DEFAULT 0
            )
        """)
        if conn.execute("SELECT COUNT(*) FROM languages").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO languages VALUES (:id, :name, :difficulty, :total)",
                SEED,
            )


init_db()


class LanguageIn(BaseModel):
    id: int
    name: str
    difficulty: str = ""
    total: int = 0


@app.get("/languages")
def get_languages():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM languages ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.post("/languages", status_code=201)
def add_language(lang: LanguageIn):
    with get_conn() as conn:
        exists = conn.execute(
            "SELECT 1 FROM languages WHERE id = ?", (lang.id,)
        ).fetchone()
        if exists:
            raise HTTPException(status_code=400, detail=f"ID {lang.id} artıq mövcuddur")
        conn.execute(
            "INSERT INTO languages VALUES (?, ?, ?, ?)",
            (lang.id, lang.name, lang.difficulty, lang.total),
        )
    return lang.model_dump()


@app.delete("/languages/{lang_id}")
def delete_language(lang_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM languages WHERE id = ?", (lang_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"ID {lang_id} tapılmadı")
        conn.execute("DELETE FROM languages WHERE id = ?", (lang_id,))
    return dict(row)
