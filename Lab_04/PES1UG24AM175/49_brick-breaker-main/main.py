
import pygame
from game.game_engine import GameEngine


WIDTH, HEIGHT = 640, 560
FPS = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Brick Breaker - Pygame Version")
    clock = pygame.time.Clock()
    engine = GameEngine(WIDTH, HEIGHT)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            action = engine.handle_event(event)

            if action == "quit":
                running = False
            elif action == "restart":
                engine.start_new_game(engine.selected_difficulty)

        if running:
            engine.handle_input()
            engine.update()
            engine.render(screen)
            pygame.display.flip()
            clock.tick(FPS)

    engine.close()
    pygame.quit()


if __name__ == "__main__":
    main()
