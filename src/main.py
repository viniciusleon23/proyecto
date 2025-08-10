import pygame
import sys
from config import *

from game import Game

def main():
    try:
        pygame.init()
        
        #crea y corre el juego 
        game = Game()
        game.run()
        
    except Exception as e:
        print(f"error : {e}")
        sys.exit(1)
        
    finally:
        pygame.quit()
        sys.exit()
        
        
if __name__ == "__main__":
    main()