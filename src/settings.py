import os
import pygame

# --- YOLLAR ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_PATH = os.path.join(BASE_DIR, "assets")

# --- EKRAN ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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
CHAR_SCALE_HEIGHT = 200 

# --- BELGE DÜZENİ (ESKİ HALİ) ---
DOC_SIZES = {
    "id_card": (300, 190),      # ID Kart boyutu
    "entry_permit": (300, 400), # Standart boyut
    "health_report": (300, 400) # Standart boyut
}

# Yazıların Koordinatları (x, y) - Eski koordinatlar
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

# --- KAŞE AYARLARI ---
STAMP_POSITIONS = {
    "approve": (SCREEN_WIDTH - 150, 400), # Masanın sağı
    "deny": (SCREEN_WIDTH - 150, 520)     # Masanın sağı (biraz aşağıda)
}

STAMP_COLOR_APPROVE = (0, 150, 0) # Yeşil
STAMP_COLOR_DENY = (180, 0, 0)    # Kırmızı

# --- BED / DAY CYCLE ---
BED_ROOM_INDEX = 5
# X=250 (Daha geniş), Y=230 (Daha yukarıdan başlar)
BED_RECT = pygame.Rect(250, 230, 380, 300)

# UI Colors
FONT_COLOR_UI = (200, 200, 200)