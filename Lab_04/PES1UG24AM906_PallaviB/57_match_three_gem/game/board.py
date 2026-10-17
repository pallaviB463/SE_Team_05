import random
import math
import pygame

GRID_SIZE = 8
TILE_SIZE = 60
GEM_COLORS = [
    (220, 50, 50),   # Red
    (50, 200, 50),   # Green
    (50, 100, 240),  # Blue
    (240, 200, 40),  # Yellow
    (180, 50, 220),  # Purple
    (240, 130, 40),  # Orange
]
IDLE_HINT_DELAY = 5000


class Gem:
   
    def __init__(self, color, target_row, col):
        self.color = color
        self.special_direction = None
        self.target_row = target_row
        self.col = col
        self.current_y = (target_row - 2) * TILE_SIZE
        self.target_y = target_row * TILE_SIZE
        self.fall_speed = 12.0

    def update(self):
        if self.current_y < self.target_y:
            self.current_y += self.fall_speed
            if self.current_y > self.target_y:
                self.current_y = self.target_y

    def is_animating(self):
        return self.current_y < self.target_y


class Board:

    def __init__(self, offset_x, offset_y, target_score=500, max_moves=20):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.target_score = target_score
        self.max_moves = max_moves
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected = None
        self.score = 0
        self.moves_remaining = max_moves
        self.idle_since = pygame.time.get_ticks()
        self.hint_swap = None
        self.reset()

    def reset(self):
        self.score = 0
        self.moves_remaining = self.max_moves
        self.selected = None
        self.reset_idle_timer()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = random.choice(GEM_COLORS)
                gem = Gem(color, r, c)
                gem.current_y = gem.target_y  
                self.grid[r][c] = gem

        self.resolve_matches()
        self._ensure_valid_move()

    def _ensure_valid_move(self):
        # Normally a random board has a legal move. If it does not, reshuffle
        # existing gem colors a bounded number of times rather than leaving the
        # player with a board that cannot be played.
        for _ in range(100):
            if self._find_hint_swap() is not None:
                return
            colors = [gem.color for row in self.grid for gem in row if gem]
            random.shuffle(colors)
            index = 0
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    gem = self.grid[r][c]
                    if gem:
                        gem.color = colors[index]
                        index += 1
            self.resolve_matches()

        # Deterministic fallback: guarantee a horizontal three-match is one
        # swap away by making the first three cells in row 0 the same color,
        # with a matching color directly below the third cell.
        color = GEM_COLORS[0]
        self.grid[0][0].color = color
        self.grid[0][1].color = color
        self.grid[0][2].color = GEM_COLORS[1]
        self.grid[1][2].color = color
        self.grid[0][3].color = GEM_COLORS[2]
        self.reset_idle_timer()

    def reset_idle_timer(self):
        self.idle_since = pygame.time.get_ticks()
        self.hint_swap = None

    def _find_hint_swap(self):
        # Search only on a stable board. Swap grid references temporarily so
        # testing a candidate cannot change gem animation positions.
        existing_matches = self.find_matches()

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                for neighbor in ((r, c + 1), (r + 1, c)):
                    nr, nc = neighbor
                    if nr >= GRID_SIZE or nc >= GRID_SIZE:
                        continue

                    self.grid[r][c], self.grid[nr][nc] = (
                        self.grid[nr][nc],
                        self.grid[r][c],
                    )
                    try:
                        new_matches = self.find_matches()
                        creates_match = bool(new_matches - existing_matches)
                    finally:
                        # Always restore the original board, even if matching
                        # raises an exception.
                        self.grid[r][c], self.grid[nr][nc] = (
                            self.grid[nr][nc],
                            self.grid[r][c],
                        )

                    if creates_match:
                        return ((r, c), neighbor)
        return None

    def _update_hint(self):
        elapsed_idle_ms = pygame.time.get_ticks() - self.idle_since
        animating = self.is_animating()
        game_over = self.is_game_over()
        if (
            animating
            or game_over
            or elapsed_idle_ms < IDLE_HINT_DELAY
        ):
            self.hint_swap = None
            return
        if self.hint_swap is None:
            self.hint_swap = self._find_hint_swap()

    def is_animating(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] and self.grid[r][c].is_animating():
                    return True
        return False

    def swap_gems(self, pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2

        g1, g2 = self.grid[r1][c1], self.grid[r2][c2]
        self.grid[r1][c1], self.grid[r2][c2] = g2, g1

        if self.grid[r1][c1]:
            self.grid[r1][c1].target_row = r1
            self.grid[r1][c1].target_y = r1 * TILE_SIZE
            self.grid[r1][c1].current_y = r1 * TILE_SIZE

        if self.grid[r2][c2]:
            self.grid[r2][c2].target_row = r2
            self.grid[r2][c2].target_y = r2 * TILE_SIZE
            self.grid[r2][c2].current_y = r2 * TILE_SIZE

    def is_adjacent(self, pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2
        return abs(r1 - r2) + abs(c1 - c2) == 1

    def find_matches(self):
        matched, _ = self._find_match_groups()
        return matched

    def _find_match_groups(self):
        matched = set()
        groups = []

        for r in range(GRID_SIZE):
            c = 0
            while c < GRID_SIZE:
                start = c
                gem = self.grid[r][c]
                while (
                    gem
                    and c + 1 < GRID_SIZE
                    and self.grid[r][c + 1]
                    and self.grid[r][c + 1].color == gem.color
                ):
                    c += 1
                if c - start + 1 >= 3:
                    group = {(r, match_col) for match_col in range(start, c + 1)}
                    matched.update(group)
                    if len(group) >= 4:
                        groups.append((group, "row"))
                c += 1

        for c in range(GRID_SIZE):
            r = 0
            while r < GRID_SIZE:
                start = r
                gem = self.grid[r][c]
                while (
                    gem
                    and r + 1 < GRID_SIZE
                    and self.grid[r + 1][c]
                    and self.grid[r + 1][c].color == gem.color
                ):
                    r += 1
                if r - start + 1 >= 3:
                    group = {(match_row, c) for match_row in range(start, r + 1)}
                    matched.update(group)
                    if len(group) >= 4:
                        groups.append((group, "column"))
                r += 1

        return matched, groups

    def _expand_special_matches(self, matches):
        clear_positions = set(matches)
        pending = [
            position
            for position in matches
            if self.grid[position[0]][position[1]]
            and self.grid[position[0]][position[1]].special_direction
        ]
        activated = set()

        while pending:
            position = pending.pop()
            if position in activated:
                continue
            activated.add(position)
            gem = self.grid[position[0]][position[1]]
            if not gem:
                continue

            if gem.special_direction == "row":
                affected = {(position[0], c) for c in range(GRID_SIZE)}
            else:
                affected = {(r, position[1]) for r in range(GRID_SIZE)}

            for affected_position in affected:
                clear_positions.add(affected_position)
                affected_gem = self.grid[affected_position[0]][affected_position[1]]
                if (
                    affected_gem
                    and affected_gem.special_direction
                    and affected_position not in activated
                ):
                    pending.append(affected_position)

        return clear_positions

    
    def drop_and_refill(self):
        for c in range(GRID_SIZE):
            empty_slots = 0

            # Move existing gems down within this column
            for r in range(GRID_SIZE - 1, -1, -1):
                if self.grid[r][c] is None:
                    empty_slots += 1
                elif empty_slots > 0:
                    gem = self.grid[r][c]
                    new_row = r + empty_slots

                    gem.target_row = new_row
                    gem.target_y = new_row * TILE_SIZE

                    self.grid[new_row][c] = gem
                    self.grid[r][c] = None

            # Fill empty spaces at the top of this column
            for r in range(empty_slots):
                color = random.choice(GEM_COLORS)
                gem = Gem(color, r, c)
                gem.current_y = -((empty_slots - r) * TILE_SIZE)
                self.grid[r][c] = gem


    def resolve_matches(self, award_score=False):
        total_cleared = 0
        cascade_multiplier = 1
        while True:
            matches, groups = self._find_match_groups()
            if not matches:
                break

            clear_positions = self._expand_special_matches(matches)
            special_positions = {}
            for group, direction in groups:
                special_position = sorted(group)[len(group) // 2]
                special_gem = self.grid[special_position[0]][special_position[1]]
                if special_position in clear_positions and not (
                    special_gem and special_gem.special_direction
                ):
                    special_positions.setdefault(special_position, direction)

            clear_positions -= special_positions.keys()
            total_cleared += len(clear_positions)
            if award_score:
                self.score += len(clear_positions) * 10 * cascade_multiplier
                cascade_multiplier += 1

            for r, c in clear_positions:
                self.grid[r][c] = None
            for (r, c), direction in special_positions.items():
                gem = Gem(self.grid[r][c].color if self.grid[r][c] else GEM_COLORS[0], r, c)
                gem.special_direction = direction
                gem.current_y = gem.target_y = r * TILE_SIZE
                self.grid[r][c] = gem
            self.drop_and_refill()
        return total_cleared

    
    def process_swap(self, pos1, pos2):
        self.reset_idle_timer()
        if (
            not self.is_adjacent(pos1, pos2)
            or self.is_game_over()
            or self.is_animating()
        ):
            return False

        self.swap_gems(pos1, pos2)
        matches = self.find_matches()

        # Invalid swaps must not consume a move
        if not matches:
            self.swap_gems(pos1, pos2)
            return False

        # Only valid swaps consume a move
        self.moves_remaining -= 1

        self.resolve_matches(award_score=True)
        return True


    def is_game_over(self):
        return self.score >= self.target_score or self.moves_remaining <= 0

    def check_result(self):
        if self.score >= self.target_score:
            return "WIN"
        if self.moves_remaining <= 0:
            return "LOSS"
        return None

    def update(self):
        self._update_hint()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c]:
                    self.grid[r][c].update()

    def render(self, surface):
        board_rect = pygame.Rect(
            self.offset_x, self.offset_y, GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE
        )
        pygame.draw.rect(surface, (20, 22, 28), board_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 65, 75), board_rect, width=3, border_radius=8)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                gem = self.grid[r][c]
                if gem:
                    x = self.offset_x + c * TILE_SIZE
                    y = self.offset_y + gem.current_y
                    tile_rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)

                    pygame.draw.rect(surface, gem.color, tile_rect, border_radius=10)
                    pygame.draw.rect(
                        surface, (255, 255, 255), tile_rect, width=1, border_radius=10
                    )
                    if gem.special_direction:
                        pygame.draw.rect(
                            surface, (255, 245, 120), tile_rect, width=4, border_radius=10
                        )
                        if gem.special_direction == "row":
                            pygame.draw.line(
                                surface,
                                (255, 255, 220),
                                tile_rect.midleft,
                                tile_rect.midright,
                                width=3,
                            )
                        else:
                            pygame.draw.line(
                                surface,
                                (255, 255, 220),
                                tile_rect.midtop,
                                tile_rect.midbottom,
                                width=3,
                            )

                if self.selected == (r, c):
                    sel_x = self.offset_x + c * TILE_SIZE
                    sel_y = self.offset_y + r * TILE_SIZE
                    sel_rect = pygame.Rect(sel_x + 2, sel_y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                    pygame.draw.rect(
                        surface, (255, 255, 255), sel_rect, width=4, border_radius=10
                    )

        if self.hint_swap:
            pulse = int(80 + 50 * math.sin(pygame.time.get_ticks() / 180))
            hint_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            for row, col in self.hint_swap:
                x = self.offset_x + col * TILE_SIZE
                y = self.offset_y + row * TILE_SIZE
                hint_rect = pygame.Rect(x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
                pygame.draw.rect(
                    hint_surface,
                    (255, 240, 120, pulse),
                    hint_rect,
                    width=4,
                    border_radius=10,
                )
            surface.blit(hint_surface, (0, 0))
