from OpenGL.GL import *
from OpenGL.GLU import *
from classes.game import Game


def main():

    try:
        game = Game()
        print("Game initialized successfully!")
        print("Starting night racing game...")
        game.run()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
