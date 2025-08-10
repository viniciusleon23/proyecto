from config import *
import pygame
import random

class Wall:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        
    def draw(self, screen):
        """Se dibujan las paredes"""
        pygame.draw.rect(screen, WALL_COLOR, self.rect)

class Fire:
    def __init__(self, x, y):
        # Centrar el fuego en el tile
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.animation_timer = 0
        
    def draw(self, screen):
        """Dibujar el fuego como un pixel rojo que parpadea"""
        self.animation_timer += 1
        # Hacer que parpadee cada 30 frames
        if (self.animation_timer // 30) % 2 == 0:
            pygame.draw.circle(screen, RED, (self.x, self.y), 3)
        else:
            pygame.draw.circle(screen, ORANGE, (self.x, self.y), 3)

class MovingRect:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(x, y, 20, 20)
        self.move_timer = 0
        
        # Conjunto de coordenadas visitadas (individual para cada agente)
        self.coordenadas_visitadas = set()
        
        # Posicion anterior para poder retroceder
        self.posicion_anterior = (x, y)
        
        # agreagar posicion inicial al conjunto
        self.coordenadas_visitadas.add((x, y))
        
        # Direcciones posibles
        self.direcciones = [(0, -20), (0, 20), (-20, 0), (20, 0)]  # arriba, abajo, izquierda, derecha
        
    def hay_colision(self, x, y, walls):
        """Verifica si hay colisión con paredes o límites"""
        # Verificar límites de pantalla
        if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT:
            return True
        
        # Verificar colisión con paredes
        temp_rect = pygame.Rect(x, y, 20, 20)
        for wall in walls:
            if temp_rect.colliderect(wall.rect):
                return True
        
        return False
    
    def ya_visitada(self, x, y):
        """Verifica si ya visitó esa coordenada"""
        return (x, y) in self.coordenadas_visitadas
    
    def retroceder(self):
        """Retrocede a la posición anterior"""
        self.x, self.y = self.posicion_anterior
        self.rect.x = self.x
        self.rect.y = self.y
        
    def evaluar_opciones(self, walls):
        """Evalúa las direcciones disponibles y elige la mejor"""
        opciones_validas = []
        
        for dx, dy in self.direcciones:
            nueva_x = self.x + dx
            nueva_y = self.y + dy
            
            # Verificar si es una opción válida (no colisiona y no está visitada)
            if not self.hay_colision(nueva_x, nueva_y, walls) and not self.ya_visitada(nueva_x, nueva_y):
                opciones_validas.append((dx, dy, nueva_x, nueva_y))
        
        # Si no hay opciones no visitadas, permitir ir a lugares ya visitados
        if not opciones_validas:
            for dx, dy in self.direcciones:
                nueva_x = self.x + dx
                nueva_y = self.y + dy
                
                # Solo verificar que no colisione (permitir lugares visitados)
                if not self.hay_colision(nueva_x, nueva_y, walls):
                    opciones_validas.append((dx, dy, nueva_x, nueva_y))
        
        return opciones_validas
    
    def move(self, walls):
        
        self.move_timer += 1
        
        # Moverse cada 30 frames
        if self.move_timer >= 30:
            self.move_timer = 0
            
            # Guardar posición actual como anterior
            self.posicion_anterior = (self.x, self.y)
            
            # Elegir una dirección aleatoria para intentar
            dx, dy = random.choice(self.direcciones)
            nueva_x = self.x + dx
            nueva_y = self.y + dy
            
            # Verificar si puede moverse 
            if self.hay_colision(nueva_x, nueva_y, walls) or self.ya_visitada(nueva_x, nueva_y):
                # Si hay colisión o ya visitó esa zona, retroceder y evaluar opciones
                self.retroceder()
                
                # Evaluar todas las opciones disponibles
                opciones = self.evaluar_opciones(walls)
                
                if opciones:
                    # Elegir aleatoriamente entre las opciones válidas
                    dx, dy, nueva_x, nueva_y = random.choice(opciones)
                    
                    # Moverse nueva posicion
                    self.x = nueva_x
                    self.y = nueva_y
                    self.rect.x = self.x
                    self.rect.y = self.y
                    
                    # Agregar nueva coordenada al conjunto
                    self.coordenadas_visitadas.add((nueva_x, nueva_y))
                
            else:
                # silo el movimiento valido 
                self.x = nueva_x
                self.y = nueva_y
                self.rect.x = self.x
                self.rect.y = self.y
                
                # Agregar nueva coordenada al conjunto
                self.coordenadas_visitadas.add((nueva_x, nueva_y))
    
    def draw(self, screen):
        """Dibujar el agente"""
        pygame.draw.rect(screen, self.color, self.rect)