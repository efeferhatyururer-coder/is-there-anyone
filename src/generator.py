import pygame
import os
import random
from src.settings import ASSET_PATH, CHAR_SCALE_HEIGHT # ARTIK WIDTH YOK, SADECE HEIGHT
from src.entities import Character

class CharacterGenerator:
    """Dosya sistemini tarayıp rastgele karakter üreten sınıf."""
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        # Asset listeleri
        self.parts = {
            "heads": [], "torsos": [], "hands": [],
            "eyes": [], "noses": [], "mouths": [],
            "teeth": [], "anomalies": []
        }
        self.load_all_assets()

    def load_all_assets(self):
        print("Assetler yükleniyor...")
        # Yüklerken scale etmiyoruz, orijinal boyut kalsın
        self.scan_folder("heads", "heads")
        self.scan_folder("torsos", "torsos")
        self.scan_folder("hands", "hands") 
        self.scan_fashion_products()
        print("Karakter veritabanı hazır.")

    def scan_folder(self, folder_name, dict_key):
        path = os.path.join(ASSET_PATH, folder_name)
        if not os.path.exists(path): return

        for filename in os.listdir(path):
            if not filename.endswith(".png"): continue
            
            # Dosya adının tamamını kod olarak al (örn: bmo1)
            code = filename.split("_")[0]
            full_path = os.path.join(path, filename)
            
            try:
                img = pygame.image.load(full_path).convert_alpha()
                self.parts[dict_key].append({"code": code, "image": img, "filename": filename})
            except Exception as e:
                print(f"Hata: {filename} - {e}")

    def scan_fashion_products(self):
        path = os.path.join(ASSET_PATH, "fp")
        if not os.path.exists(path): path = os.path.join(ASSET_PATH, "fashion product")
        if not os.path.exists(path): return

        for filename in os.listdir(path):
            if not filename.endswith(".png"): continue
            
            parts = filename.split("_")
            prefix = parts[0]
            suffix = parts[-1].replace(".png", "")
            full_path = os.path.join(path, filename)
            
            try:
                img = pygame.image.load(full_path).convert_alpha()
                entry = {"code": prefix, "image": img, "filename": filename}

                if suffix == "e": self.parts["eyes"].append(entry)
                elif "nose" in filename: self.parts["noses"].append(entry)
                elif "mouth" in filename: self.parts["mouths"].append(entry)
                elif "teeth" in filename: self.parts["teeth"].append(entry)
                elif suffix.startswith("a"): self.parts["anomalies"].append(entry)
            except: pass

    def create_random_character(self):
        races = ["bm", "wm", "bw", "ww"]
        chosen_race = random.choice(races)
        chosen_variant = str(random.randint(1, 3))
        
        # Parça bulucu
        def get_part(part_list):
            return self.find_compatible_part_raw(part_list, chosen_race, chosen_variant)
        def get_face(part_list, state=""):
            return self.find_compatible_face_raw(part_list, chosen_race, chosen_variant, state)
        
        torso = get_part(self.parts["torsos"])
        head = get_part(self.parts["heads"])
        
        eye_state = random.choice(["n", "s", "ti"])
        eyes = get_face(self.parts["eyes"], eye_state)
        nose = get_face(self.parts["noses"])
        mouth = get_face(self.parts["mouths"])
        
        anomaly = None
        if random.random() < 0.10: 
            anomaly = self.find_compatible_anomaly(self.parts["anomalies"], chosen_race)

        # Fallback (Eğer parça bulunamazsa boş oluştur)
        if not torso: 
            return Character([pygame.Surface((100,100))], 100, 100, chosen_race)

        base_w, base_h = torso.get_width(), torso.get_height()
        composite = pygame.Surface((base_w, base_h), pygame.SRCALPHA)

        # Hepsini (0,0) noktasına üst üste bindir (Pre-positioned asset mantığı)
        composite.blit(torso, (0, 0))
        if head: composite.blit(head, (0, 0))
        if eyes: composite.blit(eyes, (0, 0))
        if nose: composite.blit(nose, (0, 0))
        if mouth: composite.blit(mouth, (0, 0))
        if anomaly: composite.blit(anomaly, (0, 0))

        # --- ORANTILI SCALE İŞLEMİ ---
        # Genişlik ayarı yok, yüksekliğe göre genişliği biz buluyoruz.
        target_h = CHAR_SCALE_HEIGHT # 500px (Settings'den geliyor)
        aspect_ratio = base_w / base_h
        target_w = int(target_h * aspect_ratio) # Genişliği orantılı hesapla
        
        final_char = pygame.transform.smoothscale(composite, (target_w, target_h))

        return Character([final_char], target_w, target_h, chosen_race)

    def find_compatible_part_raw(self, part_list, race, variant):
        # Varyant eşleşmesi (bmo1 -> bmo1)
        candidates = []
        for p in part_list:
            p_code = p['code']
            # Basit eşleşme kontrolü:
            if p_code.startswith(race) and (variant in p_code):
                 candidates.append(p['image'])
        
        return random.choice(candidates) if candidates else None

    def find_compatible_face_raw(self, part_list, race, variant, state=""):
        candidates = []
        for p in part_list:
            if not p['code'].startswith(race): continue
            if state and state not in p['code']: continue
            if variant in p['code']: 
                candidates.append(p['image'])
        return random.choice(candidates) if candidates else None

    def find_compatible_anomaly(self, part_list, race):
        candidates = [p['image'] for p in part_list if p['code'].startswith(race)]
        return random.choice(candidates) if candidates else None