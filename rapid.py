import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()

# ==================== CONSTANTS ====================
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

# Colors - Enhanced Neon Palette
BLACK = (10, 10, 15)
DARK_BG = (15, 12, 30)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 0, 200)
NEON_GREEN = (0, 255, 100)
NEON_ORANGE = (255, 128, 0)
NEON_YELLOW = (255, 255, 0)
NEON_PURPLE = (200, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
DARK_RED = (100, 0, 0)

# Physics
GRAVITY = 0.5
PLAYER_SPEED = 8
JUMP_FORCE = 16
FRICTION = 0.87

# Ground level (platform area from image)
GROUND_Y = SCREEN_HEIGHT - 180

# ==================== SETUP ====================
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("⚡ NEON NINJA FIGHTER ⚡")
clock = pygame.time.Clock()

# Enhanced Neon Fonts
font_small = pygame.font.SysFont("arial", 14, bold=True)
font_medium = pygame.font.SysFont("arial", 18, bold=True)
font_large = pygame.font.SysFont("arial", 28, bold=True)
font_xlarge = pygame.font.SysFont("arial", 50, bold=True)
font_title = pygame.font.SysFont("arial", 80, bold=True)
font_subtitle = pygame.font.SysFont("arial", 50, bold=True)
font_name_input = pygame.font.SysFont("arial", 32, bold=True)

# Load all images
def load_image(path, size=None):
    """Load image from assets path"""
    if os.path.exists(path):
        img = pygame.image.load(path)
        if size:
            img = pygame.transform.scale(img, size)
        return img
    return None

# Load backgrounds
menu_bg = load_image("assets/menu.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
main_bg = load_image("assets/main.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load character images - BIGGER SIZES
player_image = load_image("assets/characters/player.png", (100, 140))
player_image_flipped = pygame.transform.flip(player_image, True, False) if player_image else None

bowman_img = load_image("assets/characters/bowman.png", (90, 130))
bowman_img_flipped = pygame.transform.flip(bowman_img, True, False) if bowman_img else None
gunman_img = load_image("assets/characters/gunman.png", (90, 130))
gunman_img_flipped = pygame.transform.flip(gunman_img, True, False) if gunman_img else None
swordsman_img = load_image("assets/characters/swordsman.png", (90, 130))
swordsman_img_flipped = pygame.transform.flip(swordsman_img, True, False) if swordsman_img else None

# Load weapon images
sword_img = load_image("assets/weapons/sword.png", (50, 50))
bow_img = load_image("assets/weapons/bow.png", (50, 50))
gun_img = load_image("assets/weapons/gun.png", (50, 50))

weapon_images = {
    'SWORD': sword_img,
    'BOW': bow_img,
    'GUN': gun_img
}

print("✓ All assets loaded successfully!")

# ==================== CLASSES ====================

class Weapon:
    def __init__(self, name, damage, cooldown, color, image=None):
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.color = color
        self.current_cooldown = 0
        self.image = image
    
    def can_shoot(self):
        return self.current_cooldown <= 0
    
    def shoot(self):
        self.current_cooldown = self.cooldown
    
    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class Sword:
    def __init__(self, x, y, direction, damage, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.damage = damage
        self.color = color
        self.life = 20
        self.alive = True
        self.angle = 0
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.alive = False
        self.angle = (1 - self.life / 20) * math.pi
        self.x += self.direction * 8
    
    def draw(self):
        length = 45
        width = 12
        
        tip_x = self.x + math.cos(self.angle + math.pi/2) * length * self.direction
        tip_y = self.y + math.sin(self.angle + math.pi/2) * length
        
        side1_x = self.x - width/2
        side1_y = self.y - 8
        
        side2_x = self.x + width/2
        side2_y = self.y - 8
        
        # Glow effect
        pygame.draw.polygon(screen, self.color, [
            (tip_x, tip_y),
            (side1_x, side1_y),
            (side2_x, side2_y)
        ])
        
        pygame.draw.line(screen, self.color, (tip_x, tip_y), (side1_x, side1_y), 3)
        pygame.draw.line(screen, self.color, (tip_x, tip_y), (side2_x, side2_y), 3)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (tip_x, tip_y), 2)


class Arrow:
    def __init__(self, x, y, direction, damage, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.vel_x = direction * 14
        self.vel_y = -1
        self.damage = damage
        self.color = color
        self.alive = True
        self.angle = 0
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY * 0.4
        self.angle = math.atan2(self.vel_y, self.vel_x)
        
        if self.x < -50 or self.x > SCREEN_WIDTH + 50 or self.y > SCREEN_HEIGHT + 50:
            self.alive = False
    
    def draw(self):
        end_x = self.x - math.cos(self.angle) * 15
        end_y = self.y - math.sin(self.angle) * 15
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), 3)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 6)


class Bullet:
    def __init__(self, x, y, direction, damage, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.vel_x = direction * 16
        self.vel_y = -0.5
        self.damage = damage
        self.color = color
        self.alive = True
        self.time = 0
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY * 0.2
        self.time += 1
        
        if self.x < -50 or self.x > SCREEN_WIDTH + 50 or self.y > SCREEN_HEIGHT + 50:
            self.alive = False
    
    def draw(self):
        size = 8
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), size - 2)


class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.x = 250
        self.y = GROUND_Y - 140
        self.width = 100
        self.height = 140
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.health = 300
        self.max_health = 300
        self.invincible = 0
        
        # Weapons - SWORD damage between BOW and GUN
        self.weapons = {
            'SWORD': Weapon('SWORD', 50, 15, NEON_CYAN, sword_img),
            'BOW': Weapon('BOW', 45, 25, NEON_GREEN, bow_img),
            'GUN': Weapon('GUN', 55, 20, NEON_ORANGE, gun_img)
        }
        self.current_weapon = self.weapons['SWORD']
        self.weapon_names = ['SWORD', 'BOW', 'GUN']
        self.weapon_idx = 0
        
        self.is_moving = False
    
    def update(self, keys):
        moving = False
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
            moving = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
            moving = True
        else:
            self.vel_x *= FRICTION
        
        self.is_moving = moving
        
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -JUMP_FORCE
            self.on_ground = False
        
        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
        
        self.x = max(10, min(SCREEN_WIDTH - self.width - 10, self.x))
        
        if self.invincible > 0:
            self.invincible -= 1
        
        self.current_weapon.update()
    
    def switch_weapon(self):
        self.weapon_idx = (self.weapon_idx + 1) % len(self.weapon_names)
        self.current_weapon = self.weapons[self.weapon_names[self.weapon_idx]]
    
    def shoot(self, bullets_list):
        if not self.current_weapon.can_shoot():
            return
        
        direction = 1 if self.facing_right else -1
        weapon_name = self.current_weapon.name
        
        if weapon_name == 'SWORD':
            sword = Sword(
                self.x + (self.width if self.facing_right else -10),
                self.y + 60,
                direction,
                self.current_weapon.damage,
                self.current_weapon.color
            )
            bullets_list.append(sword)
        
        elif weapon_name == 'BOW':
            arrow = Arrow(
                self.x + (self.width if self.facing_right else -10),
                self.y + 50,
                direction,
                self.current_weapon.damage,
                self.current_weapon.color
            )
            bullets_list.append(arrow)
        
        elif weapon_name == 'GUN':
            bullet = Bullet(
                self.x + (self.width if self.facing_right else -10),
                self.y + 50,
                direction,
                self.current_weapon.damage,
                self.current_weapon.color
            )
            bullets_list.append(bullet)
        
        self.current_weapon.shoot()
    
    def take_damage(self, amount):
        if self.invincible == 0:
            self.health -= amount
            self.invincible = 50
            return True
        return False
    
    def draw(self):
        if self.invincible > 0 and self.invincible % 6 < 3:
            return
        
        if player_image is not None:
            img_to_draw = player_image_flipped if not self.facing_right else player_image
            screen.blit(img_to_draw, (self.x - 30, self.y - 20))
        else:
            pygame.draw.circle(screen, NEON_CYAN, (self.x + self.width//2, self.y + self.height//2), 35)


class EnemySword:
    def __init__(self, x, y, direction, damage, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.damage = damage
        self.color = color
        self.life = 20
        self.alive = True
        self.angle = 0
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.alive = False
        self.angle = (1 - self.life / 20) * math.pi
        self.x += self.direction * 6
    
    def draw(self):
        length = 40
        width = 8
        
        tip_x = self.x + math.cos(self.angle + math.pi/2) * length * self.direction
        tip_y = self.y + math.sin(self.angle + math.pi/2) * length
        
        side1_x = self.x - width/2
        side1_y = self.y - 8
        
        side2_x = self.x + width/2
        side2_y = self.y - 8
        
        pygame.draw.polygon(screen, (150, 150, 255), [
            (tip_x, tip_y),
            (side1_x, side1_y),
            (side2_x, side2_y)
        ])
        
        pygame.draw.line(screen, self.color, (tip_x, tip_y), (side1_x, side1_y), 2)
        pygame.draw.line(screen, self.color, (tip_x, tip_y), (side2_x, side2_y), 2)


class EnemyArrow:
    def __init__(self, x, y, dir_x, dir_y, damage, color):
        self.x = x
        self.y = y
        self.vel_x = dir_x * 12
        self.vel_y = dir_y * 12
        self.damage = damage
        self.color = color
        self.alive = True
        self.angle = math.atan2(dir_y, dir_x)
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY * 0.3
        self.angle = math.atan2(self.vel_y, self.vel_x)
        
        if self.x < -50 or self.x > SCREEN_WIDTH + 50 or self.y > SCREEN_HEIGHT + 50:
            self.alive = False
    
    def draw(self):
        end_x = self.x - math.cos(self.angle) * 12
        end_y = self.y - math.sin(self.angle) * 12
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 4)


class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y, damage, color):
        self.x = x
        self.y = y
        self.vel_x = dir_x * 14
        self.vel_y = dir_y * 14
        self.damage = damage
        self.color = color
        self.alive = True
        self.time = 0
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY * 0.15
        self.time += 1
        
        if self.x < -50 or self.x > SCREEN_WIDTH + 50 or self.y > SCREEN_HEIGHT + 50:
            self.alive = False
    
    def draw(self):
        size = 7
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), size - 2)


class Enemy:
    def __init__(self, enemy_type, side, wave):
        self.type = enemy_type
        self.alive = True
        self.side = side
        self.wave = wave
        
        # ALL ENEMIES come CLOSE - no standoff distance
        if side == 'left':
            self.x = 50
            # ALL come close to center
            self.target_x = random.randint(200, 350)
        else:
            self.x = SCREEN_WIDTH - 130
            self.target_x = random.randint(SCREEN_WIDTH - 350, SCREEN_WIDTH - 200)
        
        self.y = GROUND_Y - 130
        self.width = 90
        self.height = 130
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = side == 'left'
        
        # Wave scaling - UNLIMITED
        scale = 0.7 + (wave * 0.15)
        scale = min(scale, 4.0)
        
        if enemy_type == 'BRUTE':
            self.speed = 5.0 * scale
            self.max_hp = int(40 * scale)
            self.damage = int(15 * scale)
            self.accuracy = 0.90
            self.shoot_cooldown = max(8, int(20 / scale))
            self.color = RED
            self.image = swordsman_img
            self.image_flipped = swordsman_img_flipped
        
        elif enemy_type == 'ARCHER':
            self.speed = 2.5 * scale
            self.max_hp = int(28 * scale)
            self.damage = int(18 * scale)
            self.accuracy = 0.70 + (wave * 0.04)
            self.shoot_cooldown = max(18, int(40 / scale))
            self.color = NEON_GREEN
            self.image = bowman_img
            self.image_flipped = bowman_img_flipped
        
        elif enemy_type == 'GUNNER':
            self.speed = 3.2 * scale
            self.max_hp = int(35 * scale)
            self.damage = int(16 * scale)
            self.accuracy = 0.76 + (wave * 0.04)
            self.shoot_cooldown = max(16, int(35 / scale))
            self.color = NEON_ORANGE
            self.image = gunman_img
            self.image_flipped = gunman_img_flipped
        
        self.hp = self.max_hp
        self.shoot_timer = 0
        self.hit_timer = 0
    
    def update(self, player, bullets_list):
        distance_to_target = abs(self.x - self.target_x)
        
        # MOVE TOWARDS TARGET
        if distance_to_target > 15:
            if self.target_x > self.x:
                self.vel_x = self.speed
                self.facing_right = True
            else:
                self.vel_x = -self.speed
                self.facing_right = False
        else:
            # Slight slow down at target
            self.vel_x *= 0.9
        
        # ALWAYS SHOOT WHEN ON GROUND
        if self.on_ground:
            self.shoot_timer += 1
            if self.shoot_timer > self.shoot_cooldown:
                self.shoot_at_player(player, bullets_list)
                self.shoot_timer = 0
        
        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
        
        if self.hit_timer > 0:
            self.hit_timer -= 1
    
    def shoot_at_player(self, player, bullets_list):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist == 0:
            return
        
        if random.random() > self.accuracy:
            dx += random.uniform(-100, 100)
            dy += random.uniform(-60, 60)
            dist = math.sqrt(dx*dx + dy*dy)
            if dist == 0:
                return
        
        if self.type == 'BRUTE':
            sword = EnemySword(self.x, self.y + 40, 1 if self.facing_right else -1, self.damage, self.color)
            bullets_list.append(sword)
        
        elif self.type == 'ARCHER':
            arrow = EnemyArrow(self.x, self.y + 30, dx/dist, dy/dist, self.damage, self.color)
            bullets_list.append(arrow)
        
        elif self.type == 'GUNNER':
            bullet = EnemyBullet(self.x, self.y + 30, dx/dist, dy/dist, self.damage, self.color)
            bullets_list.append(bullet)
    
    def draw(self):
        if self.hit_timer > 0 and self.hit_timer % 5 < 3:
            return
        
        if self.image:
            img_to_draw = self.image_flipped if not self.facing_right else self.image
            screen.blit(img_to_draw, (self.x - 30, self.y - 20))
        else:
            pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), 35)
        
        bar_width = self.width
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, DARK_RED, (self.x, self.y - 30, bar_width, 5))
        pygame.draw.rect(screen, NEON_GREEN, (self.x, self.y - 30, bar_width * hp_ratio, 5))
        pygame.draw.rect(screen, self.color, (self.x, self.y - 30, bar_width, 5), 1)


class Particle:
    def __init__(self, x, y, color, vel_x=0, vel_y=0):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x + random.uniform(-2, 2)
        self.vel_y = vel_y + random.uniform(-3, -1)
        self.size = random.randint(3, 8)
        self.life = random.randint(30, 60)
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY * 0.2
        self.life -= 1
        self.size = max(0, self.size - 0.15)
    
    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))


# ==================== GLOBAL STATE ====================
player = None
player_bullets = []
enemy_bullets = []
enemies = []
particles = []
wave = 1
score = 0
game_over = False
enemy_spawn_timer = 0
game_state = "MENU"
player_name_input = ""
total_waves_completed = 0
wave_transition_timer = 0
loading_progress = 0

# ==================== FUNCTIONS ====================

def draw_neon_glow_box(x, y, width, height, color, thickness=3, glow_size=2):
    """Draw a neon-style box with glow"""
    # Outer glow
    for i in range(glow_size, 0, -1):
        glow_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.rect(screen, glow_color, (x - i, y - i, width + i*2, height + i*2), 1)
    
    # Main border
    pygame.draw.rect(screen, color, (x, y, width, height), thickness)
    
    # Corner decorations
    corner_size = 15
    corners = [
        (x, y),
        (x + width - corner_size, y),
        (x, y + height - corner_size),
        (x + width - corner_size, y + height - corner_size)
    ]
    
    for cx, cy in corners[:2]:
        pygame.draw.line(screen, color, (cx, cy), (cx + corner_size, cy), thickness)
        pygame.draw.line(screen, color, (cx, cy), (cx, cy + corner_size), thickness)
    
    for cx, cy in corners[2:]:
        pygame.draw.line(screen, color, (cx, cy), (cx + corner_size, cy), thickness)
        pygame.draw.line(screen, color, (cx, cy), (cx, cy + corner_size), thickness)


def draw_loading_screen():
    if menu_bg:
        screen.blit(menu_bg, (0, 0))
    else:
        screen.fill(BLACK)
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(100)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    loading_text = font_xlarge.render("LOADING", True, NEON_CYAN)
    loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(loading_text, loading_rect)
    
    # Neon loading bar
    bar_width = 400
    bar_height = 20
    bar_x = SCREEN_WIDTH//2 - bar_width//2
    bar_y = SCREEN_HEIGHT//2 + 50
    
    draw_neon_glow_box(bar_x, bar_y, bar_width, bar_height, NEON_CYAN, 2, 1)
    
    fill_width = int(bar_width * (loading_progress / 100))
    pygame.draw.rect(screen, NEON_PINK, (bar_x + 2, bar_y + 2, fill_width - 4, bar_height - 4))
    
    percent_text = font_medium.render(f"{int(loading_progress)}%", True, NEON_YELLOW)
    screen.blit(percent_text, (SCREEN_WIDTH//2 - 25, bar_y + 30))


def draw_menu_screen():
    if menu_bg:
        screen.blit(menu_bg, (0, 0))
    else:
        screen.fill(BLACK)
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(120)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # ===== TITLE WITH ENHANCED GLOW =====
    title_text = font_title.render("⚡ NEON NINJA", True, NEON_CYAN)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 60))
    
    # Draw glow multiple times
    for i in range(5, 0, -1):
        glow_surf = font_title.render("⚡ NEON NINJA", True, NEON_CYAN)
        glow_surf.set_alpha(30)
        screen.blit(glow_surf, (title_rect.x - i, title_rect.y))
    
    screen.blit(title_text, title_rect)
    
    # ===== SUBTITLE =====
    subtitle_text = font_subtitle.render("FIGHTER", True, NEON_PINK)
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 140))
    
    for i in range(4, 0, -1):
        glow_surf = font_subtitle.render("FIGHTER", True, NEON_PINK)
        glow_surf.set_alpha(25)
        screen.blit(glow_surf, (subtitle_rect.x - i, subtitle_rect.y))
    
    screen.blit(subtitle_text, subtitle_rect)
    
    # ===== LABEL =====
    label_text = font_large.render("ENTER YOUR NAME", True, NEON_GREEN)
    label_rect = label_text.get_rect(center=(SCREEN_WIDTH//2, 260))
    screen.blit(label_text, label_rect)
    
    # ===== ENHANCED INPUT BOX - FIXED =====
    input_box_x = SCREEN_WIDTH//2 - 240
    input_box_y = 330
    input_box_width = 480
    input_box_height = 80
    
    # Draw enhanced neon box
    draw_neon_glow_box(input_box_x, input_box_y, input_box_width, input_box_height, NEON_CYAN, 3, 2)
    
    # Inner fill - SOLID COLOR, NO LINE
    pygame.draw.rect(screen, (10, 25, 50), (input_box_x + 4, input_box_y + 4, input_box_width - 8, input_box_height - 8))
    
    # Player name display
    if player_name_input:
        name_display = font_name_input.render(player_name_input.upper(), True, NEON_PINK)
    else:
        name_display = font_medium.render("Type your warrior name...", True, (100, 120, 150))
    
    name_rect = name_display.get_rect(center=(SCREEN_WIDTH//2, input_box_y + input_box_height//2))
    screen.blit(name_display, name_rect)
    
    # ===== INSTRUCTIONS =====
    instructions1 = font_medium.render("Press ENTER to Start Battle", True, NEON_YELLOW)
    screen.blit(instructions1, (SCREEN_WIDTH//2 - 220, 480))
    
    instructions2 = font_small.render("Max 15 characters", True, (100, 150, 150))
    screen.blit(instructions2, (SCREEN_WIDTH//2 - 80, 520))


def draw_background():
    if main_bg:
        screen.blit(main_bg, (0, 0))
    else:
        screen.fill(BLACK)


def spawn_enemy(wave_num):
    types = ['BRUTE', 'ARCHER', 'GUNNER']
    
    # EASY START - gradually increase difficulty
    if wave_num == 1:
        weights = [0.6, 0.3, 0.1]  # Mostly BRUTE
        count = 1  # Only 1 enemy
    elif wave_num == 2:
        weights = [0.5, 0.35, 0.15]
        count = 1  # Still 1 enemy
    elif wave_num == 3:
        weights = [0.4, 0.4, 0.2]
        count = 2  # Now 2 enemies
    elif wave_num == 4:
        weights = [0.35, 0.4, 0.25]
        count = 2
    elif wave_num == 5:
        weights = [0.3, 0.4, 0.3]
        count = 3
    elif wave_num == 6:
        weights = [0.25, 0.4, 0.35]
        count = 3
    else:
        weights = [0.2, 0.35, 0.45]
        count = 3 + (wave_num - 7) // 3  # Gradual increase after wave 6
    
    for _ in range(count):
        enemy_type = random.choices(types, weights=weights)[0]
        side = random.choice(['left', 'right'])
        enemies.append(Enemy(enemy_type, side, wave_num))


def check_collisions():
    global score, wave, total_waves_completed, game_state, wave_transition_timer
    
    for bullet in player_bullets[:]:
        if not bullet.alive:
            continue
        
        for enemy in enemies:
            hit = False
            
            if isinstance(bullet, Sword):
                hit = (bullet.x > enemy.x - 30 and bullet.x < enemy.x + enemy.width + 30 and
                       bullet.y > enemy.y - 30 and bullet.y < enemy.y + enemy.height + 30)
            else:
                hit = (bullet.x > enemy.x - 10 and bullet.x < enemy.x + enemy.width + 10 and
                       bullet.y > enemy.y and bullet.y < enemy.y + enemy.height)
            
            if hit:
                enemy.hp -= bullet.damage
                enemy.hit_timer = 15
                
                for _ in range(10):
                    particles.append(Particle(bullet.x, bullet.y, bullet.color))
                
                if not isinstance(bullet, Bullet):
                    bullet.alive = False
                
                if enemy.hp <= 0:
                    bonus = {'BRUTE': 50, 'ARCHER': 75, 'GUNNER': 60}
                    score += bonus.get(enemy.type, 25)
                    for _ in range(25):
                        particles.append(Particle(enemy.x + enemy.width//2, enemy.y + 40, enemy.color,
                                               random.uniform(-4, 4), random.uniform(-4, 2)))
    
    for bullet in enemy_bullets[:]:
        if (bullet.x > player.x and bullet.x < player.x + player.width and
            bullet.y > player.y and bullet.y < player.y + player.height):
            
            if player.take_damage(bullet.damage):
                for _ in range(15):
                    particles.append(Particle(player.x + player.width//2, player.y + 40, RED,
                                           random.uniform(-3, 3), random.uniform(-5, -1)))
            bullet.alive = False
    
    for enemy in enemies:
        if (player.x < enemy.x + enemy.width + 20 and
            player.x + player.width + 20 > enemy.x and
            player.y < enemy.y + enemy.height and
            player.y + player.height > enemy.y):
            
            if player.take_damage(enemy.damage // 4):
                for _ in range(8):
                    particles.append(Particle(player.x, player.y + 40, RED))
    
    player_bullets[:] = [b for b in player_bullets if b.alive]
    enemy_bullets[:] = [b for b in enemy_bullets if b.alive]
    enemies[:] = [e for e in enemies if e.hp > 0]
    
    if len(enemies) == 0 and wave_transition_timer > 60:
        game_state = "WAVE_COMPLETE"
        wave_transition_timer = 0


def draw_ui():
    name_text = font_large.render(f"⚡ {player.name} ⚡", True, NEON_CYAN)
    screen.blit(name_text, (15, 10))
    
    health_bar_x = 15
    health_bar_y = 45
    health_bar_width = 350
    health_bar_height = 28
    
    pygame.draw.rect(screen, NEON_CYAN, (health_bar_x - 2, health_bar_y - 2, health_bar_width + 4, health_bar_height + 4), 3)
    pygame.draw.rect(screen, (20, 20, 40), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    
    health_ratio = max(0, player.health / player.max_health)
    health_color = NEON_GREEN if health_ratio > 0.5 else (NEON_YELLOW if health_ratio > 0.25 else RED)
    fill_width = int(health_bar_width * health_ratio)
    pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, fill_width, health_bar_height))
    
    hp_text = font_medium.render(f"{int(player.health)}/{int(player.max_health)} HP", True, health_color)
    screen.blit(hp_text, (health_bar_x + 10, health_bar_y + 4))
    
    weapon_y = 85
    weapon_text = font_large.render(f"⚔ {player.current_weapon.name}", True, player.current_weapon.color)
    screen.blit(weapon_text, (15, weapon_y))
    
    damage_text = font_medium.render(f"DMG: {int(player.current_weapon.damage)}", True, NEON_ORANGE)
    screen.blit(damage_text, (15, weapon_y + 40))
    
    cooldown_text = font_medium.render(f"READY" if player.current_weapon.can_shoot() else f"RELOAD: {player.current_weapon.current_cooldown}",
                                      True, NEON_GREEN if player.current_weapon.can_shoot() else RED)
    screen.blit(cooldown_text, (200, weapon_y + 40))
    
    wave_text = font_xlarge.render(f"WAVE {wave}", True, NEON_PINK)
    wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH//2, 50))
    
    glow_rect = wave_rect.inflate(30, 30)
    pygame.draw.rect(screen, NEON_PINK, glow_rect, 3)
    screen.blit(wave_text, wave_rect)
    
    score_text = font_large.render(f"💰 SCORE: {score}", True, NEON_YELLOW)
    screen.blit(score_text, (SCREEN_WIDTH - 380, 20))
    
    enemies_text = font_medium.render(f"ENEMIES: {len(enemies)}", True, RED)
    screen.blit(enemies_text, (SCREEN_WIDTH - 380, 70))
    
    controls = "A/D MOVE  |  UP JUMP  |  SPACE ATTACK  |  E SWITCH WEAPON"
    control_text = font_small.render(controls, True, (100, 150, 150))
    screen.blit(control_text, (SCREEN_WIDTH//2 - 350, SCREEN_HEIGHT - 25))


def draw_wave_complete_screen():
    draw_background()
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    complete_text = font_xlarge.render(f"⚡ WAVE {total_waves_completed} CLEAR! ⚡", True, NEON_GREEN)
    complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(complete_text, complete_rect)
    
    score_text = font_large.render(f"💰 SCORE: {score}", True, NEON_YELLOW)
    screen.blit(score_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50))
    
    next_text = font_medium.render("Press SPACE for Next Wave...", True, NEON_CYAN)
    screen.blit(next_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 150))


def draw_game_over():
    draw_background()
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    game_over_text = font_xlarge.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - 280, SCREEN_HEIGHT//2 - 150))
    
    player_text = font_large.render(f"PLAYER: {player.name}", True, NEON_CYAN)
    screen.blit(player_text, (SCREEN_WIDTH//2 - 140, SCREEN_HEIGHT//2 - 20))
    
    waves_text = font_large.render(f"WAVES: {total_waves_completed}", True, NEON_PINK)
    screen.blit(waves_text, (SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 + 30))
    
    score_text = font_large.render(f"SCORE: {score}", True, NEON_YELLOW)
    screen.blit(score_text, (SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 + 80))
    
    restart_text = font_medium.render("Press SPACE to Menu or Q to Quit", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 150))


def reset_game():
    global player, player_bullets, enemy_bullets, enemies, particles, wave, score, game_over, game_state, total_waves_completed, enemy_spawn_timer, wave_transition_timer
    player = Player(player_name_input)
    player_bullets = []
    enemy_bullets = []
    enemies = []
    particles = []
    wave = 1
    score = 0
    game_over = False
    total_waves_completed = 0
    enemy_spawn_timer = 0
    wave_transition_timer = 0
    game_state = "PLAYING"
    spawn_enemy(1)


# ==================== MAIN LOOP ====================
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == "MENU":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_name_input.strip():
                        loading_progress = 0
                        game_state = "LOADING"
                elif event.key == pygame.K_BACKSPACE:
                    player_name_input = player_name_input[:-1]
                elif event.unicode.isprintable() and len(player_name_input) < 15:
                    player_name_input += event.unicode.upper()
        
        elif game_state == "LOADING":
            pass
        
        elif game_state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot(player_bullets)
                if event.key == pygame.K_e:
                    player.switch_weapon()
                if event.key == pygame.K_q:
                    running = False
        
        elif game_state == "WAVE_COMPLETE":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    wave += 1
                    total_waves_completed += 1
                    enemy_spawn_timer = 0
                    wave_transition_timer = 0
                    game_state = "PLAYING"
                    spawn_enemy(wave)
        
        elif game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player_name_input = ""
                    game_state = "MENU"
                    loading_progress = 0
                if event.key == pygame.K_q:
                    running = False
    
    if game_state == "MENU":
        draw_menu_screen()
    
    elif game_state == "LOADING":
        loading_progress = min(100, loading_progress + 2)
        draw_loading_screen()
        if loading_progress >= 100:
            player = Player(player_name_input)
            game_state = "PLAYING"
            spawn_enemy(1)
    
    elif game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        player.update(keys)
        
        enemy_spawn_timer += 1
        wave_transition_timer += 1
        
        if enemy_spawn_timer > 50:
            spawn_enemy(wave)
            enemy_spawn_timer = 0
        
        for bullet in player_bullets:
            bullet.update()
        
        for bullet in enemy_bullets:
            bullet.update()
        
        for enemy in enemies:
            enemy.update(player, enemy_bullets)
        
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
        
        check_collisions()
        
        if player.health <= 0:
            game_over = True
            game_state = "GAME_OVER"
        
        draw_background()
        
        for bullet in player_bullets:
            bullet.draw()
        
        for bullet in enemy_bullets:
            bullet.draw()
        
        for particle in particles:
            particle.draw()
        
        for enemy in enemies:
            enemy.draw()
        
        player.draw()
        draw_ui()
    
    elif game_state == "WAVE_COMPLETE":
        draw_wave_complete_screen()
    
    elif game_state == "GAME_OVER":
        draw_game_over()
    
    pygame.display.flip()

pygame.quit()