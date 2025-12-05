import pygame
import os
import random

from src.settings import ASSET_PATH, CHAR_SCALE_HEIGHT
from src.entities import AnimatedNPC


class CharacterLoader:
    """Loads vertical spritesheet characters from `assets/characters/`.

    Expects files named like `char_1.png` … `char_4.png` with 3 vertical frames.
    """
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.char_dir = os.path.join(ASSET_PATH, "characters")

    def create_random_character(self):
        """Pick a random spritesheet, slice into 3 frames, scale each frame and
        return an AnimatedNPC initialized with the frames.
        """
        if not os.path.exists(self.char_dir):
            print(f"HATA: Karakter klasörü bulunamadı: {self.char_dir}")
            raise FileNotFoundError(f"Characters folder not found: {self.char_dir}")

        # DÜZELTME: Dosya isimlerini 'char_' olarak değiştirdiysen burası çalışır.
        files = [f for f in os.listdir(self.char_dir) if f.lower().endswith('.png') and f.startswith('char_')]
        
        if not files:
            print(f"HATA: '{self.char_dir}' içinde 'char_' ile başlayan PNG bulunamadı!")
            raise FileNotFoundError(f"No character spritesheets found in {self.char_dir}")

        chosen = random.choice(files)
        full_path = os.path.join(self.char_dir, chosen)

        try:
            img = pygame.image.load(full_path).convert_alpha()
        except Exception as e:
            print(f"HATA: Resim dosyası bozuk veya açılamadı: {full_path}")
            raise e

        # DİKEY KESİM (VERTICAL SLICING)
        total_h = img.get_height()
        frame_h = total_h // 3 
        
        frames = []
        for i in range(3):
            rect = pygame.Rect(0, i * frame_h, img.get_width(), frame_h)
            
            try:
                frame = img.subsurface(rect).copy()
                
                # ÖLÇEKLENDİRME
                target_h = CHAR_SCALE_HEIGHT
                aspect = frame.get_width() / frame.get_height()
                target_w = max(1, int(target_h * aspect))
                
                frame_scaled = pygame.transform.smoothscale(frame, (target_w, target_h))
                frames.append(frame_scaled)
            except Exception as e:
                print(f"HATA: Kare kesilirken sorun oluştu: {e}")
                raise e

        race_code = os.path.splitext(chosen)[0]
        return AnimatedNPC(frames, race_code=race_code)