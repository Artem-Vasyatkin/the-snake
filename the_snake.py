import random

import pygame as pg

# Константы для размеров поля и сетки.
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения.
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный.
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки.
BORDER_COLOR = (93, 216, 228)

# Цвет яблока.
APPLE_COLOR = (255, 0, 0)

# Цвет змейки.
SNAKE_COLOR = (0, 255, 0)

# Цвет текста.
TEXT_COLOR = (255, 255, 255)
HELP_TEXT_COLOR = (200, 200, 200)

# Скорость движения змейки.
BASE_SPEED = 10
MIN_SPEED = 5
MAX_SPEED = 20
SPEED_STEP = 1


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw_cell(self, position, color, border_color=None):
        """Метод для отрисовки ячейки."""
        rect = pg.Rect(position[0], position[1], GRID_SIZE, GRID_SIZE)
        pg.draw.rect(screen, color, rect)
        if border_color is not None:
            pg.draw.rect(screen, border_color, rect, 1)

    def draw(self):
        """Метод отрисовки объектов."""
        raise NotImplementedError(
            'Метод draw() должен быть переопределен в дочернем классе.'
        )


class Apple(GameObject):
    """Отвечает за появление яблока в случайной позиции."""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        super().__init__(body_color)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Генерирует случайную позицию яблока, не занятую змейкой."""
        while True:
            position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if (
                position not in occupied_positions
                and not is_under_text(position)
            ):
                self.position = position
                break

    def draw(self):
        """Отрисовка яблока на игровом поле."""
        self.draw_cell(self.position, self.body_color, BORDER_COLOR)


def is_under_text(position):
    """Проверяет, находится ли позиция под областью текста."""
    x, y = position
    return (
        (x < 200 and y < 80)
        or (x > SCREEN_WIDTH - 200 and y < 110)
        or (x > SCREEN_WIDTH - 250 and y > SCREEN_HEIGHT - 30)
    )


class Snake(GameObject):
    """Отвечает за движение, рост, столкновения и отрисовку."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализация змейки."""
        super().__init__(body_color)
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self, new_direction):
        """Обновляет текущее направление движения."""
        if new_direction is not None:
            opposite_direction = (-self.direction[0], -self.direction[1])
            if new_direction != opposite_direction:
                self.direction = new_direction

    def move(self):
        """Перемещает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        new_head = (
            (head_x + direction_x) % SCREEN_WIDTH,
            (head_y + direction_y) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        """
        Сбрасывает змейку в начальное состояние.
        Используется при столкновении с собой.
        """
        self.length = 1
        start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        while is_under_text(start_pos):
            start_pos = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
        self.positions = [start_pos]
        directions = [
            (GRID_SIZE, 0),
            (-GRID_SIZE, 0),
            (0, GRID_SIZE),
            (0, -GRID_SIZE)
        ]
        self.direction = random.choice(directions)

    def draw(self):
        """Отрисовка змейки на игровом поле."""
        for position in self.positions:
            self.draw_cell(position, self.body_color, BORDER_COLOR)


def handle_quit_event():
    """Выход из игры."""
    pg.quit()
    raise SystemExit


def handle_direction_key(event, snake):
    """Управление змейкой."""
    if event.key == pg.K_UP:
        snake.update_direction((0, -GRID_SIZE))
    elif event.key == pg.K_DOWN:
        snake.update_direction((0, GRID_SIZE))
    elif event.key == pg.K_LEFT:
        snake.update_direction((-GRID_SIZE, 0))
    elif event.key == pg.K_RIGHT:
        snake.update_direction((GRID_SIZE, 0))


def handle_speed_key(event, current_speed):
    """Изменение скорости змейки."""
    new_speed = current_speed
    if event.key == pg.K_EQUALS or event.key == pg.K_PLUS:
        new_speed = min(current_speed + SPEED_STEP, MAX_SPEED)
    elif event.key == pg.K_MINUS:
        new_speed = max(current_speed - SPEED_STEP, MIN_SPEED)
    return new_speed


def handle_keys(snake, current_speed):
    """Обрабатывает нажатия клавиш."""
    new_speed = current_speed

    for event in pg.event.get():
        if event.type == pg.QUIT:
            handle_quit_event()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                handle_quit_event()
            elif event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                handle_direction_key(event, snake)
            elif event.key in (pg.K_EQUALS, pg.K_PLUS, pg.K_MINUS):
                new_speed = handle_speed_key(event, current_speed)

    return new_speed


def show_info(speed, score):
    """Отображает информацию на экране: скорость, счет, управление."""
    font = pg.font.SysFont('Arial', 18)
    font_small = pg.font.SysFont('Arial', 14)

    s = pg.Surface((200, 80))
    s.set_alpha(180)
    s.fill(BOARD_BACKGROUND_COLOR)
    screen.blit(s, (0, 0))

    s2 = pg.Surface((200, 110))
    s2.set_alpha(180)
    s2.fill(BOARD_BACKGROUND_COLOR)
    screen.blit(s2, (SCREEN_WIDTH - 200, 0))

    s3 = pg.Surface((250, 30))
    s3.set_alpha(180)
    s3.fill(BOARD_BACKGROUND_COLOR)
    screen.blit(s3, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 30))

    speed_text = font.render(f'Скорость: {speed}', True, TEXT_COLOR)
    score_text = font.render(f'Счет: {score}', True, TEXT_COLOR)
    screen.blit(speed_text, (10, 10))
    screen.blit(score_text, (10, 35))

    help_lines = [
        'Управление:',
        '↑ ↓ ← → - движение',
        '+ / - - скорость',
        'ESC - выход'
    ]

    y_offset = 10
    for line in help_lines:
        text = font_small.render(line, True, HELP_TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.topright = (SCREEN_WIDTH - 10, y_offset)
        screen.blit(text, text_rect)
        y_offset += 20

    reset_hint = font_small.render(
        'Скорость сбрасывается при столкновении',
        True,
        HELP_TEXT_COLOR
    )
    reset_hint_rect = reset_hint.get_rect()
    reset_hint_rect.bottomright = (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)
    screen.blit(reset_hint, reset_hint_rect)


def main():
    """Реализация pygame."""
    global screen

    pg.init()

    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pg.display.set_caption('Змейка (ESC - выход, +/- - скорость)')
    clock = pg.time.Clock()

    snake = Snake()
    apple = Apple(snake.positions)
    speed = BASE_SPEED
    score = 0

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(speed)

        speed = handle_keys(snake, speed)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            score += 1
            apple.randomize_position(snake.positions)

        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            speed = BASE_SPEED
            score = 0
            screen.fill(BOARD_BACKGROUND_COLOR)

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()

        show_info(speed, score)
        pg.display.update()


if __name__ == '__main__':
    main()
