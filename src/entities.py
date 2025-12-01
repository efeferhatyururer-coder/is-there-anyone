import pygame

class Document(pygame.sprite.Sprite):
    def __init__(self, x, y, image_surface, doc_type_name):
        super().__init__()
        self.image = image_surface
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

class Character(pygame.sprite.Sprite):
    def __init__(self, layer_images, w, h, race_code):
        super().__init__()
        self.race_code = race_code
        
        # Sadece resmi oluştur, üzerine GÖLGE ATMA (Cam efekti states.py'da yapılacak)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        
        for img in layer_images:
            # Görseller zaten generator'da scale edildi, burada direkt basıyoruz
            # Ortalamak için basit bir matematik (Eğer görsel yüzeyden küçükse)
            bx = (w - img.get_width()) // 2
            by = (h - img.get_height()) // 2
            self.image.blit(img, (bx, by))
            
        self.rect = self.image.get_rect()