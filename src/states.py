import pygame
import os
import math
import time
import random
from src.settings import *
from src.entities import Document
from src.generator import CharacterGenerator
from src.doc_generator import DocumentFactory

# ... (GameStateManager ve BaseState AYNI - Dokunma) ...
class GameStateManager:
    def __init__(self, game):
        self.game = game
        self.states = {}
        self.current_state = None
    def add_state(self, name, state):
        self.states[name] = state
    def change_state(self, name):
        if self.current_state: pass
        self.current_state = self.states[name]
        self.current_state.on_enter()

class BaseState:
    def __init__(self, manager):
        self.manager = manager
        self.game = manager.game
        self.screen = manager.game.screen
        self.font = pygame.font.SysFont("Arial", 20)
    def handle_events(self, events): pass
    def update(self): pass
    def draw(self): pass
    def on_enter(self): pass

# --- MASA MODU ---
class DeskState(BaseState):
    def __init__(self, manager):
        super().__init__(manager)
        
        # ... (Yüklemeler ve Değişkenler AYNI) ...
        self.room_images = []
        rooms_folder = os.path.join(ASSET_PATH, "rooms")
        for i in range(8):
            path = os.path.join(rooms_folder, f"room_{i}.png")
            if not os.path.exists(path): path = os.path.join(ASSET_PATH, f"room_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert()
                img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.room_images.append(img)
            else:
                self.room_images.append(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)))

        self.generator = CharacterGenerator(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.doc_factory = DocumentFactory()
        self.documents = []
        self.current_npc = None
        
        self.GLASS_SIZE = (785, 318)
        self.glass_rect = pygame.Rect((SCREEN_WIDTH - self.GLASS_SIZE[0]) // 2, 85, self.GLASS_SIZE[0], self.GLASS_SIZE[1])

        self.create_new_visitor()

        self.current_room_index = 0
        self.current_zoom = 1.0
        self.target_zoom = 1.0
        self.focus_x = SCREEN_WIDTH / 2
        self.focus_y = SCREEN_HEIGHT / 2
        
        self.last_mouse_move_time = time.time()
        self.can_change_room = True
        self.is_manual_zooming = False
        
        self.current_time_minutes = START_HOUR * 60
        self.is_interaction_active = False

    def create_new_visitor(self):
        self.current_npc = self.generator.create_random_character()
        
        countries = ["latvia", "lithuania", "ukraine", "belarus", "kazakhistan", "turkey", "sweden", "germany"]
        birth_year = random.randint(1946, 1973)
        npc_data = {
            "name": f"Citizen-{random.randint(1000, 9999)}",
            "dob": f"{random.randint(1,28)}.{random.randint(1,12)}.{birth_year}",
            "country": random.choice(countries),
            "issue": f"12.05.{birth_year + 18}",
            "expiry": "12.05.1991",
            # FOTOĞRAF SATIRI KALDIRILDI
            # "photo": pygame.transform.scale(self.current_npc.image, (60, 80)) 
        }
        
        self.documents.clear()
        doc_id = self.doc_factory.create_id_card(npc_data)
        if doc_id: self.documents.append(doc_id)
        
        doc_entry = self.doc_factory.create_entry_permit(npc_data)
        if doc_entry: self.documents.append(doc_entry)
        
        if random.random() > 0.5:
            doc_health = self.doc_factory.create_health_report(npc_data)
            if doc_health: self.documents.append(doc_health)

    def on_enter(self):
        self.target_zoom = 1.0

    def handle_events(self, events):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: self.create_new_visitor()
                if event.key == pygame.K_l:
                    loc = self.game.loc_manager
                    new_lang = "en" if loc.current_lang == "tr" else "tr"
                    loc.load_language(new_lang)
                if event.key == pygame.K_e: self.manager.change_state("EYE_EXAM")
                if event.key == pygame.K_h: self.manager.change_state("HAND_EXAM")

            # --- ZOOM ENGELLEME ---
            # Sadece ODA 0 DEĞİLSE zoom yapmaya izin ver
            if self.current_room_index != 0:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.is_manual_zooming = True
                    self.focus_x = mouse_x
                    self.focus_y = mouse_y
                if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    self.is_manual_zooming = False
            
            if event.type == pygame.MOUSEMOTION:
                self.last_mouse_move_time = time.time()
            
            # SÜRÜKLEME
            if self.current_room_index == 0:
                for doc in reversed(self.documents):
                    if doc.update(event):
                        self.documents.remove(doc)
                        self.documents.append(doc)
                        break
            # Bed click: only when in bedroom and after END_HOUR
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                try:
                    # BED_RECT is in screen coords; only active in the bedroom room
                    if self.current_room_index == BED_ROOM_INDEX and self.current_time_minutes >= END_HOUR * 60:
                        if BED_RECT.collidepoint(event.pos):
                            # End-day action
                            self.game.day_count = getattr(self.game, 'day_count', 1) + 1
                            self.current_time_minutes = START_HOUR * 60
                            self.create_new_visitor()
                            self.current_room_index = 0
                            print(f"Day {self.game.day_count} Started")
                except Exception:
                    pass

    def update(self):
        current_time = time.time()
        
        # --- ZOOM ENGELLEME ---
        # Oda 0'da ise zoom hep 1.0 kalsın
        if self.current_room_index == 0:
            self.target_zoom = 1.0
            self.current_zoom = 1.0
        else:
            # Diğer odalarda normal zoom mantığı
            if self.is_manual_zooming:
                self.target_zoom = MANUAL_ZOOM_LEVEL
            else:
                idle = current_time - self.last_mouse_move_time
                if idle > IDLE_TIME_TRIGGER:
                    self.target_zoom = MAX_AUTO_ZOOM
                    self.focus_x = SCREEN_WIDTH / 2; self.focus_y = SCREEN_HEIGHT / 2
                else:
                    self.target_zoom = 1.0
            self.current_zoom += (self.target_zoom - self.current_zoom) * MANUAL_ZOOM_SPEED

        # Oda Değişimi (Zoom yokken)
        if self.current_zoom < 1.05:
            mouse_x, _ = pygame.mouse.get_pos()
            reset_start, reset_end = SCREEN_WIDTH / 3, (SCREEN_WIDTH / 3) * 2
            if reset_start < mouse_x < reset_end: self.can_change_room = True
            if self.can_change_room:
                if mouse_x > SCREEN_WIDTH - EDGE_THRESHOLD:
                    self.current_room_index = (self.current_room_index + 1) % 8
                    self.can_change_room = False
                elif mouse_x < EDGE_THRESHOLD:
                    self.current_room_index = (self.current_room_index - 1) % 8
                    self.can_change_room = False

        # Time progression: only advance if current time is before END_HOUR
        end_minutes = END_HOUR * 60
        if self.current_time_minutes < end_minutes:
            self.current_time_minutes += 0.05
            # clamp to end_minutes to avoid passing slightly beyond
            if self.current_time_minutes > end_minutes:
                self.current_time_minutes = end_minutes

    def draw(self):
        self.screen.fill((0, 0, 0))
        canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 1. Oda
        if self.room_images:
            canvas.blit(self.room_images[self.current_room_index], (0, 0))
            # Debug: draw bed click area when in bedroom
            try:
                if self.current_room_index == BED_ROOM_INDEX:
                    bed_overlay = pygame.Surface((int(BED_RECT.width), int(BED_RECT.height)), pygame.SRCALPHA)
                    bed_overlay.fill((200, 50, 50, 80))
                    canvas.blit(bed_overlay, (int(BED_RECT.x), int(BED_RECT.y)))
            except Exception:
                pass
        
        # 2. ODA 0 ÖZEL ÇİZİM (Karakter + Belgeler)
        if self.current_room_index == 0:
            # Karakter (Cam Arkası)
            if self.current_npc:
                glass_surf = pygame.Surface(self.GLASS_SIZE, pygame.SRCALPHA)
                glass_surf.blit(canvas, (0, 0), area=self.glass_rect)
                
                char_w, char_h = self.current_npc.image.get_size()
                local_x = (self.GLASS_SIZE[0] - char_w) // 2
                local_y = self.GLASS_SIZE[1] - char_h
                
                glass_surf.blit(self.current_npc.image, (local_x, local_y))
                
                tint = pygame.Surface(self.GLASS_SIZE, pygame.SRCALPHA)
                tint.fill((0, 20, 30, 80))
                glass_surf.blit(tint, (0,0))
                
                canvas.blit(glass_surf, self.glass_rect.topleft)

            # Belgeler
            for doc in self.documents:
                canvas.blit(doc.image, doc.rect)

        # 3. ZOOM UYGULAMA (Oda 0'da Zoom Kapalı olduğu için burası çalışsa bile 1.0 zoom yapacak)
        # Ama yine de Mac'i garantiye almak için:
        if self.current_room_index != 0 and self.current_zoom > 1.001:
            try:
                zoom = float(self.current_zoom)
                view_w = int(max(1, SCREEN_WIDTH / zoom))
                view_h = int(max(1, SCREEN_HEIGHT / zoom))
                view_x = int(self.focus_x - view_w // 2)
                view_y = int(self.focus_y - view_h // 2)
                view_x = max(0, min(view_x, SCREEN_WIDTH - view_w))
                view_y = max(0, min(view_y, SCREEN_HEIGHT - view_h))
                
                sub = canvas.subsurface((view_x, view_y, view_w, view_h)).copy()
                scaled = pygame.transform.smoothscale(sub, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.screen.blit(scaled, (0, 0))
            except:
                self.screen.blit(canvas, (0, 0))
        else:
            # Oda 0 için direkt bas (Siyah ekran riski SIFIR)
            self.screen.blit(canvas, (0, 0))

        # 4. Day / Time UI (top center)
        day = getattr(self.game, 'day_count', 1)
        h = int(self.current_time_minutes // 60)
        m = int(self.current_time_minutes % 60)
        ui_text = f"DAY {day} | {h:02}:{m:02}"

        ui_w, ui_h = 300, 40
        ui_x = (SCREEN_WIDTH - ui_w) // 2
        ui_y = 8

        # Semi-transparent background
        ui_surf = pygame.Surface((ui_w, ui_h), pygame.SRCALPHA)
        ui_surf.fill((10, 10, 10, 200))
        self.screen.blit(ui_surf, (ui_x, ui_y))
        pygame.draw.rect(self.screen, (80, 80, 80), (ui_x, ui_y, ui_w, ui_h), 2)

        # If it's past END_HOUR show blinking/red indicator
        color = FONT_COLOR_UI
        if self.current_time_minutes >= END_HOUR * 60:
            # blink every 0.5s
            if int(time.time() * 2) % 2 == 0:
                color = (200, 50, 50)
            else:
                color = FONT_COLOR_UI

        text_surf = self.font.render(ui_text, True, color)
        tx = ui_x + (ui_w - text_surf.get_width()) // 2
        ty = ui_y + (ui_h - text_surf.get_height()) // 2
        self.screen.blit(text_surf, (tx, ty))

# --- GÖZ ve EL Sınıfları (Aynı - Kopyalamadım) ---
# ... (ActionEyeState ve ActionHandState önceki kodla aynı kalabilir) ...
class ActionEyeState(BaseState):
    # Önceki kodun aynısı
    def __init__(self, manager): super().__init__(manager); self.bg = None; self.baby = None; self.front = None; self.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2); self.max_radius = 120; self.pupil_pos = (0,0); self.back_btn = pygame.Rect(50, SCREEN_HEIGHT-80, 150, 50)
    def on_enter(self):
        try: path = os.path.join(ASSET_PATH, "eyes"); self.bg = pygame.transform.scale(pygame.image.load(os.path.join(path, "eyes1_background.png")).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)); raw_baby = pygame.image.load(os.path.join(path, "eyes2_baybe.png")).convert_alpha(); target_w = 150; aspect = raw_baby.get_height()/raw_baby.get_width(); self.baby = pygame.transform.smoothscale(raw_baby, (target_w, int(target_w*aspect))); self.front = pygame.transform.scale(pygame.image.load(os.path.join(path, "eyes3_front.png")).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        except: pass
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and self.back_btn.collidepoint(e.pos): self.manager.change_state("DESK")
    def update(self):
        if not self.baby: return
        mx, my = pygame.mouse.get_pos(); cx, cy = self.center; dx, dy = mx-cx, my-cy; dist = math.hypot(dx, dy)
        if dist > self.max_radius: scale = self.max_radius/dist; dx*=scale; dy*=scale
        pw, ph = self.baby.get_size(); self.pupil_pos = (cx+dx-pw//2, cy+dy-ph//2)
    def draw(self):
        self.screen.fill((0,0,0)); 
        if self.bg: self.screen.blit(self.bg, (0,0))
        if self.baby: self.screen.blit(self.baby, self.pupil_pos)
        if self.front: self.screen.blit(self.front, (0,0))
        pygame.draw.rect(self.screen, (50,50,50), self.back_btn); self.screen.blit(self.font.render("GERİ",True,(200,200,200)), (self.back_btn.x+50, self.back_btn.y+15))

class ActionHandState(BaseState):
    # Önceki kodun aynısı
    def __init__(self, manager): super().__init__(manager); self.hands = []; self.current_hand_idx = 0; self.back_btn = pygame.Rect(50, SCREEN_HEIGHT-80, 150, 50)
    def on_enter(self):
        npc = self.manager.states["DESK"].current_npc; self.hands = []; path = os.path.join(ASSET_PATH, "hands")
        for i in range(1, 4):
            fp = os.path.join(path, f"{npc.race_code}{i}_h.png")
            if os.path.exists(fp):
                img = pygame.image.load(fp).convert_alpha(); th = int(SCREEN_HEIGHT*0.8); tw = int(th*(img.get_width()/img.get_height())); 
                if tw > SCREEN_WIDTH: tw = int(SCREEN_WIDTH*0.9); th = int(tw/(img.get_width()/img.get_height()))
                self.hands.append(pygame.transform.smoothscale(img, (tw, th)))
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.back_btn.collidepoint(e.pos): self.manager.change_state("DESK")
                elif self.hands: self.current_hand_idx = (self.current_hand_idx+1)%len(self.hands)
    def draw(self):
        self.screen.fill((15,15,20)); 
        if self.hands: h = self.hands[self.current_hand_idx]; self.screen.blit(h, ((SCREEN_WIDTH-h.get_width())//2, (SCREEN_HEIGHT-h.get_height())//2))
        pygame.draw.rect(self.screen, (50,50,50), self.back_btn); self.screen.blit(self.font.render("GERİ",True,(200,200,200)), (self.back_btn.x+50, self.back_btn.y+15))