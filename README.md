# RideApp

Sürücü, müştəri və gediş məlumatlarını idarə etmək üçün FastAPI backend + Flet UI tətbiqi.

## Tələblər

```
pip install fastapi uvicorn flet httpx
```

## İşə salma

**1. Backend-i başlat:**
```bash
uvicorn api:app --reload
```

**2. UI-ı başlat (ayrı terminalda):**
```bash
python test.py
```

## API Endpointləri

| Method | Endpoint | Təsvir |
|--------|----------|--------|
| GET | `/drivers` | Bütün sürücüləri gətir |
| POST | `/drivers` | Yeni sürücü əlavə et |
| DELETE | `/drivers/{id}` | Sürücü sil |
| GET | `/customers` | Bütün müştəriləri gətir |
| POST | `/customers` | Yeni müştəri əlavə et |
| DELETE | `/customers/{id}` | Müştəri sil |
| GET | `/rides` | Bütün gedişləri gətir |
| POST | `/rides` | Yeni gediş əlavə et |
| DELETE | `/rides/{id}` | Gediş sil |

## Qeyd

- VehicleType yalnız: `Sedan`, `SUV`, `Minivan`, `Truck`
- API docs: `http://127.0.0.1:8000/docs`
