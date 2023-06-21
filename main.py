import pygame
import random

pygame.font.init()
pygame.init()

# 게임 설정
screen_width = 800
screen_height = 700
play_width = 300
play_height = 600
block_size = 30

top_left_x = (screen_width - play_width) // 2
top_left_y = screen_height - play_height

# 사용자 정의 이벤트 정의
FALL_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(FALL_EVENT, 400)  # 1초마다 이벤트 발생

MOVE_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(MOVE_EVENT, 50)  # 0.2초마다 이벤트 발생

# 테트로미노 형태
S = [
    [".....", ".....", "..00.", ".00..", "....."],
    [".....", "..0..", "..00.", "...0.", "....."],
]

Z = [
    [".....", ".....", ".00..", "..00.", "....."],
    [".....", "..0..", ".00..", ".0...", "....."],
]

I = [
    [".....", "..0..", "..0..", "..0..", "..0.."],
    [".....", "0000.", ".....", ".....", "....."],
]

O = [[".....", ".....", ".00..", ".00..", "....."]]

J = [
    [".....", ".0...", ".000.", ".....", "....."],
    [".....", "..00.", "..0..", "..0..", "....."],
    [".....", ".....", ".000.", "...0.", "....."],
    [".....", "..0..", "..0..", ".00..", "....."],
]

L = [
    [".....", "...0.", ".000.", ".....", "....."],
    [".....", "..0..", "..0..", "..00.", "....."],
    [".....", ".....", ".000.", ".0...", "....."],
    [".....", ".00..", "..0..", "..0..", "....."],
]

T = [
    [".....", "..0..", ".000.", ".....", "....."],
    [".....", "..0..", "..00.", "..0..", "....."],
    [".....", ".....", ".000.", "..0..", "....."],
    [".....", "..0..", ".00..", "..0..", "....."],
]

# 인덱스는 색깔에 대한 것입니다
shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),
    (255, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (128, 0, 128),
]


# 클래스들


class Piece(object):
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # 회전 방향은 네 가지 중 하나입니다


# 게임 보드 설정
def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


# 다음 블록 랜덤 선택
def get_shape():
    return Piece(5, 0, random.choice(shapes))


# 텍스트 표시
def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(
        label,
        (
            top_left_x + play_width / 2 - (label.get_width() / 2),
            top_left_y + play_height / 2 - label.get_height() / 2,
        ),
    )


# 그리드 라인 그리기
def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(
            surface, (128, 128, 128), (sx, sy + i * 30), (sx + play_width, sy + i * 30)
        )  # 가로 선
        for j in range(col):
            pygame.draw.line(
                surface,
                (128, 128, 128),
                (sx + j * 30, sy),
                (sx + j * 30, sy + play_height),
            )  # 세로 선


# 전체 창 업데이트
def draw_window(surface):
    surface.fill((0, 0, 0))
    pygame.font.init()
    font = pygame.font.SysFont("comicsans", 60)
    label = font.render("Tetris", 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface,
                grid[i][j],
                (top_left_x + j * 30, top_left_y + i * 30, 30, 30),
                0,
            )

    draw_grid(surface, 20, 10)
    pygame.draw.rect(
        surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 4
    )
    pygame.display.update()


def main():
    global grid

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()

    auto_fall = True

    while run:
        grid = create_grid(locked_positions)
        keys = pygame.key.get_pressed()

        # 플레이어가 아래 화살표를 누르고 있는 경우 자동 하강을 멈춤
        if keys[pygame.K_DOWN]:
            auto_fall = False
        else:
            auto_fall = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == FALL_EVENT and auto_fall:
                current_piece.y += 1
                if not valid_space(current_piece, grid) and current_piece.y > 0:
                    current_piece.y -= 1
                    change_piece = True
            elif event.type == MOVE_EVENT:
                if keys[pygame.K_DOWN]:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                        change_piece = True
                if keys[pygame.K_LEFT]:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif keys[pygame.K_RIGHT]:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

        shape_pos = convert_shape_format(current_piece)

        # 블록을 추가
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # 블록이 땅에 닿으면 새 블록
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

        draw_window(win)
        pygame.display.update()

        # 종료
        if check_lost(locked_positions):
            run = False

    draw_text_middle("You Lost", 80, (255, 255, 255), win)
    pygame.display.update()
    pygame.time.delay(2000)


def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle("Press any key to play", 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main()

    pygame.display.quit()


# 현재 블록의 위치를 변환
def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


# 블록이 적절한 위치에 있는지 확인
def valid_space(piece, grid):
    accepted_positions = [
        [(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)
    ]
    accepted_positions = [j for sub in accepted_positions for j in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


# 게임이 끝났는지 확인
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tetris")
main_menu(win)  # 메인 메뉴 시작
