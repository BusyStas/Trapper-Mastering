"""
Simple Pygame-based 2D GUI prototype for Trapper-Mastering.
- Arrow keys / WASD to move the player
- ESC or window close to quit

This is a minimal, self-contained prototype to validate a 2D graphical interface.
"""

import sys
import pygame

WIDTH, HEIGHT = 800, 600
BG_COLOR = (34, 139, 34)  # grassy green
GRID_COLOR = (20, 100, 20)
PLAYER_COLOR = (255, 215, 0)  # gold
FPS = 60

PLAYER_SPEED = 240  # pixels per second
PLAYER_RADIUS = 12


def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trapper-Mastering - GUI Prototype")
    clock = pygame.time.Clock()

    # start player in center
    px, py = WIDTH // 2, HEIGHT // 2

    font = pygame.font.SysFont(None, 20)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        px += dx * PLAYER_SPEED * dt
        py += dy * PLAYER_SPEED * dt

        # clamp to screen
        px = max(PLAYER_RADIUS, min(WIDTH - PLAYER_RADIUS, px))
        py = max(PLAYER_RADIUS, min(HEIGHT - PLAYER_RADIUS, py))

        # draw background
        screen.fill(BG_COLOR)

        # draw simple grid
        grid_size = 40
        for x in range(0, WIDTH, grid_size):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, grid_size):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

        # draw player
        pygame.draw.circle(screen, PLAYER_COLOR, (int(px), int(py)), PLAYER_RADIUS)
        pygame.draw.circle(screen, (0, 0, 0), (int(px), int(py)), PLAYER_RADIUS, 2)

        # HUD
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        pos_text = font.render(f"Pos: ({int(px)}, {int(py)})", True, (255, 255, 255))
        screen.blit(fps_text, (8, 8))
        screen.blit(pos_text, (8, 28))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print("Error running GUI prototype:", e, file=sys.stderr)
        pygame.quit()
        sys.exit(1)
