import pygame
import random
import sys
import math
from collections import deque

# 初始化pygame
pygame.init()

# 游戏常量
WIDTH, HEIGHT = 1000, 800
CELL_SIZE = 30
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
GOLD = (255, 215, 0)
DARK_RED = (139, 0, 0)
DARK_BLUE = (0, 0, 139)
ORANGE = (255, 165, 0)
SILVER = (192, 192, 192)
UI_BG = (30, 30, 30, 200)
DARK_GREEN = (0, 100, 0)
DARK_PURPLE = (100, 0, 100)

# 创建游戏窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Adventure")
clock = pygame.time.Clock()

# 游戏状态
class GameState:
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    VICTORY = "victory"

# 难度模式
class Difficulty:
    NORMAL = "normal"
    HARD = "hard"

# 小怪物类 - 改进的寻路算法
class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.move_timer = 0
        self.move_interval = 0.4  # 移动间隔（秒）- 加快速度
        self.active = False
        self.move_count = 0
        
    def update(self, dt, player_x, player_y, maze):
        if not self.active:
            return
            
        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            self.move_towards_player(player_x, player_y, maze)
    
    def find_path_to_player(self, player_x, player_y, maze):
        """使用BFS算法找到到玩家的最短路径"""
        if self.x == player_x and self.y == player_y:
            return []
            
        # BFS队列：(x, y, path)
        queue = deque([(self.x, self.y, [])])
        visited = set()
        visited.add((self.x, self.y))
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            x, y, path = queue.popleft()
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # 检查是否到达玩家位置
                if nx == player_x and ny == player_y:
                    return path + [(dx, dy)]
                
                # 检查新位置是否有效且未访问过
                if (0 <= nx < COLS and 0 <= ny < ROWS and 
                    maze[ny][nx] == 0 and 
                    (nx, ny) not in visited):
                    
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + [(dx, dy)]))
        
        # 如果没有找到路径，返回空列表
        return []
    
    def move_towards_player(self, player_x, player_y, maze):
        # 使用BFS找到到玩家的最短路径
        path = self.find_path_to_player(player_x, player_y, maze)
        
        if path:
            # 沿着路径的第一步移动
            dx, dy = path[0]
            new_x, new_y = self.x + dx, self.y + dy
            
            # 确保移动是有效的
            if is_valid_move(maze, new_x, new_y):
                self.x = new_x
                self.y = new_y
                self.move_count += 1
        else:
            # 如果没有找到路径，随机移动
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            valid_directions = []
            
            for dx, dy in directions:
                new_x, new_y = self.x + dx, self.y + dy
                if is_valid_move(maze, new_x, new_y):
                    valid_directions.append((dx, dy))
            
            if valid_directions:
                dx, dy = random.choice(valid_directions)
                self.x += dx
                self.y += dy
                self.move_count += 1
    
    def draw(self, screen):
        if not self.active:
            return
            
        center_x = self.x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.y * CELL_SIZE + CELL_SIZE // 2
        
        # 怪物身体（紫色）
        body_radius = CELL_SIZE // 2 - 4
        pygame.draw.circle(screen, PURPLE, (center_x, center_y), body_radius)
        
        # 怪物眼睛（红色）
        eye_radius = 3
        pygame.draw.circle(screen, RED, (center_x - 4, center_y - 3), eye_radius)
        pygame.draw.circle(screen, RED, (center_x + 4, center_y - 3), eye_radius)
        
        # 怪物嘴巴
        pygame.draw.arc(screen, RED, 
                       (center_x - 6, center_y + 2, 12, 8), 
                       0.2, 2.9, 2)
        
        # 怪物角
        pygame.draw.polygon(screen, RED, [
            (center_x - 3, center_y - body_radius),
            (center_x - 8, center_y - body_radius - 8),
            (center_x, center_y - body_radius - 4)
        ])
        pygame.draw.polygon(screen, RED, [
            (center_x + 3, center_y - body_radius),
            (center_x + 8, center_y - body_radius - 8),
            (center_x, center_y - body_radius - 4)
        ])
        
    def activate(self, player_x, player_y, maze):
        # 怪物出生点为主角出生点 (1, 1)
        self.x = 1
        self.y = 1
        self.active = True

# 更复杂的迷宫生成算法
def generate_maze():
    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    
    def carve_path(x, y):
        maze[y][x] = 0
        
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 1:
                maze[y + dy//2][x + dx//2] = 0
                carve_path(nx, ny)
    
    # 从多个起点生成迷宫，创造更多分支
    start_points = [(1, 1), (COLS-2, ROWS-2), (COLS//2, 1), (1, ROWS//2)]
    for start_x, start_y in start_points:
        if maze[start_y][start_x] == 1:
            carve_path(start_x, start_y)
    
    # 添加一些额外的通道增加复杂度
    for _ in range(ROWS * COLS // 50):
        x = random.randint(1, COLS-2)
        y = random.randint(1, ROWS-2)
        if maze[y][x] == 1:
            neighbors = 0
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 0:
                    neighbors += 1
            if neighbors >= 2:
                maze[y][x] = 0
    
    maze[1][1] = 0
    maze[ROWS-2][COLS-2] = 0
    
    return maze

# 地刺类 - 支持动画和批次管理
class Spike:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = False
        self.animation_progress = 0.0
        self.cycle_timer = 0
        self.visible = False
        self.cycle_completed = False
        
        # 地刺动画参数
        self.rise_duration = 0.8
        self.fall_duration = 0.8
        self.hidden_duration = 1.0
        
    def update(self, dt):
        self.cycle_completed = False
        old_active = self.active
        
        self.cycle_timer += dt
        
        cycle_length = self.rise_duration + self.fall_duration + self.hidden_duration
        cycle_progress = (self.cycle_timer % cycle_length) / cycle_length
        
        if cycle_progress < self.rise_duration / cycle_length:
            # 升起阶段
            phase_progress = cycle_progress / (self.rise_duration / cycle_length)
            self.animation_progress = phase_progress
            self.active = True
            self.visible = True
        elif cycle_progress < (self.rise_duration + self.fall_duration) / cycle_length:
            # 保持阶段
            self.animation_progress = 1.0
            self.active = True
            self.visible = True
        elif cycle_progress < (self.rise_duration + self.fall_duration + self.hidden_duration * 0.2) / cycle_length:
            # 下降阶段
            phase_progress = (cycle_progress - (self.rise_duration + self.fall_duration) / cycle_length) / (self.hidden_duration * 0.2 / cycle_length)
            self.animation_progress = 1.0 - phase_progress
            self.active = True
            self.visible = True
        else:
            # 完全隐藏阶段 - 检测周期完成
            self.animation_progress = 0.0
            self.active = False
            self.visible = False
            
            # 检查是否刚刚完成一个完整周期
            if old_active and not self.active:
                self.cycle_completed = True
    
    def draw(self, screen):
        if not self.visible:
            return
            
        base_height = 6
        spike_height = (CELL_SIZE - 10) * self.animation_progress
        
        # 绘制地刺底座
        base_rect = pygame.Rect(
            self.x * CELL_SIZE + 5,
            self.y * CELL_SIZE + CELL_SIZE - base_height,
            CELL_SIZE - 10,
            base_height
        )
        pygame.draw.rect(screen, (80, 0, 0), base_rect)
        pygame.draw.rect(screen, (120, 0, 0), base_rect, 1)
        
        if self.animation_progress > 0:
            # 绘制地刺（带动画高度）
            spike_color = (
                min(255, 150 + int(105 * self.animation_progress)),
                max(0, 50 - int(50 * self.animation_progress)),
                max(0, 50 - int(50 * self.animation_progress))
            )
            
            spike_points = [
                (self.x * CELL_SIZE + CELL_SIZE // 2, 
                 self.y * CELL_SIZE + CELL_SIZE - base_height - spike_height),
                (self.x * CELL_SIZE + 8, 
                 self.y * CELL_SIZE + CELL_SIZE - base_height),
                (self.x * CELL_SIZE + CELL_SIZE - 8, 
                 self.y * CELL_SIZE + CELL_SIZE - base_height)
            ]
            pygame.draw.polygon(screen, spike_color, spike_points)
            pygame.draw.polygon(screen, (200, 0, 0), spike_points, 1)
            
            # 地刺发光效果
            if self.animation_progress > 0.7:
                glow_alpha = int(100 * (self.animation_progress - 0.7) / 0.3)
                glow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.polygon(glow_surface, (*RED, glow_alpha), [
                    (CELL_SIZE // 2, CELL_SIZE - base_height - spike_height),
                    (8, CELL_SIZE - base_height),
                    (CELL_SIZE - 8, CELL_SIZE - base_height)
                ])
                screen.blit(glow_surface, (self.x * CELL_SIZE, self.y * CELL_SIZE))

# 生成新的随机地刺位置
def generate_random_spikes(maze, player_x, player_y, count=30):
    spikes = []
    attempts = 0
    max_attempts = count * 15
    
    # 计算可用的路径格子数量
    available_cells = 0
    for y in range(ROWS):
        for x in range(COLS):
            if (maze[y][x] == 0 and 
                (x, y) != (1, 1) and 
                (x, y) != (COLS-2, ROWS-2)):
                available_cells += 1
    
    # 如果可用格子太少，减少地刺数量
    actual_count = min(count, available_cells - 5)
    
    while len(spikes) < actual_count and attempts < max_attempts:
        x = random.randint(1, COLS-2)
        y = random.randint(1, ROWS-2)
        
        # 检查位置是否有效
        if (maze[y][x] == 0 and 
            (x, y) != (1, 1) and 
            (x, y) != (COLS-2, ROWS-2) and
            (x, y) != (player_x, player_y) and
            not any(spike.x == x and spike.y == y for spike in spikes)):
            
            # 计算与主角的距离
            distance_to_player = math.sqrt((x - player_x)**2 + (y - player_y)**2)
            
            # 允许出现在主角附近，但不能太近（至少1格距离）
            if distance_to_player >= 1.2:
                spikes.append(Spike(x, y))
        
        attempts += 1
    
    return spikes

# 绘制半透明UI背景
def draw_ui_panel(rect, alpha=200):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((30, 30, 30, alpha))
    screen.blit(s, (rect.x, rect.y))
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)

# 绘制按钮
def draw_button(text, rect, color, hover_color, is_hovered):
    button_color = hover_color if is_hovered else color
    pygame.draw.rect(screen, button_color, rect, border_radius=12)
    pygame.draw.rect(screen, WHITE, rect, 3, border_radius=12)
    
    font = pygame.font.SysFont("arial", 28, bold=True)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

# 绘制主角（年轻冒险者）
def draw_player(x, y):
    center_x = x * CELL_SIZE + CELL_SIZE // 2
    center_y = y * CELL_SIZE + CELL_SIZE // 2
    
    # 身体（绿色冒险服）
    body_rect = pygame.Rect(x * CELL_SIZE + 6, y * CELL_SIZE + 12, CELL_SIZE - 12, CELL_SIZE - 16)
    pygame.draw.rect(screen, (0, 150, 0), body_rect, border_radius=4)
    
    # 头部（年轻肤色）
    head_radius = CELL_SIZE // 3
    head_center = (center_x, y * CELL_SIZE + 8 + head_radius)
    pygame.draw.circle(screen, (255, 220, 180), head_center, head_radius)
    
    # 头发（棕色短发）
    hair_rect = pygame.Rect(center_x - head_radius + 2, y * CELL_SIZE + 6, head_radius * 2 - 4, head_radius - 2)
    pygame.draw.ellipse(screen, (101, 67, 33), hair_rect)
    
    # 眼睛（更有活力）
    eye_y = y * CELL_SIZE + 10
    pygame.draw.circle(screen, (0, 0, 139), (center_x - 4, eye_y), 3)
    pygame.draw.circle(screen, (0, 0, 139), (center_x + 4, eye_y), 3)
    pygame.draw.circle(screen, WHITE, (center_x - 3, eye_y - 1), 1)
    pygame.draw.circle(screen, WHITE, (center_x + 5, eye_y - 1), 1)
    
    # 微笑
    pygame.draw.arc(screen, (200, 0, 0), 
                   (center_x - 6, eye_y + 2, 12, 8), 
                   0.2, 2.9, 2)
    
    # 背包
    pack_rect = pygame.Rect(x * CELL_SIZE + 4, y * CELL_SIZE + 18, 8, CELL_SIZE - 22)
    pygame.draw.rect(screen, (139, 69, 19), pack_rect, border_radius=2)
    pygame.draw.rect(screen, (101, 67, 33), pack_rect, 1, border_radius=2)
    
    # 剑
    sword_length = CELL_SIZE - 10
    pygame.draw.line(screen, SILVER, 
                    (center_x + 10, center_y - sword_length//2),
                    (center_x + 10, center_y + sword_length//2), 3)
    
    # 剑柄
    pygame.draw.rect(screen, (139, 69, 19), 
                    (center_x + 7, center_y - 2, 6, 4))
    
    # 剑格
    pygame.draw.rect(screen, GOLD, 
                    (center_x + 5, center_y - 1, 10, 2))
    
    # 剑刃尖端
    pygame.draw.polygon(screen, SILVER, [
        (center_x + 10, center_y - sword_length//2),
        (center_x + 13, center_y - sword_length//2 + 5),
        (center_x + 7, center_y - sword_length//2 + 5)
    ])

# 绘制宝箱
def draw_treasure_chest(x, y):
    chest_rect = pygame.Rect(x * CELL_SIZE + 5, y * CELL_SIZE + 8, CELL_SIZE - 10, CELL_SIZE - 16)
    
    # 宝箱主体
    pygame.draw.rect(screen, (139, 69, 19), chest_rect, border_radius=3)
    
    # 宝箱金属边
    pygame.draw.rect(screen, GOLD, chest_rect, 2, border_radius=3)
    
    # 宝箱盖子
    lid_rect = pygame.Rect(x * CELL_SIZE + 3, y * CELL_SIZE + 5, CELL_SIZE - 6, 8)
    pygame.draw.rect(screen, (160, 82, 45), lid_rect, border_radius=2)
    pygame.draw.rect(screen, GOLD, lid_rect, 2, border_radius=2)
    
    # 宝箱锁
    lock_rect = pygame.Rect(x * CELL_SIZE + CELL_SIZE//2 - 3, y * CELL_SIZE + 10, 6, 8)
    pygame.draw.rect(screen, GOLD, lock_rect)
    pygame.draw.circle(screen, GOLD, (x * CELL_SIZE + CELL_SIZE//2, y * CELL_SIZE + 18), 3)

# 绘制迷宫
def draw_maze(maze, spikes, monster=None):
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if maze[y][x] == 1:
                # 墙壁纹理
                pygame.draw.rect(screen, BLUE, rect)
                pygame.draw.rect(screen, (0, 80, 200), rect, 2)
                # 墙壁砖块效果
                for i in range(0, CELL_SIZE, 6):
                    for j in range(0, CELL_SIZE, 6):
                        if (i//6 + j//6) % 2 == 0:
                            pygame.draw.rect(screen, (0, 100, 220), 
                                           (x * CELL_SIZE + i, y * CELL_SIZE + j, 3, 3))
            else:
                pygame.draw.rect(screen, BLACK, rect)
                pygame.draw.rect(screen, (30, 30, 30), rect, 1)
    
    # 绘制地刺
    for spike in spikes:
        spike.draw(screen)
    
    # 绘制怪物
    if monster:
        monster.draw(screen)
    
    # 绘制终点宝箱
    draw_treasure_chest(COLS-2, ROWS-2)

# 检查移动是否有效
def is_valid_move(maze, x, y):
    return 0 <= x < COLS and 0 <= y < ROWS and maze[y][x] == 0

# 绘制开始菜单
def draw_menu(normal_hovered, hard_hovered):
    # 背景渐变
    for y in range(HEIGHT):
        color_value = max(20, 50 - y // 20)
        pygame.draw.line(screen, (color_value, color_value, color_value), (0, y), (WIDTH, y))
    
    # 标题
    title_font = pygame.font.SysFont("arial", 80, bold=True)
    title_text = title_font.render("MAZE ADVENTURE", True, YELLOW)
    title_shadow = title_font.render("MAZE ADVENTURE", True, (100, 100, 0))
    
    # 标题阴影效果
    screen.blit(title_shadow, (WIDTH//2 - title_text.get_width()//2 + 3, HEIGHT//4 + 3))
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
    
    # 副标题
    subtitle_font = pygame.font.SysFont("arial", 36)
    subtitle_text = subtitle_font.render("Choose Your Challenge", True, WHITE)
    screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//4 + 90))
    
    # 按钮区域背景
    button_area = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 50, 400, 200)
    draw_ui_panel(button_area, 180)
    
    # 难度选项按钮
    normal_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 60)
    hard_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 80, 300, 60)
    
    draw_button("NORMAL MODE", normal_button, DARK_GREEN, GREEN, normal_hovered)
    draw_button("HARD MODE", hard_button, DARK_PURPLE, PURPLE, hard_hovered)
    
    # 模式说明
    desc_font = pygame.font.SysFont("arial", 18)
    desc_lines = [
        "Normal: Classic maze with spikes only",
        "Hard: Advanced maze with chasing monster"
    ]
    
    for i, line in enumerate(desc_lines):
        desc_text = desc_font.render(line, True, WHITE)
        screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT//2 + 160 + i * 25))
    
    # 操作提示
    hint_font = pygame.font.SysFont("arial", 16)
    hint_text = hint_font.render("Click to select your challenge", True, YELLOW)
    screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT - 50))

# 主游戏函数
def main():
    # 游戏状态
    game_state = GameState.MENU
    difficulty = None
    
    # 游戏变量
    maze = None
    spikes = []
    monster = None
    player_x, player_y = 1, 1
    game_over = False
    win = False
    move_delay = 0
    move_interval = 6
    need_respawn = False
    player_move_count = 0
    
    # 菜单选择
    normal_hovered = False
    hard_hovered = False
    
    last_time = pygame.time.get_ticks()
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0
        last_time = current_time
        
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 菜单状态处理
                if game_state == GameState.MENU:
                    normal_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 60)
                    hard_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 80, 300, 60)
                    
                    if normal_button.collidepoint(mouse_pos):
                        difficulty = Difficulty.NORMAL
                        game_state = GameState.PLAYING
                        # 初始化游戏
                        maze = generate_maze()
                        player_x, player_y = 1, 1
                        spikes = generate_random_spikes(maze, player_x, player_y, 30)
                        monster = None  # Normal模式没有怪物
                        game_over = False
                        win = False
                        player_move_count = 0
                    
                    elif hard_button.collidepoint(mouse_pos):
                        difficulty = Difficulty.HARD
                        game_state = GameState.PLAYING
                        # 初始化游戏
                        maze = generate_maze()
                        player_x, player_y = 1, 1
                        spikes = generate_random_spikes(maze, player_x, player_y, 30)
                        monster = Monster(1, 1)  # Hard模式有怪物，出生在主角位置
                        game_over = False
                        win = False
                        player_move_count = 0
            
            elif event.type == pygame.KEYDOWN:
                # 游戏结束或胜利状态处理
                if game_state in [GameState.GAME_OVER, GameState.VICTORY]:
                    if event.key == pygame.K_r:  # 重新开始当前关卡
                        game_state = GameState.PLAYING
                        maze = generate_maze()
                        player_x, player_y = 1, 1
                        spikes = generate_random_spikes(maze, player_x, player_y, 30)
                        if difficulty == Difficulty.HARD:
                            monster = Monster(1, 1)  # 怪物出生在主角位置
                        else:
                            monster = None
                        game_over = False
                        win = False
                        player_move_count = 0
                    
                    elif event.key == pygame.K_h:  # 切换到Hard模式
                        difficulty = Difficulty.HARD
                        game_state = GameState.PLAYING
                        maze = generate_maze()
                        player_x, player_y = 1, 1
                        spikes = generate_random_spikes(maze, player_x, player_y, 30)
                        monster = Monster(1, 1)  # 怪物出生在主角位置
                        game_over = False
                        win = False
                        player_move_count = 0
                    
                    elif event.key == pygame.K_n:  # 切换到Normal模式
                        difficulty = Difficulty.NORMAL
                        game_state = GameState.PLAYING
                        maze = generate_maze()
                        player_x, player_y = 1, 1
                        spikes = generate_random_spikes(maze, player_x, player_y, 30)
                        monster = None
                        game_over = False
                        win = False
                        player_move_count = 0
        
        # 更新菜单悬停状态
        if game_state == GameState.MENU:
            normal_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 60)
            hard_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 80, 300, 60)
            normal_hovered = normal_button.collidepoint(mouse_pos)
            hard_hovered = hard_button.collidepoint(mouse_pos)
        
        # 游戏进行中
        if game_state == GameState.PLAYING:
            # 更新地刺动画并检查是否完成周期
            all_cycle_completed = True
            for spike in spikes:
                spike.update(dt)
                if not spike.cycle_completed:
                    all_cycle_completed = False
            
            # 当地刺批次完成完整周期后重新生成
            if all_cycle_completed and len(spikes) > 0 and not need_respawn:
                need_respawn = True
            
            # 在下一批地刺开始前重新生成位置
            if need_respawn and all(not spike.active and not spike.visible for spike in spikes):
                spikes = generate_random_spikes(maze, player_x, player_y, 30)
                need_respawn = False
            
            # 更新怪物（只在Hard模式）
            if monster and difficulty == Difficulty.HARD:
                # 玩家移动5格后激活怪物
                if not monster.active and player_move_count >= 5:
                    monster.activate(player_x, player_y, maze)
                
                # 怪物一直在移动（即使没有激活也会更新位置）
                monster.update(dt, player_x, player_y, maze)
                
                # 检查怪物碰撞
                if monster.active and monster.x == player_x and monster.y == player_y:
                    game_over = True
                    game_state = GameState.GAME_OVER
            
            # 处理连续移动
            keys = pygame.key.get_pressed()
            move_delay += 1
            
            if move_delay >= move_interval:
                new_x, new_y = player_x, player_y
                
                if keys[pygame.K_UP]:
                    new_y -= 1
                elif keys[pygame.K_DOWN]:
                    new_y += 1
                elif keys[pygame.K_LEFT]:
                    new_x -= 1
                elif keys[pygame.K_RIGHT]:
                    new_x += 1
                
                if is_valid_move(maze, new_x, new_y) and (new_x, new_y) != (player_x, player_y):
                    player_x, player_y = new_x, new_y
                    move_delay = 0
                    player_move_count += 1
                    
                    # 检查是否到达终点
                    if player_x == COLS-2 and player_y == ROWS-2:
                        win = True
                        game_state = GameState.VICTORY
                    
                    # 检查是否碰到活跃的地刺
                    for spike in spikes:
                        if spike.active and spike.x == player_x and spike.y == player_y:
                            game_over = True
                            game_state = GameState.GAME_OVER
        
        # 绘制游戏
        screen.fill(BLACK)
        
        if game_state == GameState.MENU:
            draw_menu(normal_hovered, hard_hovered)
        
        elif game_state == GameState.PLAYING:
            draw_maze(maze, spikes, monster)
            draw_player(player_x, player_y)
            
            # 显示关卡信息
            level_font = pygame.font.SysFont("arial", 20)
            mode_text = "Normal" if difficulty == Difficulty.NORMAL else "Hard"
            level_text = level_font.render(f"Mode: {mode_text}", True, WHITE)
            screen.blit(level_text, (10, 10))
            
            # 显示怪物激活倒计时（Hard模式）
            if difficulty == Difficulty.HARD and monster and not monster.active:
                count_font = pygame.font.SysFont("arial", 16)
                count_text = count_font.render(f"Monster activates in: {5 - player_move_count} moves", True, YELLOW)
                screen.blit(count_text, (10, 35))
        
        # 显示游戏结束状态
        elif game_state == GameState.GAME_OVER:
            draw_maze(maze, spikes, monster)
            draw_player(player_x, player_y)
            
            panel_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 120, 500, 240)
            draw_ui_panel(panel_rect)
            
            font_large = pygame.font.SysFont("arial", 72, bold=True)
            font_medium = pygame.font.SysFont("arial", 28)
            
            text = font_large.render("GAME OVER", True, RED)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 80))
            
            restart_text = font_medium.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
            
            if difficulty == Difficulty.NORMAL:
                switch_text = font_medium.render("Press H for Hard Mode", True, YELLOW)
            else:
                switch_text = font_medium.render("Press N for Normal Mode", True, YELLOW)
            screen.blit(switch_text, (WIDTH//2 - switch_text.get_width()//2, HEIGHT//2 + 60))
        
        # 显示胜利状态
        elif game_state == GameState.VICTORY:
            draw_maze(maze, spikes, monster)
            draw_player(player_x, player_y)
            
            panel_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 120, 500, 240)
            draw_ui_panel(panel_rect)
            
            font_large = pygame.font.SysFont("arial", 72, bold=True)
            font_medium = pygame.font.SysFont("arial", 28)
            
            text = font_large.render("VICTORY!", True, GREEN)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 80))
            
            restart_text = font_medium.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
            
            if difficulty == Difficulty.NORMAL:
                switch_text = font_medium.render("Press H for Hard Mode", True, YELLOW)
            else:
                switch_text = font_medium.render("Press N for Normal Mode", True, YELLOW)
            screen.blit(switch_text, (WIDTH//2 - switch_text.get_width()//2, HEIGHT//2 + 60))
        
        # 显示操作说明
        if game_state == GameState.PLAYING:
            controls_bg = pygame.Rect(5, HEIGHT - 35, WIDTH - 10, 30)
            draw_ui_panel(controls_bg, 150)
            
            font = pygame.font.SysFont("arial", 16)
            controls_text = font.render("Arrow Keys: Move | Avoid Spikes" + 
                                      (" | Escape Monster" if difficulty == Difficulty.HARD else ""), 
                                      True, WHITE)
            screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 28))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()