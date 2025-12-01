import pygame
import os
import random
from src.settings import *
from src.entities import Document

class DocumentFactory:
    def __init__(self):
        # Font boyutlarını belge boyutuna göre ayarladık
        self.font = pygame.font.SysFont("Courier New", 14, bold=True)
        self.large_font = pygame.font.SysFont("Courier New", 16, bold=True)
        self.assets = {}
        self._load_doc_assets()

    def _load_doc_assets(self):
        doc_path = os.path.join(ASSET_PATH, "doc")
        
        # Genel Belgeler
        for key in ["entry", "health"]:
            filename = f"{key}.png" 
            full_path = os.path.join(doc_path, filename)
            if os.path.exists(full_path):
                self.assets[key] = pygame.image.load(full_path).convert_alpha()
            else:
                print(f"UYARI: {filename} bulunamadı!")

        # Ülke Kimlikleri
        countries = ["latvia", "lithuania", "ukraine", "belarus", "kazakhistan", "turkey", "sweden", "germany"]
        for c in countries:
            fname = f"{c}_id.png"
            fpath = os.path.join(doc_path, fname)
            if os.path.exists(fpath):
                self.assets[f"{c}_id"] = pygame.image.load(fpath).convert_alpha()

    def _create_base_surface(self, asset_key, doc_type_key):
        """Resmi yükle ve HEDEF BOYUTA GETİR (Yazı yazmadan önce!)"""
        target_size = DOC_SIZES[doc_type_key] # settings.py'dan alıyor
        
        if asset_key in self.assets:
            raw_img = self.assets[asset_key]
            # ÖNCE RESİZE ET
            return pygame.transform.smoothscale(raw_img, target_size)
        else:
            # Asset yoksa boş kutu
            surf = pygame.Surface(target_size)
            surf.fill((200, 200, 180))
            return surf

    def create_id_card(self, npc_data):
        country = npc_data.get("country", "turkey").lower()
        base_key = f"{country}_id"
        
        # 1. Küçültülmüş zemini al
        surf = self._create_base_surface(base_key, "id_card")
        layout = DOC_LAYOUTS["id_card"]
        
        # 2. Yazıları bu küçük zemin üzerine yaz (Koordinatlar artık tutacak)
        self._draw_text(surf, npc_data["name"], layout["name"])
        self._draw_text(surf, "ID: " + str(random.randint(10000,99999)), layout["id_no"])
        self._draw_text(surf, npc_data["dob"], layout["dob"])
        self._draw_text(surf, npc_data["issue"], layout["issue"])
        self._draw_text(surf, npc_data["expiry"], layout["expiry"])
        
        # 3. Fotoğrafı Yapıştır
        if "photo" in npc_data and npc_data["photo"]:
            x, y, w, h = layout["photo_rect"]
            try:
                photo = pygame.transform.scale(npc_data["photo"], (w, h))
                surf.blit(photo, (x, y))
            except: pass

        return Document(100, 400, surf, "ID Card")

    def create_entry_permit(self, npc_data):
        surf = self._create_base_surface("entry", "entry_permit")
        layout = DOC_LAYOUTS["entry_permit"]
        
        self._draw_text(surf, npc_data["name"], layout["name"])
        self._draw_text(surf, npc_data["country"].upper(), layout["nationality"])
        self._draw_text(surf, "15.05.1991", layout["valid_until"])
        self._draw_text(surf, "TRANSIT", layout["purpose"])
        
        return Document(280, 420, surf, "Entry Permit")

    def create_health_report(self, npc_data):
        surf = self._create_base_surface("health", "health_report")
        layout = DOC_LAYOUTS["health_report"]
        
        status = "CLEAR" if random.random() > 0.1 else "INFECTED"
        color = (0, 100, 0) if status == "CLEAR" else (150, 0, 0)
        
        self._draw_text(surf, npc_data["name"], layout["name"])
        self._draw_text(surf, status, layout["status"], color=color, font=self.large_font)
        self._draw_text(surf, "10.05.1991", layout["exam_date"])
        self._draw_text(surf, "Dr. A. Ivan", layout["doctor"])
        self._draw_text(surf, "None", layout["notes"])
        
        return Document(460, 440, surf, "Health Report")

    def _draw_text(self, surface, text, pos, color=(30, 30, 30), font=None):
        if font is None: font = self.font
        render = font.render(str(text), True, color)
        surface.blit(render, pos)