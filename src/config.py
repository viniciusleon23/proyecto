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

# Tu mapa (1 = pared, 0 = espacio libre, 2 = fuego)
LEVEL = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 2, 0, 1],  # Fuego en posición
    [1, 0, 1, 0, 2, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 2, 0, 0, 1, 0, 0, 2, 0, 1],  # Otro fuego
    [1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 2, 1],  # Tercer fuego
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]