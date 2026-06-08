import sqlite3
from contextlib import contextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="RideApp API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent / "db.sqlite"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Driver (
                DriverID    INTEGER PRIMARY KEY,
                FullName    TEXT    NOT NULL,
                Phone       TEXT    NOT NULL DEFAULT '',
                VehicleType TEXT    NOT NULL DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Customers (
                CustomerID INTEGER PRIMARY KEY,
                FullName   TEXT    NOT NULL,
                Phone      TEXT    NOT NULL DEFAULT '',
                Email      TEXT    NOT NULL DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Rides (
                RideID     INTEGER PRIMARY KEY,
                DriverID   INTEGER NOT NULL REFERENCES Driver(DriverID),
                CustomerID INTEGER NOT NULL REFERENCES Customers(CustomerID),
                PickUP     TEXT    NOT NULL DEFAULT '',
                Fare       REAL    NOT NULL DEFAULT 0.0
            )
        """)
        if conn.execute("SELECT COUNT(*) FROM Driver").fetchone()[0] == 0:
            conn.executemany("INSERT INTO Driver VALUES (?,?,?,?)", [
                (1, "Ali Həsənov",   "050-123-4567", "Sedan"),
                (2, "Vüsal Əliyev", "055-987-6543", "SUV"),
            ])
        if conn.execute("SELECT COUNT(*) FROM Customers").fetchone()[0] == 0:
            conn.executemany("INSERT INTO Customers VALUES (?,?,?,?)", [
                (1, "Nigar Məmmədova", "051-111-2222", "nigar@mail.az"),
                (2, "Tural Hüseynov",  "070-333-4444", "tural@mail.az"),
            ])
        if conn.execute("SELECT COUNT(*) FROM Rides").fetchone()[0] == 0:
            conn.executemany("INSERT INTO Rides VALUES (?,?,?,?,?)", [
                (1, 1, 1, "Nizami küçəsi", 4.5),
                (2, 2, 2, "Hava limani",   12.0),
            ])


init_db()


#  Models
class DriverIn(BaseModel):
    DriverID: int
    FullName: str    = Field(..., min_length=3, max_length=100)
    Phone: str       = Field(..., min_length=6, max_length=20)
    VehicleType: str = Field(..., pattern=r"^(Sedan|SUV|Minivan|Truck)$")

    @field_validator("DriverID")
    @classmethod
    def id_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("DriverID müsbət olmalidir")
        return v


class CustomerIn(BaseModel):
    CustomerID: int
    FullName: str
    Phone: str = ""
    Email: str = ""


class RideIn(BaseModel):
    RideID: int
    DriverID: int
    CustomerID: int
    PickUP: str = ""
    Fare: float = 0.0


#    Drivers
@app.get("/drivers")
def get_drivers():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM Driver ORDER BY DriverID").fetchall()
    return [dict(r) for r in rows]


@app.post("/drivers", status_code=201)
def add_driver(d: DriverIn):
    with get_db() as conn:
        if conn.execute("SELECT 1 FROM Driver WHERE DriverID=?", (d.DriverID,)).fetchone():
            raise HTTPException(400, detail=f"DriverID {d.DriverID} artiq mövcuddur")
        conn.execute("INSERT INTO Driver VALUES (?,?,?,?)",
                     (d.DriverID, d.FullName, d.Phone, d.VehicleType))
    return d.model_dump()


@app.delete("/drivers/{driver_id}")
def delete_driver(driver_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM Driver WHERE DriverID=?", (driver_id,)).fetchone()
        if not row:
            raise HTTPException(404, detail=f"DriverID {driver_id} tapilmadi")
        conn.execute("DELETE FROM Driver WHERE DriverID=?", (driver_id,))
    return dict(row)


#    Customers
@app.get("/customers")
def get_customers():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM Customers ORDER BY CustomerID").fetchall()
    return [dict(r) for r in rows]


@app.post("/customers", status_code=201)
def add_customer(c: CustomerIn):
    with get_db() as conn:
        if conn.execute("SELECT 1 FROM Customers WHERE CustomerID=?", (c.CustomerID,)).fetchone():
            raise HTTPException(400, detail=f"CustomerID {c.CustomerID} artiq mövcuddur")
        conn.execute("INSERT INTO Customers VALUES (?,?,?,?)",
                     (c.CustomerID, c.FullName, c.Phone, c.Email))
    return c.model_dump()


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM Customers WHERE CustomerID=?", (customer_id,)).fetchone()
        if not row:
            raise HTTPException(404, detail=f"CustomerID {customer_id} tapılmadı")
        conn.execute("DELETE FROM Customers WHERE CustomerID=?", (customer_id,))
    return dict(row)


#   Rides

@app.get("/rides")
def get_rides():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM Rides ORDER BY RideID").fetchall()
    return [dict(r) for r in rows]


@app.post("/rides", status_code=201)
def add_ride(r: RideIn):
    with get_db() as conn:
        if conn.execute("SELECT 1 FROM Rides WHERE RideID=?", (r.RideID,)).fetchone():
            raise HTTPException(400, detail=f"RideID {r.RideID} artıq mövcuddur")
        conn.execute("INSERT INTO Rides VALUES (?,?,?,?,?)",
                     (r.RideID, r.DriverID, r.CustomerID, r.PickUP, r.Fare))
    return r.model_dump()


@app.delete("/rides/{ride_id}")
def delete_ride(ride_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM Rides WHERE RideID=?", (ride_id,)).fetchone()
        if not row:
            raise HTTPException(404, detail=f"RideID {ride_id} tapılmadı")
        conn.execute("DELETE FROM Rides WHERE RideID=?", (ride_id,))
    return dict(row)


#   Vehicle Types
@app.get("/vehicle-types")
def get_vehicle_types():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT VehicleType FROM Driver WHERE VehicleType != '' ORDER BY VehicleType"
        ).fetchall()
    types = [r[0] for r in rows]
    return {"types": types, "count": len(types)}
