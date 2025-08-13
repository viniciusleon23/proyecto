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
    def __init__(self, x, y, level):
        # Centrar el fuego en el tile
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.level = level  # Nivel del fuego (1, 2, o 3)
        self.animation_timer = 0
        
    def draw(self, screen):
        """Dibujar el fuego según su nivel"""
        self.animation_timer += 1
        
        if self.level == 1:
            # Fuego nivel 1: rojo/naranja pequeño
            if (self.animation_timer // 30) % 2 == 0:
                pygame.draw.circle(screen, RED, (self.x, self.y), 3)
            else:
                pygame.draw.circle(screen, ORANGE, (self.x, self.y), 3)
        
        elif self.level == 2:
            # Fuego nivel 2: amarillo/naranja mediano
            if (self.animation_timer // 20) % 2 == 0:
                pygame.draw.circle(screen, YELLOW, (self.x, self.y), 5)
            else:
                pygame.draw.circle(screen, ORANGE, (self.x, self.y), 5)
        
        elif self.level == 3:
            # Fuego nivel 3: morado/rojo grande (peligroso)
            if (self.animation_timer // 15) % 2 == 0:
                pygame.draw.circle(screen, PURPLE, (self.x, self.y), 7)
                # Halo exterior para mostrar peligro
                pygame.draw.circle(screen, RED, (self.x, self.y), 10, 2)
            else:
                pygame.draw.circle(screen, RED, (self.x, self.y), 7)
                pygame.draw.circle(screen, PURPLE, (self.x, self.y), 10, 2)

class MovingRect:
    def __init__(self, x, y, color, coordenadas_compartidas, agent_type="normal"):
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(x, y, 20, 20)
        self.move_timer = 0
        self.agent_type = agent_type  # "normal" o "support"
        
        # Punto de inicio para recargar
        self.origin_x = x
        self.origin_y = y
        
        # Sistema de unidades
        self.fire_units = 3  # Unidades para apagar fuego
        self.max_units = 3
        self.returning_to_base = False  # Si está regresando a recargar
        
        # Sistema de seguimiento de ruta (backtracking)
        self.path_history = [(x, y)]  # Historial de posiciones visitadas por ESTE agente
        self.return_path = []  # Ruta de regreso al origen
        self.following_return_path = False  # Si está siguiendo la ruta de regreso
        
        # Referencia a las coordenadas compartidas entre todos los agentes
        self.coordenadas_visitadas = coordenadas_compartidas
        
        # Posicion anterior para poder retroceder
        self.posicion_anterior = (x, y)
        
        # agreagar posicion inicial al conjunto compartido
        self.coordenadas_visitadas.add((x, y))
        
        # Direcciones posibles
        self.direcciones = [(0, -20), (0, 20), (-20, 0), (20, 0)]  # arriba, abajo, izquierda, derecha
        
        # Sistema para llamar apoyo
        self.support_needed = False  # Si necesita apoyo
        self.support_location = None  # Ubicación donde necesita apoyo
        self.waiting_for_support = False  # Si está esperando apoyo
        self.helping_another = False  # Si está ayudando a otro agente
        self.target_fire_location = None  # Ubicación del fuego al que se dirige
        
        # Estado de misión
        self.mission_complete = False  # Si la misión terminó
        
    def can_extinguish_fire(self, fire):
        """Verificar si puede extinguir el fuego según su tipo y unidades disponibles"""
        if self.agent_type == "normal":
            return fire.level <= 2 and self.fire_units >= fire.level  # Agentes normales: solo fuegos nivel 1 y 2
        elif self.agent_type == "support":
            return fire.level <= 3 and self.fire_units >= fire.level  # Agentes de apoyo: todos los fuegos
        return False
    
    def count_nearby_agents_with_units(self, all_agents):
        """Contar cuántos agentes con unidades están cerca (incluyéndose a sí mismo)"""
        nearby_agents = 0
        total_units = 0
        
        for agent in all_agents:
            if agent.fire_units > 0:  # Solo contar agentes con unidades
                distance = ((self.x - agent.x) ** 2 + (self.y - agent.y) ** 2) ** 0.5
                if distance < 50:  # Si está a menos de 50 pixeles
                    nearby_agents += 1
                    total_units += agent.fire_units
        
        return nearby_agents, total_units
    
    def request_multiple_support(self, fire_location, fire_level, all_agents):
        """Solicitar múltiples agentes según el nivel del fuego y unidades disponibles"""
        nearby_count, total_units = self.count_nearby_agents_with_units(all_agents)
        
        print(f"Fuego nivel {fire_level}: {nearby_count} agentes cerca con {total_units} unidades totales")
        
        if total_units >= fire_level:
            # Ya hay suficientes unidades cerca
            return True
        
        # Necesita más apoyo - solicitar a agentes disponibles
        agents_needed = fire_level - total_units
        agents_called = 0
        
        for agent in all_agents:
            if (agent != self and 
                agent.fire_units > 0 and 
                not agent.helping_another and 
                not agent.waiting_for_support and
                not agent.returning_to_base and
                agents_called < agents_needed):
                
                # Calcular distancia
                distance = ((self.x - agent.x) ** 2 + (self.y - agent.y) ** 2) ** 0.5
                if distance >= 50:  # No está cerca, necesita venir
                    agent.helping_another = True
                    agent.target_fire_location = fire_location
                    agents_called += 1
                    print(f"Llamando a agente {agent.color} para apoyo en fuego nivel {fire_level}")
        
        if agents_called > 0:
            self.support_needed = True
            self.support_location = fire_location
            self.waiting_for_support = True
            return False
        else:
            print(f"No hay más agentes disponibles para ayudar")
            return False
    
    def start_return_to_base(self):
        """Iniciar el regreso a la base siguiendo la ruta de vuelta"""
        self.returning_to_base = True
        self.following_return_path = True
        
        # Crear ruta de regreso invirtiendo el historial
        self.return_path = self.path_history[:-1]  # Excluir posición actual
        self.return_path.reverse()  # Invertir para ir de vuelta
        
        print(f"Agente {self.color} sin unidades! Historial completo: {self.path_history}")
        print(f"Agente {self.color} creó ruta de regreso: {self.return_path}")
        print(f"Pasos para regresar: {len(self.return_path)}")
        
        # Debug: verificar si el agente tiene una ruta válida
        if not self.return_path:
            print(f"ERROR: Agente {self.color} no tiene ruta de regreso. Usando método directo.")
            self.following_return_path = False
    
    def recharge_units(self):
        """Recargar unidades en la base"""
        if self.is_at_base():
            self.fire_units = self.max_units
            self.returning_to_base = False
            self.following_return_path = False
            self.return_path = []
            
            # Reiniciar historial desde el origen
            self.path_history = [(self.origin_x, self.origin_y)]
            
            print(f"Agente {self.color} recargó unidades. Reiniciando exploración desde origen.")
    
    def follow_return_path(self, walls):
        """Seguir la ruta de regreso paso a paso, pero esquivar obstáculos"""
        if not self.return_path:
            # Ya llegó al origen o no hay ruta
            self.following_return_path = False
            print(f"Agente {self.color} terminó ruta de regreso")
            return True
            
        # Tomar el siguiente paso de la ruta de regreso
        next_x, next_y = self.return_path[0]  # No hacer pop aún
        
        print(f"Agente {self.color} intentando ir de ({self.x}, {self.y}) a ({next_x}, {next_y})")
        
        # Verificar si puede ir al siguiente paso
        temp_rect = pygame.Rect(next_x, next_y, 20, 20)
        can_move = True
        
        # Verificar colisión con paredes
        for wall in walls:
            if temp_rect.colliderect(wall.rect):
                can_move = False
                break
        
        # Verificar límites de pantalla
        if next_x < 0 or next_x >= SCREEN_WIDTH or next_y < 0 or next_y >= SCREEN_HEIGHT:
            can_move = False
        
        if can_move:
            # Puede seguir la ruta original
            self.return_path.pop(0)  # Quitar este paso de la lista
            self.x = next_x
            self.y = next_y
            self.rect.x = self.x
            self.rect.y = self.y
            print(f"✓ Agente {self.color} siguió ruta: ({next_x}, {next_y}) - {len(self.return_path)} pasos restantes")
        else:
            # El paso está bloqueado, intentar esquivar hacia la base
            print(f"⚠ Obstáculo en ruta! Agente {self.color} esquivando...")
            moved = self.move_towards_base(walls)
            if not moved:
                # Si no puede esquivar, cambiar a método directo
                self.following_return_path = False
                print(f"Agente {self.color} abandonando ruta, usando método directo")
        
        return len(self.return_path) == 0  # True si completó la ruta
    
    def start_mission_complete(self):
        """Iniciar regreso al inicio porque la misión terminó"""
        self.mission_complete = True
        self.start_return_to_base()  # Usar la ruta de regreso también para misión completa
        self.helping_another = False
        self.waiting_for_support = False
        self.support_needed = False
        print(f"Agente {self.color}: ¡Misión completada! Regresando a base por ruta de vuelta.")
    
    def record_position(self, x, y):
        """Registrar nueva posición en el historial del agente"""
        self.path_history.append((x, y))
    
    def get_direction_to_base(self):
        """Obtener dirección hacia la base evitando obstáculos"""
        dx = self.origin_x - self.x
        dy = self.origin_y - self.y
        
        # Crear lista de direcciones priorizando la más directa
        directions_to_try = []
        
        # Priorizar dirección principal
        if abs(dx) > abs(dy):
            # Moverse horizontalmente es prioritario
            main_dir = (20 if dx > 0 else -20, 0)
            secondary_dir = (0, 20 if dy > 0 else -20)
        else:
            # Moverse verticalmente es prioritario  
            main_dir = (0, 20 if dy > 0 else -20)
            secondary_dir = (20 if dx > 0 else -20, 0)
        
        directions_to_try.append(main_dir)
        if secondary_dir != (0, 0):
            directions_to_try.append(secondary_dir)
        
        # Agregar direcciones alternativas si las principales fallan
        for direction in self.direcciones:
            if direction not in directions_to_try:
                directions_to_try.append(direction)
        
        return directions_to_try
    
    def move_towards_base(self, walls):
        """Moverse hacia la base esquivando obstáculos"""
        directions_to_try = self.get_direction_to_base()
        
        for dx, dy in directions_to_try:
            nueva_x = self.x + dx
            nueva_y = self.y + dy
            
            # Si esta dirección no tiene colisión, moverse ahí
            if not self.hay_colision(nueva_x, nueva_y, walls):
                self.x = nueva_x
                self.y = nueva_y
                self.rect.x = self.x
                self.rect.y = self.y
                
                print(f"Agente {self.color} esquivando hacia base: ({nueva_x}, {nueva_y})")
                return True
        
        # Si no puede moverse en ninguna dirección, está bloqueado
        print(f"Agente {self.color} completamente bloqueado camino a base")
        return False
    
    def is_at_base(self):
        """Verificar si está en la base (punto de inicio)"""
        return abs(self.x - self.origin_x) < 15 and abs(self.y - self.origin_y) < 15
    
    def request_support(self, fire_location, all_agents):
        """Solicitar al agente más cercano que venga a ayudar"""
        self.support_needed = True
        self.support_location = fire_location
        self.waiting_for_support = True
        
        # Encontrar el agente más cercano que no esté ocupado
        closest_agent = None
        min_distance = float('inf')
        
        for agent in all_agents:
            if agent != self and not agent.helping_another and not agent.waiting_for_support:
                distance = ((self.x - agent.x) ** 2 + (self.y - agent.y) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_agent = agent
        
        if closest_agent:
            closest_agent.helping_another = True
            closest_agent.target_fire_location = fire_location  # Ir directo al fuego
            print(f"Agente {self.color} solicita apoyo. Agente {closest_agent.color} va directo al fuego.")
    
    def find_nearby_fire(self, fires):
        """Buscar fuegos cercanos que pueda manejar"""
        for fire in fires:
            # Verificar si está cerca del fuego
            distance = ((self.x + 10) - fire.x) ** 2 + ((self.y + 10) - fire.y) ** 2
            if distance < 400:  # Aproximadamente 20 pixeles
                return fire
        return None
        
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
        """Evalúa las direcciones disponibles y prioriza las NO visitadas"""
        opciones_no_visitadas = []
        opciones_visitadas = []
        
        for dx, dy in self.direcciones:
            nueva_x = self.x + dx
            nueva_y = self.y + dy
            
            # Verificar si NO hay colisión con paredes o límites
            if not self.hay_colision(nueva_x, nueva_y, walls):
                # Separar entre visitadas y no visitadas
                if not self.ya_visitada(nueva_x, nueva_y):
                    opciones_no_visitadas.append((dx, dy, nueva_x, nueva_y))
                else:
                    opciones_visitadas.append((dx, dy, nueva_x, nueva_y))
        
        # PRIORIDAD: Devolver opciones NO visitadas si existen
        if opciones_no_visitadas:
            return opciones_no_visitadas
        
        # FALLBACK: Si todas están visitadas, devolver las visitadas como opción
        return opciones_visitadas
    
    def move(self, walls, fires, all_agents, is_my_turn):
        
        # Solo moverse en su turno
        if not is_my_turn:
            return
            
        # Moverse inmediatamente cuando es su turno (sin esperar 30 frames)
        # Guardar posición actual como anterior
        self.posicion_anterior = (self.x, self.y)
        
        # PRIORIDAD MÁXIMA: Si está en la base, recargar unidades
        if self.is_at_base() and (self.fire_units < self.max_units or self.mission_complete):
            if not self.mission_complete:
                self.recharge_units()
            return
        
        # PRIORIDAD 1: Si está siguiendo ruta de regreso
        if self.following_return_path:
            print(f"DEBUG: Agente {self.color} está siguiendo ruta de regreso")
            arrived = self.follow_return_path(walls)
            if arrived:
                print(f"Agente {self.color} llegó al origen por ruta de regreso")
            return
        
        # PRIORIDAD 2: Si está regresando a la base (método directo con esquiva)
        if self.returning_to_base and not self.following_return_path:
            print(f"DEBUG: Agente {self.color} regresando por método directo")
            moved = self.move_towards_base(walls)
            if not moved:
                print(f"Agente {self.color} completamente bloqueado - esperando")
            return
        
        # PRIORIDAD 2: Si está ayudando, ir directo a las coordenadas del fuego
        if self.helping_another and self.target_fire_location:
            target_x, target_y = self.target_fire_location
            
            dx = target_x - self.x
            dy = target_y - self.y
            
            # Normalizar movimiento
            if abs(dx) > abs(dy):
                move_x = 20 if dx > 0 else -20
                move_y = 0
            else:
                move_x = 0
                move_y = 20 if dy > 0 else -20
            
            nueva_x = self.x + move_x
            nueva_y = self.y + move_y
            
            if not self.hay_colision(nueva_x, nueva_y, walls):
                self.x = nueva_x
                self.y = nueva_y
                self.rect.x = self.x
                self.rect.y = self.y
                self.coordenadas_visitadas.add((nueva_x, nueva_y))
                self.record_position(nueva_x, nueva_y)
                
                print(f"Agente {self.color} yendo a ayudar: ({nueva_x}, {nueva_y})")
                
                # Si llegó cerca del fuego
                if abs(self.x - target_x) < 30 and abs(self.y - target_y) < 30:
                    # YA NO está ayudando, está en posición
                    self.helping_another = False
                    self.target_fire_location = None
                    
                    print(f"¡¡¡Agente {self.color} LLEGÓ AL FUEGO PARA APOYO!!!")
                return
        
        # PRIORIDAD 3: Verificar si hay fuego cerca
        nearby_fire = self.find_nearby_fire(fires)
        if nearby_fire:
            print(f"Agente {self.color} encontró fuego nivel {nearby_fire.level}, tiene {self.fire_units} unidades")
            
            # Contar TODOS los agentes cerca del fuego con unidades
            agents_near_fire = [self]  # Incluirse a sí mismo
            total_units = self.fire_units
            
            for agent in all_agents:
                if agent != self and agent.fire_units > 0:
                    # Distancia del agente al fuego
                    distance = ((agent.x + 10 - nearby_fire.x) ** 2 + (agent.y + 10 - nearby_fire.y) ** 2) ** 0.5
                    if distance < 60:  # Si está cerca del fuego
                        agents_near_fire.append(agent)
                        total_units += agent.fire_units
            
            print(f"Agentes cerca del fuego: {len(agents_near_fire)}, Unidades totales: {total_units}")
            
            # Si hay suficientes unidades, ATACAR
            if total_units >= nearby_fire.level:
                print(f"¡ATACANDO! {total_units} unidades vs fuego nivel {nearby_fire.level}")
                
                # TODOS atacan
                for agent in agents_near_fire:
                    if nearby_fire.level > 0:  # Si aún hay fuego
                        damage = min(agent.fire_units, nearby_fire.level)
                        agent.fire_units -= damage
                        nearby_fire.level -= damage
                        print(f"Agente {agent.color} hace {damage} daño. Fuego restante: {nearby_fire.level}")
                        
                        if agent.fire_units <= 0:
                            agent.start_return_to_base()
                
                # Si el fuego fue extinguido
                if nearby_fire.level <= 0:
                    fires.remove(nearby_fire)
                    print(f"¡FUEGO EXTINGUIDO!")
                
                # Resetear estados
                for agent in all_agents:
                    agent.waiting_for_support = False
                    agent.helping_another = False
                    agent.support_needed = False
                    agent.target_fire_location = None
                
                return
            
            else:
                # No hay suficientes unidades, llamar apoyo
                if not self.waiting_for_support:
                    print(f"Faltan unidades. Llamando apoyo...")
                    
                    for agent in all_agents:
                        if (agent != self and 
                            agent.fire_units > 0 and 
                            not agent.helping_another and
                            not agent.returning_to_base):
                            
                            distance = ((agent.x + 10 - nearby_fire.x) ** 2 + (agent.y + 10 - nearby_fire.y) ** 2) ** 0.5
                            if distance >= 60:  # No está cerca
                                agent.helping_another = True
                                agent.target_fire_location = (nearby_fire.x, nearby_fire.y)
                                print(f"Llamando a {agent.color}")
                    
                    self.waiting_for_support = True
                
                return
        
        # PRIORIDAD 4: Si está esperando apoyo, no moverse
        if self.waiting_for_support:
            return
        
        # COMPORTAMIENTO MEJORADO: Exploración inteligente por turnos con debug
        print(f"\n=== TURNO AGENTE {self.color} ===")
        print(f"Posición actual: ({self.x}, {self.y})")
        print(f"Total posiciones visitadas por todos: {len(self.coordenadas_visitadas)}")
        
        # Evaluar cada dirección individualmente para debug
        for i, (dx, dy) in enumerate(self.direcciones):
            nueva_x = self.x + dx
            nueva_y = self.y + dy
            direccion_nombre = ["ARRIBA", "ABAJO", "IZQUIERDA", "DERECHA"][i]
            
            # Verificar colisión
            colision = self.hay_colision(nueva_x, nueva_y, walls)
            visitada = self.ya_visitada(nueva_x, nueva_y)
            
            print(f"  {direccion_nombre} ({nueva_x}, {nueva_y}): Colisión={colision}, Visitada={visitada}")
        
        opciones = self.evaluar_opciones(walls)
        
        if opciones:
            # Elegir aleatoriamente entre las opciones disponibles
            dx, dy, nueva_x, nueva_y = random.choice(opciones)
            
            # Verificar si es nueva antes de moverse
            es_nueva = not self.ya_visitada(nueva_x, nueva_y)
            
            # Moverse a nueva posicion
            self.x = nueva_x
            self.y = nueva_y
            self.rect.x = self.x
            self.rect.y = self.y
            
            # Agregar nueva coordenada al conjunto compartido
            self.coordenadas_visitadas.add((nueva_x, nueva_y))
            
            # IMPORTANTE: Registrar en historial personal para poder regresar
            self.record_position(nueva_x, nueva_y)
            
            # Mensaje diferenciado según el tipo de movimiento
            if es_nueva:
                print(f"✓ Agente {self.color} exploró NUEVA posición: ({nueva_x}, {nueva_y}) - Historial: {len(self.path_history)} pasos")
            else:
                print(f"↻ Agente {self.color} revisitó posición: ({nueva_x}, {nueva_y}) (sin opciones nuevas)")
        
        else:
            # Caso extremo: no puede moverse a ningún lado
            print(f"✗ Agente {self.color} bloqueado - no puede moverse")
        
        print(f"Ahora hay {len(self.coordenadas_visitadas)} posiciones visitadas")
        print("="*40)
    
    def has_support_nearby(self, all_agents):
        """Verificar si hay otro agente cerca para apoyo"""
        for agent in all_agents:
            if agent != self:
                distance = ((self.x - agent.x) ** 2 + (self.y - agent.y) ** 2) ** 0.5
                if distance < 50:  # Si hay un agente a menos de 50 pixeles
                    return True
        return False
    
    def draw(self, screen):
        """Dibujar el agente con indicadores de estado"""
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Indicadores visuales
        if self.helping_another:
            # Borde azul si está yendo a ayudar
            pygame.draw.rect(screen, CYAN, self.rect, 3)
        
        if self.waiting_for_support:
            # Punto rojo si está esperando apoyo
            pygame.draw.circle(screen, RED, (self.x + 10, self.y + 10), 2)
        
        if self.support_needed:
            # Exclamación si necesita apoyo
            pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 5), 4)
            pygame.draw.circle(screen, RED, (self.x + 15, self.y + 5), 2)
        
        if self.returning_to_base:
            # Borde amarillo si está regresando a base
            pygame.draw.rect(screen, YELLOW, self.rect, 2)
        
        # Si la misión está completa, mostrar marca de verificación
        if self.mission_complete and self.is_at_base():
            pygame.draw.circle(screen, GREEN, (self.x + 10, self.y + 10), 8, 2)
            pygame.draw.circle(screen, GREEN, (self.x + 10, self.y + 10), 3)