import os
import pygame

# --- YOLLAR ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_PATH = os.path.join(BASE_DIR, "assets")

# --- EKRAN ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
BG_COLOR = (10, 10, 10)

# --- ZOOM AYARLARI ---
IDLE_TIME_TRIGGER = 2.0
AUTO_ZOOM_SPEED = 0.004
MAX_AUTO_ZOOM = 1.2
MANUAL_ZOOM_LEVEL = 1.2
MANUAL_ZOOM_SPEED = 0.05
PAN_SPEED = 0.1
EDGE_THRESHOLD = 40
START_HOUR = 9
END_HOUR = 17

# --- KARAKTER AYARLARI ---
CHAR_SCALE_HEIGHT = 500 

# --- BELGE DÜZENİ (REVİZE EDİLDİ) ---
# Entry ve Health belgeleri genişletildi (Width arttı)
DOC_SIZES = {
    "id_card": (300, 190),      # ID Kart boyutu
    "entry_permit": (300, 400), # Daha geniş A4 oranı
    "health_report": (300, 400) # Daha geniş A4 oranı
}

# Yazıların Koordinatları (x, y) - Yeni boyutlara göre ayarlandı
DOC_LAYOUTS = {
    "id_card": {
        "name": (125, 52),
        "id_no": (125, 75),
        "dob": (125, 98),
        "issue": (125, 120),
        "expiry": (125, 142),
        "photo_rect": (20, 32, 85, 105)
    },
    "entry_permit": {
        "name": (30, 80),
        "nationality": (30, 125),
        "valid_until": (30, 175),
        "purpose": (30, 225),
        "stamp_area": (30, 275)
    },
    "health_report": {
        "name": (30, 65),
        "status": (170, 65), # Sağ tarafa hizalı
        "exam_date": (30, 115),
        "symptoms": (150, 115), # Kutu alanı
        "doctor": (30, 165),
        "notes": (30, 215)
    }
}

# --- BED / DAY CYCLE ---
# Index of the bedroom room image (0-based, room_0 .. room_7)
BED_ROOM_INDEX = 7
# Clickable bed area in screen coordinates (placeholder - adjustable)
BED_RECT = pygame.Rect(100, 300, 400, 300)

# UI Colors
FONT_COLOR_UI = (200, 200, 200)