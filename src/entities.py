import pygame
import random

class Document(pygame.sprite.Sprite):
    def __init__(self, x, y, image_surface, doc_type_name):
        super().__init__()
        self.image = image_surface.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.doc_type = doc_type_name
        
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.offset_x = self.rect.x - event.pos[0]
                    self.offset_y = self.rect.y - event.pos[1]
                    return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] + self.offset_x
                self.rect.y = event.pos[1] + self.offset_y
        return False

class AnimatedNPC(pygame.sprite.Sprite):
    """Simple animated NPC that cycles through 3 frames."""
    def __init__(self, frames, race_code=None):
        super().__init__()
        self.frames = list(frames)
        if len(self.frames) == 0:
            raise ValueError("AnimatedNPC requires at least one frame")

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.state = "IDLE"

        # Animation timing (3 FPS)
        self.frame_duration_ms = int(1000 / 3)
        self.last_update = pygame.time.get_ticks()
        self.reaction_end_time = None

        self.race_code = race_code
        
        # --- GİZLİ ÖZELLİK: CANAVAR MI? ---
        # %30 ihtimalle canavar olsun (Raporda görmek için)
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
        else:
            if self.current_frame != 0:
                self.current_frame = 0
                self.image = self.frames[0]

    def trigger_reaction(self, reaction_type="positive"):
        """Animasyonu tetikler."""
        now = pygame.time.get_ticks()
        self.state = "TALKING"
        self.current_frame = 0
        self.image = self.frames[0]
        self.last_update = now
        self.reaction_end_time = now + self.frame_duration_ms * len(self.frames)