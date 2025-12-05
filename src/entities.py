import pygame
import os
import random
from src.settings import *

class Document(pygame.sprite.Sprite):
    def __init__(self, x, y, image_surface, doc_type_name):
        super().__init__()
        self.image = image_surface.copy() # Orijinal temiz kopya
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.doc_type = doc_type_name
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.is_stamped = False

    def add_mark(self, mark_surface, center_pos):
        """Damgayı belgenin üzerine basar (Clipping ile)."""
        # 1. Damganın kağıt üzerindeki konumu (Sol üst köşe)
        local_x = center_pos[0] - self.rect.x - (mark_surface.get_width() // 2)
        local_y = center_pos[1] - self.rect.y - (mark_surface.get_height() // 2)
        
        # 2. Damgayı bas (Pygame'in blit fonksiyonu otomatik clipping yapar!)
        # Yani damganın kağıt sınırından taşan kısmı otomatik olarak çizilmez.
        # Sadece 'area' parametresi kullanmamıza gerek yok, blit bunu doğal yapar.
        self.image.blit(mark_surface, (local_x, local_y))
        
        self.is_stamped = True

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.offset_x = self.rect.x - event.pos[0]
                self.offset_y = self.rect.y - event.pos[1]
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] + self.offset_x
            self.rect.y = event.pos[1] + self.offset_y
        return False

# --- KEPENK SINIFI (AYNEN KALIYOR) ---
class Shutter(pygame.sprite.Sprite):
    def __init__(self, glass_rect):
        super().__init__()
        self.frames = []
        custom_width = 500  
        custom_height = 1300 
        self._load_frames((custom_width, custom_height)) 
        self.current_frame_index = 0
        self.image = self.frames[self.current_frame_index]
        self.rect = self.image.get_rect(center=glass_rect.center)
        self.state = "OPEN"
        self.animation_speed = 10 
        self.last_update_time = 0
        self.frame_duration = 1000 // self.animation_speed
        self.on_closed_callback = None

    def _load_frames(self, target_size):
        path = os.path.join(ASSET_PATH, "shutter")
        if not os.path.exists(path):
             surf = pygame.Surface(target_size, pygame.SRCALPHA)
             self.frames.append(surf)
             return
        for i in range(6):
            filename = f"shutter_{i}.png"
            full_path = os.path.join(path, filename)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.smoothscale(img, target_size)
                self.frames.append(img)
            except:
                 surf = pygame.Surface(target_size, pygame.SRCALPHA)
                 self.frames.append(surf)
        if not self.frames: self.frames.append(pygame.Surface(target_size, pygame.SRCALPHA))

    def trigger_close(self, callback_on_closed):
        if self.state == "OPEN":
            self.state = "CLOSING"
            self.current_frame_index = 0
            self.on_closed_callback = callback_on_closed
            self.last_update_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if self.state == "CLOSING":
            if now - self.last_update_time > self.frame_duration:
                self.last_update_time = now
                self.current_frame_index += 1
                if self.current_frame_index >= len(self.frames):
                    self.current_frame_index = len(self.frames) - 1
                    self.state = "CLOSED"
                    if self.on_closed_callback:
                        self.on_closed_callback()
                        self.on_closed_callback = None 
                    self.state = "OPENING" 
                self.image = self.frames[self.current_frame_index]
        elif self.state == "OPENING":
             if now - self.last_update_time > self.frame_duration:
                self.last_update_time = now
                self.current_frame_index -= 1
                if self.current_frame_index < 0:
                    self.current_frame_index = 0
                    self.state = "OPEN"
                self.image = self.frames[self.current_frame_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# --- KAŞE SINIFI (GÜNCELLENDİ) ---
class StampTool(pygame.sprite.Sprite):
    def __init__(self, type_name, start_pos):
        super().__init__()
        self.type_name = type_name 
        self.start_pos = start_pos 
        
        # Dosya isimleri: stamp_1.jpg, seal_1.jpg (veya png)
        suffix = '1' if type_name == 'approved' else '2'
        
        self.image = self._load_image(f"stamp_{suffix}", is_tool=True)
        self.seal_image = self._load_image(f"seal_{suffix}", is_tool=False)
        
        # Başlangıç konumu
        self.rect = self.image.get_rect(topleft=start_pos)
        self.dragging = False
        
    def _load_image(self, name, is_tool):
        # 'seals' klasörüne bak
        path = os.path.join(ASSET_PATH, "seals", f"{name}.jpg")
        # Eğer jpg yoksa png dene
        if not os.path.exists(path):
            path = os.path.join(ASSET_PATH, "seals", f"{name}.png")
            
        try:
            img = pygame.image.load(path).convert_alpha()
            # Boyutlandırma: Alet küçük, damga izi normal
            if is_tool:
                # Kaşe aleti (Elde duran) - Biraz küçük olsun
                return pygame.transform.smoothscale(img, (100, 100))
            else:
                # Damga izi (Kağıda basılan) - Okunabilir boyutta
                return pygame.transform.smoothscale(img, (130, 130))
        except Exception as e:
            print(f"HATA: {name} yüklenemedi! ({e})")
            # Görsel yoksa renkli kare
            s = pygame.Surface((80, 80))
            color = (0, 255, 0) if "1" in name else (255, 0, 0)
            s.fill(color)
            return s

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                return True 
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                self.rect.topleft = self.start_pos
                return "dropped" 
                
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.center = event.pos
            
        return False

class AnimatedNPC(pygame.sprite.Sprite):
    def __init__(self, frames, race_code=None):
        super().__init__()
        self.frames = list(frames)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.state = "IDLE"
        self.frame_duration_ms = int(1000 / 3)
        self.last_update = pygame.time.get_ticks()
        self.reaction_end_time = None
        self.race_code = race_code
        self.is_monster = random.choice([True, False, False])

    def update(self):
        now = pygame.time.get_ticks()
        if self.state == "TALKING":
            if now - self.last_update >= self.frame_duration_ms:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                self.last_update = now
            if self.reaction_end_time and now >= self.reaction_end_time:
                self.state = "IDLE"
                self.current_frame = 0
                self.image = self.frames[0]
                self.reaction_end_time = None
        elif self.current_frame != 0:
            self.current_frame = 0
            self.image = self.frames[0]

    def trigger_reaction(self, reaction_type="positive"):
        now = pygame.time.get_ticks()
        self.state = "TALKING"
        self.current_frame = 0
        self.image = self.frames[0]
        self.last_update = now
        self.reaction_end_time = now + self.frame_duration_ms * len(self.frames)