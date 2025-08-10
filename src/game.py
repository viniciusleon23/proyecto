import pygame
import sys
from config import *
from sprites import *


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ContraFuegos")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Crear mapa
        self.walls = []
        self.create_level()
        
        # Posición inicial común para todos los agentes
        start_x, start_y = 60, 60  # Puedes cambiar estos valores
        
        # Crear agentes con la misma posición inicial
        self.moving_rects = [
            MovingRect(start_x, start_y, YELLOW),
            MovingRect(start_x, start_y, BLUE), 
            MovingRect(start_x, start_y, GREEN)
        ]
        
    def create_level(self):
        """Creación del mapa"""
        for row_index, row in enumerate(LEVEL):
            for col_index, cell in enumerate(row):
                if cell == 1:
                    self.walls.append(Wall(col_index, row_index))
    
    def update(self):
        """Actualizar agentes"""
        for rect in self.moving_rects:
            rect.move(self.walls)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
    def draw(self):
        """Dibujar todo"""
        self.screen.fill(BLACK)
        
        # Dibujar paredes
        for wall in self.walls:
            wall.draw(self.screen)
        
        # Dibujar agentes
        for rect in self.moving_rects:
            rect.draw(self.screen)
        
        pygame.display.flip()
        
    def run(self):
        """Bucle principal"""
        while self.running:
            self.handle_events()
            self.update()      
            self.draw()
            self.clock.tick(60)