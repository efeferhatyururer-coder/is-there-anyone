import pygame
import sys
import time
import os
import random

# --- AYARLAR ---
ASSET_PATH = "assets"  # Ana varlık klasörü

# Zoom ve Kamera Ayarları
IDLE_TIME_TRIGGER = 2.0
AUTO_ZOOM_SPEED = 0.004
MAX_AUTO_ZOOM = 1.2
MANUAL_ZOOM_LEVEL = 1.2
MANUAL_ZOOM_SPEED = 0.05
PAN_SPEED = 0.1
EDGE_THRESHOLD = 40

# --- SINIFLAR ---

class Document(pygame.sprite.Sprite):
    """Masa üzerindeki sürüklenebilir belgeler."""
    def __init__(self, x, y, w, h, color, text):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        
        # Basit yazı (Placeholder)
        font = pygame.font.SysFont("Arial", 14)
        text_surf = font.render(text, True, (0, 0, 0))
        self.image.blit(text_surf, (5, 5))
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Sol Tık
                if self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.offset_x = self.rect.x - event.pos[0]
                    self.offset_y = self.rect.y - event.pos[1]
                    return True # Tıklandı sinyali gönder

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] + self.offset_x
                self.rect.y = event.pos[1] + self.offset_y
        return False

class Character(pygame.sprite.Sprite):
    """Birleştirilmiş NPC görseli."""
    def __init__(self, layer_images, screen_w, screen_h):
        super().__init__()
        # Tüm katmanları tek bir yüzeyde birleştir
        self.image = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        
        for img in layer_images:
            # Assetleri ekran boyutuna oturt (Gerekirse scale et)
            # Senin assetlerin zaten uyumluysa (1920x1080) direkt blit yeterli
            self.image.blit(img, (0, 0))
            
        self.rect = self.image.get_rect()

class CharacterGenerator:
    """Dosya sistemini tarayıp rastgele karakter üreten sınıf."""
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.parts = {
            "heads": [], "torsos": [], "hands": [],
            "eyes": [], "noses": [], "mouths": [],
            "teeth": [], "anomalies": []
        }
        self.load_all_assets()

    def load_all_assets(self):
        print("Assetler yükleniyor...")
        self.scan_folder("heads", "heads")
        self.scan_folder("torsos", "torsos")
        self.scan_fashion_products()
        print("Karakter veritabanı hazır.")

    def scan_folder(self, folder_name, dict_key):
        path = os.path.join(ASSET_PATH, folder_name)
        if not os.path.exists(path): return

        for filename in os.listdir(path):
            if not filename.endswith(".png"): continue
            
            code = filename.split("_")[0] # bm1, ww12 vb.
            full_path = os.path.join(path, filename)
            
            try:
                img = pygame.image.load(full_path).convert_alpha()
                # Ekran boyutuna ölçekle (Assetler küçükse)
                img = pygame.transform.scale(img, (self.screen_w, self.screen_h))
                
                self.parts[dict_key].append({
                    "code": code, "image": img, "filename": filename
                })
            except Exception as e:
                print(f"Hata yüklenirken: {filename} - {e}")

    def scan_fashion_products(self):
        path = os.path.join(ASSET_PATH, "fashion product")
        if not os.path.exists(path): return

        for filename in os.listdir(path):
            if not filename.endswith(".png"): continue
            
            parts = filename.split("_")
            prefix = parts[0]
            suffix = parts[-1].replace(".png", "")
            
            full_path = os.path.join(path, filename)
            img = pygame.image.load(full_path).convert_alpha()
            img = pygame.transform.scale(img, (self.screen_w, self.screen_h))
            
            entry = {"code": prefix, "image": img, "filename": filename}

            if suffix == "e": self.parts["eyes"].append(entry)
            elif "nose" in filename: self.parts["noses"].append(entry)
            elif "mouth" in filename: self.parts["mouths"].append(entry)
            elif "teeth" in filename: self.parts["teeth"].append(entry)
            elif suffix.startswith("a"): self.parts["anomalies"].append(entry)

    def create_random_character(self):
        races = ["bm", "wm", "bw", "ww"]
        chosen_race = random.choice(races)
        chosen_variant = str(random.randint(1, 3))
        
        print(f"Yeni NPC Oluşturuldu: {chosen_race}{chosen_variant}")

        char_sprites = []

        # --- KATMANLAMA MANTIĞI (TORSO -> NOSE) ---
        
        # 1. TORSO
        torso = self.find_compatible_part(self.parts["torsos"], chosen_race, chosen_variant)
        if torso: char_sprites.append(torso)

        # 2. HEAD
        head = self.find_compatible_part(self.parts["heads"], chosen_race, chosen_variant)
        if head: char_sprites.append(head)

        # 3. EYES
        eye_state = random.choice(["n", "s", "ti"])
        eyes = self.find_compatible_face(self.parts["eyes"], chosen_race, chosen_variant, eye_state)
        if eyes: char_sprites.append(eyes)

        # 4. MOUTH
        mouth = self.find_compatible_face(self.parts["mouths"], chosen_race, chosen_variant)
        if mouth: char_sprites.append(mouth)

        # 5. ANOMALY
        if random.random() < 0.3:
            anomaly = self.find_compatible_anomaly(self.parts["anomalies"], chosen_race)
            if anomaly: char_sprites.append(anomaly)

        # 6. NOSE (EN ÜSTTE - İstediğin Gibi)
        nose = self.find_compatible_face(self.parts["noses"], chosen_race, chosen_variant)
        if nose: char_sprites.append(nose)

        return Character(char_sprites, self.screen_w, self.screen_h)

    def find_compatible_part(self, part_list, race, variant):
        candidates = []
        for part in part_list:
            code = part['code']
            if code.startswith(race):
                nums = code.replace(race, "").replace("_t", "") # bm12_t -> 12
                if variant in nums:
                    candidates.append(part['image'])
        if candidates: return random.choice(candidates)
        return None

    def find_compatible_face(self, part_list, race, variant, state=""):
        candidates = []
        for part in part_list:
            code = part['code']
            if not code.startswith(race): continue
            if state and state not in code: continue 
            
            nums = ''.join(filter(str.isdigit, code))
            if variant in nums:
                candidates.append(part['image'])
        if candidates: return random.choice(candidates)
        return None

    def find_compatible_anomaly(self, part_list, race):
        candidates = []
        for part in part_list:
            if part['code'].startswith(race):
                candidates.append(part['image'])
        if candidates: return random.choice(candidates)
        return None


# --- ANA UYGULAMA ---

pygame.init()
pygame.mixer.init()

# Tam Ekran Başlat
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Is There Anyone? - Integrated")
clock = pygame.time.Clock()

# --- VARLIKLARI YÜKLE ---

# 1. Odalar
room_images = []
for i in range(8):
    # assets/rooms klasörüne bakıyoruz (Son yapıya göre)
    path = os.path.join(ASSET_PATH, "rooms", f"room_{i}.png")
    try:
        img = pygame.image.load(path).convert()
        img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        room_images.append(img)
    except FileNotFoundError:
        # Eğer rooms klasörü yoksa ana klasöre bak (Yedek)
        try:
            path_bkp = os.path.join(ASSET_PATH, f"room_{i}.png")
            img = pygame.image.load(path_bkp).convert()
            img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            room_images.append(img)
        except:
            print(f"Uyarı: room_{i}.png bulunamadı. Siyah ekran.")
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            room_images.append(s)

# 2. Karakter Üretici
generator = CharacterGenerator(SCREEN_WIDTH, SCREEN_HEIGHT)
current_npc = generator.create_random_character()

# 3. Belgeler (Örnek)
documents = []
doc1 = Document(400, 300, 200, 300, (200, 200, 180), "ID Card")
doc2 = Document(650, 400, 250, 150, (220, 220, 100), "Entry Permit")
documents.append(doc1)
documents.append(doc2)


# --- OYUN DEĞİŞKENLERİ ---
current_room_index = 0
current_zoom = 1.0
target_zoom = 1.0
current_center = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]
target_center = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]

last_mouse_move_time = time.time()
can_change_room = True
is_tool_active = False
is_manual_zooming = False

# --- DÖNGÜ ---
running = True
while running:
    current_time = time.time()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # --- A) EVENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            
            # TEST: 'SPACE' tuşuna basınca yeni karakter gelsin
            if event.key == pygame.K_SPACE:
                current_npc = generator.create_random_character()

        if event.type == pygame.MOUSEMOTION:
            last_mouse_move_time = current_time
            
        # SAĞ TIK ZOOM
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            is_manual_zooming = True
            if mouse_x < SCREEN_WIDTH / 2: target_x = SCREEN_WIDTH / 4
            else: target_x = (SCREEN_WIDTH / 4) * 3
            if mouse_y < SCREEN_HEIGHT / 2: target_y = SCREEN_HEIGHT / 4
            else: target_y = (SCREEN_HEIGHT / 4) * 3
            target_center = [target_x, target_y]
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            is_manual_zooming = False
            target_center = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]

        # BELGE SÜRÜKLEME (Sadece Room 0)
        if current_room_index == 0:
            for doc in reversed(documents):
                clicked = doc.update(event)
                if clicked:
                    documents.remove(doc)
                    documents.append(doc)
                    break

    # --- B) MANTIK ---
    
    # Zoom Hedefleme
    if is_tool_active and current_room_index == 0: target_zoom = 1.0
    elif is_manual_zooming: target_zoom = MANUAL_ZOOM_LEVEL
    else:
        idle_duration = current_time - last_mouse_move_time
        if idle_duration > IDLE_TIME_TRIGGER:
            target_zoom = MAX_AUTO_ZOOM
            target_center = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]
        else:
            target_zoom = 1.0
            target_center = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]

    # Zoom Animasyonu
    current_zoom += (target_zoom - current_zoom) * MANUAL_ZOOM_SPEED
    current_center[0] += (target_center[0] - current_center[0]) * PAN_SPEED
    current_center[1] += (target_center[1] - current_center[1]) * PAN_SPEED

    # Oda Değiştirme
    is_locked = (current_zoom > 1.01) or (is_tool_active and current_room_index == 0)
    if not is_locked:
        reset_start, reset_end = SCREEN_WIDTH / 3, (SCREEN_WIDTH / 3) * 2
        if reset_start < mouse_x < reset_end: can_change_room = True
        
        if can_change_room:
            if mouse_x > SCREEN_WIDTH - EDGE_THRESHOLD:
                current_room_index = (current_room_index + 1) % 8
                can_change_room = False
            elif mouse_x < EDGE_THRESHOLD:
                current_room_index = (current_room_index - 1) % 8
                can_change_room = False

    # --- C) RENDER ---
    screen.fill((0, 0, 0))
    
    # 1. Base Layer: ODA
    current_room_img = room_images[current_room_index]
    
    # Zoom için Surface oluşturma mantığı yerine direkt büyük surface'a her şeyi çizip
    # en son onu crop'layıp ekrana basmak daha tutarlı bir POV sağlar.
    # Ancak performans için şu anki "parçalı çizim" de çalışır.
    
    # Kameranın gördüğü her şeyi geçici bir Surface'a çizelim (CANVAS)
    # Bu sayede Zoom yaptığımızda NPC ve Belgeler de odayla birlikte zoomlanır.
    # Canvas boyutu ekran ile aynı olsun.
    world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    world_surface.blit(current_room_img, (0, 0))
    
    # 2. Layer: NPC (Sadece Room 0)
    if current_room_index == 0:
        world_surface.blit(current_npc.image, (0, 0))
    
    # 3. Layer: Belgeler (Sadece Room 0)
    if current_room_index == 0:
        for doc in documents:
            world_surface.blit(doc.image, doc.rect)

    # --- ZOOM & CROP İŞLEMİ (World Surface üzerinden) ---
    view_width = SCREEN_WIDTH / current_zoom
    view_height = SCREEN_HEIGHT / current_zoom
    view_x = max(0, min(current_center[0] - view_width/2, SCREEN_WIDTH - view_width))
    view_y = max(0, min(current_center[1] - view_height/2, SCREEN_HEIGHT - view_height))
    
    view_rect = pygame.Rect(view_x, view_y, view_width, view_height)
    
    try:
        subsurface = world_surface.subsurface(view_rect)
        scaled_surface = pygame.transform.scale(subsurface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_surface, (0, 0))
    except:
        screen.blit(world_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()