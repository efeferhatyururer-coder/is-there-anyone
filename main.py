import pygame
import sys
from src.settings import *
from src.localization import LocalizationManager
from src.states import GameStateManager, DeskState, ActionEyeState, ActionHandState

class Game:
    def __init__(self):
        pygame.init()
        # Mac için 1280x720 sabit
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Is There Anyone? - Full State Machine")
        self.clock = pygame.time.Clock()
        
        # Dil Yöneticisi
        self.loc_manager = LocalizationManager("tr")
        
        # State Yöneticisi
        self.state_manager = GameStateManager(self)
        
        # State'leri Yükle
        self.state_manager.add_state("DESK", DeskState(self.state_manager))
        self.state_manager.add_state("EYE_EXAM", ActionEyeState(self.state_manager))
        self.state_manager.add_state("HAND_EXAM", ActionHandState(self.state_manager))
        
        # Başlangıç State'i
        self.state_manager.change_state("DESK")
        # Persistent day counter across states
        self.day_count = 1

    def run(self):
        running = True
        while running:
            # Global Event Handling (Quit vs)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            # Aktif State'e eventleri ve update'i gönder
            if self.state_manager.current_state:
                self.state_manager.current_state.handle_events(events)
                self.state_manager.current_state.update()
                self.state_manager.current_state.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = Game()
    app.run()