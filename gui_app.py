"""
GUI application integrating small parts of the existing Game logic:
- Title screen
- Starter selection (creates Player + starter creature)
- Map scene showing locations from `Game.locations` and allowing travel (scene switching)

This intentionally avoids invoking console-based battle flows. It's a thin UI wrapper
that uses the existing `Player`, `Creature`, and `Game` model classes.
"""

import sys
import random
import pygame
from pygame import Rect

from creature import STARTER_CREATURES, Creature, get_random_wild_creature
from player import Player, TRAP_TYPES, HEAL_ITEMS
from game import Game
from battle import Battle, BattleResult

WIDTH, HEIGHT = 900, 640
BG = (40, 80, 40)
PANEL = (28, 48, 28)
TEXT = (240, 240, 240)
ACCENT = (200, 160, 40)
FPS = 60

# Tilemap / world settings for improved visuals
TILE_SIZE = 48
MAP_COLS = 40
MAP_ROWS = 30
WORLD_W = TILE_SIZE * MAP_COLS
WORLD_H = TILE_SIZE * MAP_ROWS
TILE_COLORS = {
    "grass": (100, 170, 100),
    "water": (48, 120, 180),
    "rock": (120, 110, 100),
}

SCENE_TITLE = "title"
SCENE_STARTER = "starter"
SCENE_MAP = "map"

BUTTON_COLOR = (70, 120, 70)
BUTTON_HOVER = (100, 160, 100)


def draw_text(surface, text, pos, font, color=TEXT):
    surf = font.render(text, True, color)
    surface.blit(surf, pos)


class Button:
    def __init__(self, rect, label):
        self.rect = Rect(rect)
        self.label = label

    def draw(self, surf, font, mouse_pos):
        hovering = self.rect.collidepoint(mouse_pos)
        color = BUTTON_HOVER if hovering else BUTTON_COLOR
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        txt = font.render(self.label, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_rect)

    def clicked(self, mouse_pos, mouse_pressed):
        return mouse_pressed[0] and self.rect.collidepoint(mouse_pos)


def create_starter_copy(starter_template):
    # Starter template is a Creature instance in STARTER_CREATURES
    return Creature(
        starter_template.name,
        starter_template.type,
        starter_template.level,
        starter_template.max_hp,
        starter_template.attack,
        starter_template.defense,
        starter_template.speed,
        [m for m in starter_template.moves],
    )


def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trapper-Mastering - GUI Integration")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    title_font = pygame.font.SysFont(None, 44)

    # Ensure assets exist: generate simple placeholder sprites if missing
    import os
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    def ensure_image(path, size, draw_fn):
        if not os.path.exists(path):
            surf = pygame.Surface(size, pygame.SRCALPHA)
            draw_fn(surf)
            try:
                pygame.image.save(surf, path)
            except Exception:
                # If saving fails (headless env), skip writing file
                pass

    # tile images
    grass_path = os.path.join(assets_dir, "tile_grass.png")
    water_path = os.path.join(assets_dir, "tile_water.png")
    rock_path = os.path.join(assets_dir, "tile_rock.png")
    player_path = os.path.join(assets_dir, "player.png")
    creature_path = os.path.join(assets_dir, "creature.png")

    ensure_image(grass_path, (TILE_SIZE, TILE_SIZE), lambda s: s.fill(TILE_COLORS['grass']))
    ensure_image(water_path, (TILE_SIZE, TILE_SIZE), lambda s: s.fill(TILE_COLORS['water']))
    def draw_rock(s):
        s.fill(TILE_COLORS['rock'])
        pygame.draw.circle(s, (160, 150, 140), (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
    ensure_image(rock_path, (TILE_SIZE, TILE_SIZE), draw_rock)

    def draw_player(s):
        s.fill((0, 0, 0, 0))
        pygame.draw.ellipse(s, ACCENT, (6, 6, TILE_SIZE - 12, TILE_SIZE - 24))
        pygame.draw.circle(s, (0, 0, 0), (TILE_SIZE // 2, 12), 4)
    ensure_image(player_path, (TILE_SIZE, TILE_SIZE), draw_player)

    def draw_creature(s):
        s.fill((0, 0, 0, 0))
        pygame.draw.rect(s, (220, 120, 100), (6, 10, TILE_SIZE - 12, TILE_SIZE - 18), border_radius=6)
    ensure_image(creature_path, (TILE_SIZE, TILE_SIZE), draw_creature)

    # Load images (fallback to simple surfaces if load fails)
    try:
        tile_grass_img = pygame.image.load(grass_path).convert()
        tile_water_img = pygame.image.load(water_path).convert()
        tile_rock_img = pygame.image.load(rock_path).convert()
        player_img = pygame.image.load(player_path).convert_alpha()
        creature_img = pygame.image.load(creature_path).convert_alpha()
    except Exception:
        tile_grass_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        tile_grass_img.fill(TILE_COLORS['grass'])
        tile_water_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        tile_water_img.fill(TILE_COLORS['water'])
        tile_rock_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        tile_rock_img.fill(TILE_COLORS['rock'])
        player_img = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(player_img, ACCENT, (6, 6, TILE_SIZE - 12, TILE_SIZE - 24))
        creature_img = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(creature_img, (220, 120, 100), (6, 10, TILE_SIZE - 12, TILE_SIZE - 18), border_radius=6)

    scene = SCENE_TITLE
    message = ""

    # UI elements
    start_button = Button((WIDTH // 2 - 80, HEIGHT // 2 + 40, 160, 44), "Start Adventure")

    # Starter buttons will be created when entering starter scene
    starter_buttons = []

    # Game model (lazily created when player chooses starter)
    game = None
    # Map / player movement state
    player_px = None
    player_py = None
    player_speed = 180  # pixels per second
    move_accum = 0.0
    location_coords = {}
    # world surface and tiles (created when entering map)
    world_surf = None
    tiles = None
    # battle state for overlay
    battle = None
    in_battle = False
    battle_message = ""
    battle_mode = "action"  # action, moves, trap, item

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill(BG)

        if scene == SCENE_TITLE:
            draw_text(screen, "TRAPPER-MASTERING", (40, 28), title_font, ACCENT)
            draw_text(screen, "A minimal GUI integration prototype.", (40, 78), font)
            draw_text(screen, "This demo covers starter selection and map/scene switching.", (40, 106), font)

            start_button.draw(screen, font, mouse_pos)
            if start_button.clicked(mouse_pos, mouse_pressed):
                # build starter buttons from STARTER_CREATURES
                starter_buttons = []
                names = list(STARTER_CREATURES.keys())
                w = 240
                h = 120
                gap = 24
                total_w = len(names) * w + (len(names) - 1) * gap
                start_x = WIDTH // 2 - total_w // 2
                y = HEIGHT // 2 - h // 2
                for i, name in enumerate(names):
                    rect = (start_x + i * (w + gap), y, w, h)
                    starter_buttons.append((rect, name))
                scene = SCENE_STARTER
                pygame.time.delay(150)

        elif scene == SCENE_STARTER:
            draw_text(screen, "Choose your starter:", (40, 28), title_font)

            for rect, name in starter_buttons:
                r = Rect(rect)
                hovering = r.collidepoint(mouse_pos)
                pygame.draw.rect(screen, PANEL if not hovering else (50, 90, 50), r)
                pygame.draw.rect(screen, (0, 0, 0), r, 2)
                # draw creature info
                starter = STARTER_CREATURES[name]
                draw_text(screen, f"{starter.name} (Type: {starter.type})", (r.x + 12, r.y + 12), font)
                draw_text(screen, f"HP: {starter.max_hp}  ATK: {starter.attack}  DEF: {starter.defense}", (r.x + 12, r.y + 36), font)
                moves = ", ".join(m.name for m in starter.moves)
                draw_text(screen, f"Moves: {moves}", (r.x + 12, r.y + 60), font)

                # choose button
                choose_btn = Rect(r.right - 96, r.bottom - 36, 84, 28)
                pygame.draw.rect(screen, BUTTON_COLOR, choose_btn)
                draw_text(screen, "Choose", (choose_btn.x + 12, choose_btn.y + 6), font)

                if mouse_pressed[0] and (r.collidepoint(mouse_pos) or choose_btn.collidepoint(mouse_pos)):
                    # Create game and player
                    player_name = "Player"  # could prompt via a text field in future
                    player = Player(player_name)
                    starter_obj = create_starter_copy(starter)
                    player.add_creature(starter_obj)
                    game = Game()
                    game.player = player
                    message = f"You chose {starter.name}! Welcome, {player_name}."
                    scene = SCENE_MAP
                    pygame.time.delay(180)
                    break

        elif scene == SCENE_MAP:
            if game is None:
                draw_text(screen, "No game instance found.", (40, 40), font)
            else:
                # Left panel: map / locations
                panel = Rect(16, 16, 540, HEIGHT - 32)
                pygame.draw.rect(screen, PANEL, panel)
                pygame.draw.rect(screen, (0, 0, 0), panel, 2)
                draw_text(screen, f"Location: {game.current_location}", (panel.x + 12, panel.y + 12), title_font)
                draw_text(screen, "Click any location to travel there.", (panel.x + 12, panel.y + 56), font)

                # draw a simple tilemap area inside the left panel
                map_area = Rect(panel.x + 12, panel.y + 96, panel.width - 24, panel.height - 112)
                pygame.draw.rect(screen, (60, 110, 60), map_area)

                # define location marker positions once
                if not location_coords:
                    # lazy-create a simple procedural tile map and location markers
                    tiles = []
                    random.seed(1234)
                    for ry in range(MAP_ROWS):
                        row = []
                        for rx in range(MAP_COLS):
                            r = random.random()
                            if r < 0.1:
                                row.append("water")
                            elif r < 0.18:
                                row.append("rock")
                            else:
                                row.append("grass")
                        tiles.append(row)
                    # create a world surface and paint tiles (use tile images when available)
                    world_surf = pygame.Surface((WORLD_W, WORLD_H))
                    for ry in range(MAP_ROWS):
                        for rx in range(MAP_COLS):
                            t = tiles[ry][rx]
                            x = rx * TILE_SIZE
                            y = ry * TILE_SIZE
                            if t == 'water':
                                world_surf.blit(tile_water_img, (x, y))
                            elif t == 'rock':
                                world_surf.blit(tile_rock_img, (x, y))
                            else:
                                world_surf.blit(tile_grass_img, (x, y))

                    # distribute logical location markers across the world surface
                    locs = list(game.locations.keys())
                    n = len(locs)
                    for i, loc in enumerate(locs):
                        fx = 0.06 + 0.88 * (i / max(1, n - 1))
                        fy = 0.12 + 0.76 * ((i % 4) / 3.0)
                        cx = int(fx * WORLD_W)
                        cy = int(fy * WORLD_H)
                        location_coords[loc] = (cx, cy)

                # initialize player position if needed (near current location) - world coords
                if player_px is None or player_py is None:
                    if game.current_location in location_coords:
                        player_px, player_py = location_coords[game.current_location]
                    else:
                        player_px = WORLD_W // 2
                        player_py = WORLD_H // 2

                # camera centered on player (world coords) and blit visible world to map_area
                cam_x = int(player_px - map_area.width // 2)
                cam_y = int(player_py - map_area.height // 2)
                cam_x = max(0, min(WORLD_W - map_area.width, cam_x))
                cam_y = max(0, min(WORLD_H - map_area.height, cam_y))

                # blit world surface portion
                screen.blit(world_surf, (map_area.x, map_area.y), area=Rect(cam_x, cam_y, map_area.width, map_area.height))

                # draw location markers in screen coords
                for loc, (wx, wy) in location_coords.items():
                    sx = map_area.x + (wx - cam_x)
                    sy = map_area.y + (wy - cam_y)
                    # draw creature icon at marker
                    c_w, c_h = creature_img.get_size()
                    screen.blit(creature_img, (int(sx - c_w / 2), int(sy - c_h / 2)))
                    draw_text(screen, loc, (sx + 16, sy - 8), font)

                # handle player movement (keyboard)
                mv_x = mv_y = 0
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    mv_x -= 1
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    mv_x += 1
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    mv_y -= 1
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    mv_y += 1

                if mv_x != 0 and mv_y != 0:
                    mv_x *= 0.7071
                    mv_y *= 0.7071

                # move player in world coords and clamp
                player_px += mv_x * player_speed * dt
                player_py += mv_y * player_speed * dt
                player_px = max(8, min(WORLD_W - 8, player_px))
                player_py = max(8, min(WORLD_H - 8, player_py))

                # simple animated player sprite (bobbing) using image
                bob = int(3.0 * (1.0 + pygame.time.get_ticks() / 300.0) % 6 - 3)
                psx = map_area.x + (player_px - cam_x)
                psy = map_area.y + (player_py - cam_y) + bob
                p_w, p_h = player_img.get_size()
                screen.blit(player_img, (int(psx - p_w / 2), int(psy - p_h / 2)))

                # check proximity to location markers to 'arrive' at that location
                for loc, (wx, wy) in location_coords.items():
                    dist2 = (player_px - wx) ** 2 + (player_py - wy) ** 2
                    if dist2 <= (TILE_SIZE // 2) ** 2:
                        if game.current_location != loc:
                            game.current_location = loc
                            message = f"Traveled to {loc}."
                            move_accum = 0.0

                # simple encounter trigger when moving in wild areas (not Starting Town)
                move_happened = (abs(mv_x) > 0 or abs(mv_y) > 0)
                if move_happened:
                    move_accum += dt
                if move_accum >= 1.0 and not in_battle:
                    rate = game.locations.get(game.current_location, {}).get('wild_encounter_rate', 0.0)
                    if rate > 0 and random.random() < rate * 0.12:
                        # spawn a wild creature based on tile under player
                        def spawn_wild_at(wx, wy):
                            # determine tile type under player
                            try:
                                tx = int(wx // TILE_SIZE)
                                ty = int(wy // TILE_SIZE)
                                tile = tiles[ty][tx]
                            except Exception:
                                tile = "grass"

                            # try to pick a creature whose type matches a simple habitat map
                            habitat_map = {
                                "water": ["Water", "Electric"],
                                "rock": ["Rock", "Ground"],
                                "grass": ["Grass", "Normal", "Flying", "Ground"],
                            }

                            preferred = habitat_map.get(tile, ["Normal"])
                            for _ in range(8):
                                c = get_random_wild_creature()
                                if c.type in preferred:
                                    return c
                            return get_random_wild_creature()

                        wild = spawn_wild_at(player_px, player_py)
                        # start a Battle instance
                        battle = Battle(game.player, wild)
                        in_battle = True
                        battle_message = f"A wild {wild.name} appeared!"
                    move_accum = 0.0

                # Right panel: player info
                info = Rect(panel.right + 12, 16, WIDTH - panel.right - 28, HEIGHT - 32)
                pygame.draw.rect(screen, PANEL, info)
                pygame.draw.rect(screen, (0, 0, 0), info, 2)
                draw_text(screen, "Player Info", (info.x + 12, info.y + 12), title_font)
                if game.player:
                    draw_text(screen, f"Name: {game.player.name}", (info.x + 12, info.y + 56), font)
                    draw_text(screen, f"Money: ${game.player.money}", (info.x + 12, info.y + 80), font)
                    draw_text(screen, "Party:", (info.x + 12, info.y + 110), font)
                    for idx, c in enumerate(game.player.party):
                        draw_text(screen, f"{idx+1}. {c.name} (Lv.{c.level}) HP:{c.current_hp}/{c.max_hp}", (info.x + 12, info.y + 136 + idx * 26), font)

        # Battle overlay (draw on top of everything)
        if in_battle and battle is not None:
            # overlay panel
            overlay = Rect(WIDTH // 2 - 340, HEIGHT // 2 - 200, 680, 400)
            pygame.draw.rect(screen, (18, 28, 18), overlay)
            pygame.draw.rect(screen, (0, 0, 0), overlay, 3)

            # left: wild creature
            left = Rect(overlay.x + 12, overlay.y + 12, 320, 200)
            pygame.draw.rect(screen, (28, 48, 28), left)
            draw_text(screen, f"Wild: {battle.wild_creature.name} (Lv.{battle.wild_creature.level})", (left.x + 8, left.y + 8), font)
            draw_text(screen, f"HP: {battle.wild_creature.current_hp}/{battle.wild_creature.max_hp}", (left.x + 8, left.y + 34), font)
            draw_text(screen, f"Type: {battle.wild_creature.type}", (left.x + 8, left.y + 58), font)

            # right: player creature and actions
            right = Rect(overlay.x + 344, overlay.y + 12, 320, 200)
            pygame.draw.rect(screen, (28, 48, 28), right)
            pc = battle.player_creature
            draw_text(screen, f"Your: {pc.name} (Lv.{pc.level})", (right.x + 8, right.y + 8), font)
            draw_text(screen, f"HP: {pc.current_hp}/{pc.max_hp}", (right.x + 8, right.y + 34), font)
            draw_text(screen, f"Type: {pc.type}", (right.x + 8, right.y + 58), font)

            # action buttons
            btn_w = 88
            btn_h = 36
            actions = ["Fight", "Trap", "Item", "Run"]
            btns = []
            for i, a in enumerate(actions):
                bx = right.x + 8 + (i % 2) * (btn_w + 8)
                by = right.y + 100 + (i // 2) * (btn_h + 8)
                brect = Rect(bx, by, btn_w, btn_h)
                pygame.draw.rect(screen, BUTTON_COLOR, brect)
                draw_text(screen, a, (bx + 12, by + 8), font)
                btns.append((a, brect))

            # battle log area
            log_rect = Rect(overlay.x + 12, overlay.y + 224, overlay.width - 24, 148)
            pygame.draw.rect(screen, (8, 18, 8), log_rect)
            pygame.draw.rect(screen, (0, 0, 0), log_rect, 2)
            state = battle.get_battle_state()
            logs = state.get('log', [])
            for i, msg in enumerate(reversed(logs)):
                draw_text(screen, msg, (log_rect.x + 8, log_rect.y + 8 + i * 18), font)

            # handle button clicks
            if mouse_pressed[0]:
                for name, rect in btns:
                    if rect.collidepoint(mouse_pos):
                        if name == 'Fight':
                            battle_mode = 'moves'
                        elif name == 'Trap':
                            battle_mode = 'trap'
                        elif name == 'Item':
                            battle_mode = 'item'
                        elif name == 'Run':
                            if battle.attempt_run():
                                battle_message = 'Ran away.'
                        pygame.time.delay(120)

            # moves / trap / item sub-menus
            sub = Rect(overlay.x + 12, overlay.y + 12, overlay.width - 24, 200)
            if battle_mode == 'moves':
                # list moves as buttons
                for i, mv in enumerate(pc.moves):
                    mrect = Rect(sub.x + 12 + (i % 2) * 160, sub.y + 8 + (i // 2) * 48, 152, 40)
                    pygame.draw.rect(screen, (60, 100, 60), mrect)
                    draw_text(screen, f"{mv.name} ({mv.type})", (mrect.x + 6, mrect.y + 8), font)
                    if mouse_pressed[0] and mrect.collidepoint(mouse_pos):
                        battle.player_attack(i)
                        battle_message = 'Player used move.'
                        battle_mode = 'action'
                        pygame.time.delay(120)

            elif battle_mode == 'trap':
                # show trap items from player inventory
                inv_traps = [n for n in game.player.inventory.keys() if 'Trap' in n]
                for i, tname in enumerate(inv_traps):
                    trect = Rect(sub.x + 12 + (i % 3) * 220, sub.y + 8 + (i // 3) * 44, 200, 36)
                    pygame.draw.rect(screen, (80, 120, 80), trect)
                    draw_text(screen, f"{tname} x{game.player.get_item_count(tname)}", (trect.x + 6, trect.y + 8), font)
                    if mouse_pressed[0] and trect.collidepoint(mouse_pos):
                        caught = battle.attempt_catch(tname)
                        battle_message = 'Tried catching.'
                        battle_mode = 'action'
                        pygame.time.delay(120)

            elif battle_mode == 'item':
                heal_items = [n for n in game.player.inventory.keys() if n in HEAL_ITEMS]
                for i, iname in enumerate(heal_items):
                    irect = Rect(sub.x + 12 + (i % 3) * 220, sub.y + 8 + (i // 3) * 44, 200, 36)
                    pygame.draw.rect(screen, (80, 80, 120), irect)
                    draw_text(screen, f"{iname} x{game.player.get_item_count(iname)}", (irect.x + 6, irect.y + 8), font)
                    if mouse_pressed[0] and irect.collidepoint(mouse_pos):
                        used = battle.use_heal_item(iname)
                        battle_message = 'Used item.'
                        battle_mode = 'action'
                        pygame.time.delay(120)

            # if battle ended, show result and a button to close overlay
            if battle.result != BattleResult.ONGOING:
                res_text = f"Result: {battle.result}"
                draw_text(screen, res_text, (overlay.x + 12, overlay.y + 360), font, ACCENT)
                end_rect = Rect(overlay.right - 120, overlay.y + 352, 96, 36)
                pygame.draw.rect(screen, (160, 80, 80), end_rect)
                draw_text(screen, "Continue", (end_rect.x + 10, end_rect.y + 8), font)
                if mouse_pressed[0] and end_rect.collidepoint(mouse_pos):
                    # finalize battle: if caught or won, messages already applied in Battle
                    in_battle = False
                    battle = None
                    battle_mode = 'action'
                    message = ""  # clear map message
                    pygame.time.delay(150)

        # draw footer message
        if message:
            pygame.draw.rect(screen, (0, 0, 0, 120), (0, HEIGHT - 36, WIDTH, 36))
            draw_text(screen, message, (12, HEIGHT - 28), font, ACCENT)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print('Error running GUI app:', e, file=sys.stderr)
        pygame.quit()
        sys.exit(1)
