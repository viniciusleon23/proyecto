# Configuración del juego

# Dimensiones de la pantalla
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400

# Tamaño de los tiles/baldosas
TILE_SIZE = 40

# Colores (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (139, 69, 19)  # Marrón para las paredes
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)  # Color para el fuego
YELLOW = (255, 255, 0)  # Fuego nivel 2
PURPLE = (128, 0, 128)  # Fuego nivel 3
CYAN = (0, 255, 255)    # Color para agente de apoyo


# Tu mapa (1 = pared, 0 = espacio libre, 2 = fuego nivel 1, 3 = fuego nivel 2, 4 = fuego nivel 3)
LEVEL = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 3, 0, 0, 2, 0, 0, 1],  # Fuegos nivel 1 y 2
    [1, 0, 1, 0, 0, 0, 0, 4, 0, 1],  # Fuego nivel 3
    [1, 0, 0, 2, 0, 1, 3, 0, 1, 1],  # Más fuegos variados
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 3, 0, 0, 0, 1, 4, 0, 0, 1],  # Fuego nivel 2 y 3
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 4, 0, 3, 0, 0, 0, 1],  # Más fuegos nivel 1 y 2
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Otro fuego nivel 3
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]