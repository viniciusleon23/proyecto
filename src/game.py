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
        
        # Sistema de turnos
        self.current_turn = 0  # 0 = rojo, 1 = azul, 2 = verde
        self.turn_timer = 0
        self.turn_delay = 30  # Frames entre turnos
        
        # Crear mapa
        self.walls = []
        self.fires = []  # Lista de fuegos
        self.create_level()
        
        # Memoria compartida entre todos los agentes
        self.coordenadas_compartidas = set()
        
        # Posición inicial común para todos los agentes
        start_x, start_y = 60, 60
        
        # Crear agentes con la misma posición inicial y memoria compartida
        self.moving_rects = [
            MovingRect(start_x, start_y, RED, self.coordenadas_compartidas, "normal"),    # 0 = rojo
            MovingRect(start_x, start_y, BLUE, self.coordenadas_compartidas, "normal"),   # 1 = azul
            MovingRect(start_x, start_y, GREEN, self.coordenadas_compartidas, "normal")   # 2 = verde
        ]
        
    def create_level(self):
        """Creación del mapa"""
        for row_index, row in enumerate(LEVEL):
            for col_index, cell in enumerate(row):
                if cell == 1:
                    self.walls.append(Wall(col_index, row_index))
                elif cell == 2:  # Fuego nivel 1
                    self.fires.append(Fire(col_index, row_index, 1))
                elif cell == 3:  # Fuego nivel 2
                    self.fires.append(Fire(col_index, row_index, 2))
                elif cell == 4:  # Fuego nivel 3
                    self.fires.append(Fire(col_index, row_index, 3))
    
    def update(self):
        """Actualizar agentes"""
        # Verificar si todos los fuegos fueron extinguidos
        if len(self.fires) == 0:
            for agent in self.moving_rects:
                if not agent.mission_complete:
                    agent.start_mission_complete()
        
        # Verificar si el mapa está completamente explorado
        if self.is_map_fully_explored():
            for agent in self.moving_rects:
                if not agent.mission_complete and not agent.returning_to_base:
                    agent.start_mission_complete()
                    print(f"¡Mapa completamente explorado! Agente {agent.color} regresando al origen.")
        
        # Sistema de turnos
        self.turn_timer += 1
        
        if self.turn_timer >= self.turn_delay:
            self.turn_timer = 0
            
            # Actualizar movimiento solo del agente en turno
            for i, agent in enumerate(self.moving_rects):
                is_my_turn = (i == self.current_turn)
                agent.move(self.walls, self.fires, self.moving_rects, is_my_turn)
            
            # Pasar al siguiente turno
            self.current_turn = (self.current_turn + 1) % len(self.moving_rects)
    
    def is_map_fully_explored(self):
        """Verificar si el mapa está completamente explorado"""
        # Calcular total de espacios libres en el mapa
        total_free_spaces = 0
        for row in LEVEL:
            for cell in row:
                if cell == 0 or cell == 2 or cell == 3 or cell == 4:  # Espacios libres y fuegos
                    total_free_spaces += 1
        
        # Convertir a coordenadas de píxeles (cada celda es de 40x40, movimiento de 20x20)
        # Cada celda tiene 4 posiciones explorables (esquinas de 20x20)
        total_explorable_positions = total_free_spaces * 4
        
        # Verificar si ya se exploraron todas las posiciones
        explored_percentage = len(self.coordenadas_compartidas) / total_explorable_positions
        
        print(f"Exploración: {len(self.coordenadas_compartidas)}/{total_explorable_positions} ({explored_percentage:.1%})")
        
        # Considerar el mapa completamente explorado si se ha recorrido el 90% o más
        return explored_percentage >= 0.98
        
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
        
        # Dibujar fuegos
        for fire in self.fires:
            fire.draw(self.screen)
        
        # Dibujar punto de origen (base de recarga)
        origin_rect = pygame.Rect(60-10, 60-10, 40, 40)
        pygame.draw.rect(self.screen, WHITE, origin_rect, 3)
        
        # Texto "BASE" en el punto de origen
        if hasattr(pygame, 'font') and pygame.font.get_init():
            font = pygame.font.Font(None, 16)
            base_text = font.render("BASE", True, WHITE)
            self.screen.blit(base_text, (55, 45))
        
        # Dibujar agentes
        for i, rect in enumerate(self.moving_rects):
            rect.draw(self.screen)
            # Indicar el turno actual con un borde especial
            if i == self.current_turn:
                pygame.draw.rect(self.screen, WHITE, rect.rect, 1)
        
        # Mostrar información en pantalla
        if hasattr(pygame, 'font') and pygame.font.get_init():
            font = pygame.font.Font(None, 24)
            fires_text = font.render(f"Fuegos restantes: {len(self.fires)}", True, WHITE)
            self.screen.blit(fires_text, (10, 10))
            
            # Mostrar turno actual
            turn_colors = ["ROJO", "AZUL", "VERDE"]
            turn_text = font.render(f"Turno: {turn_colors[self.current_turn]}", True, WHITE)
            self.screen.blit(turn_text, (10, 35))
            
            # Mostrar unidades de cada agente
            y_offset = 60
            for i, agent in enumerate(self.moving_rects):
                color_names = ["Rojo", "Azul", "Verde"]
                agent_info = font.render(f"{color_names[i]}: {agent.fire_units} unidades", True, agent.color)
                self.screen.blit(agent_info, (10, y_offset + i * 20))
            
            # Mostrar información de exploración
            exploration_percentage = 0
            if hasattr(self, 'coordenadas_compartidas'):
                total_free_spaces = sum(1 for row in LEVEL for cell in row if cell in [0, 2, 3, 4])
                total_explorable = total_free_spaces * 4  # 4 posiciones por celda
                exploration_percentage = (len(self.coordenadas_compartidas) / total_explorable) * 100
            
            exploration_text = font.render(f"Exploración: {exploration_percentage:.1f}%", True, WHITE)
            self.screen.blit(exploration_text, (10, 120))
            
            # Mostrar si la misión está completa
            if len(self.fires) == 0:
                mission_text = font.render("¡MISION COMPLETADA!", True, GREEN)
                self.screen.blit(mission_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2))
            elif exploration_percentage >= 90:
                exploration_complete_text = font.render("¡MAPA EXPLORADO!", True, CYAN)
                self.screen.blit(exploration_complete_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 30))
        
        pygame.display.flip()
        
    def run(self):
        """Bucle principal"""
        while self.running:
            self.handle_events()
            self.update()      
            self.draw()
            self.clock.tick(60)