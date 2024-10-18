import pygame
import random
import math
import copy

# Inicializar Pygame
pygame.init()

# Configuración del juego
BOARD_SIZE = 8  # Tamaño del tablero (8x8)
CELL_SIZE = 60  # Tamaño de cada celda en píxeles
SCREEN_SIZE = CELL_SIZE * BOARD_SIZE  # Tamaño total de la pantalla
FPS = 5  # Fotogramas por segundo

# Definir colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
GRAY = (169, 169, 169)

# Representación de las fichas
EMPTY = 0
BLACK_PLAYER = 1
WHITE_PLAYER = -1

# Inicializar la pantalla
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption('Reversi con IA')

# Fuente para mostrar el texto en pantalla
font = pygame.font.SysFont(None, 36)

# Función personalizada para dibujar un rectángulo con bordes redondeados
def draw_rounded_rect(surface, color, rect, corner_radius):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

# Función para inicializar el tablero de juego
def initialize_board():
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    board[3][3], board[4][4] = WHITE_PLAYER, WHITE_PLAYER
    board[3][4], board[4][3] = BLACK_PLAYER, BLACK_PLAYER
    return board

# Dibuja el tablero y las fichas en la pantalla
def draw_board(board, valid_moves=[]):
    screen.fill(GREEN)
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            if board[x][y] == BLACK_PLAYER:
                pygame.draw.circle(screen, BLACK, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 4)
            elif board[x][y] == WHITE_PLAYER:
                pygame.draw.circle(screen, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 4)

    for move in valid_moves:
        pygame.draw.circle(screen, GRAY, (move[0] * CELL_SIZE + CELL_SIZE // 2, move[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 4)

    pygame.display.flip()

# Verifica si una posición está dentro del tablero
def is_on_board(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

# Encuentra todas las fichas que se capturarían para una jugada dada
def get_flipped_pieces(board, color, x, y):
    if board[x][y] != EMPTY or not is_on_board(x, y):
        return []

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    flipped = []

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        current_flipped = []
        while is_on_board(nx, ny) and board[nx][ny] == -color:
            current_flipped.append((nx, ny))
            nx, ny = nx + dx, ny + dy
        if is_on_board(nx, ny) and board[nx][ny] == color:
            flipped.extend(current_flipped)

    return flipped

# Aplica una jugada en el tablero
def apply_move(board, color, x, y):
    flipped_pieces = get_flipped_pieces(board, color, x, y)
    if not flipped_pieces:
        return False
    board[x][y] = color
    for fx, fy in flipped_pieces:
        board[fx][fy] = color
    return True

# Obtiene todos los movimientos válidos para el jugador actual
def get_valid_moves(board, color):
    return [(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE) if board[x][y] == EMPTY and get_flipped_pieces(board, color, x, y)]

# Evalúa el tablero, devuelve un puntaje a favor del color especificado
def evaluate_board(board, color):
    return sum(row.count(color) - row.count(-color) for row in board)

# Implementación del algoritmo Minimax con poda alfa-beta
def minimax(board, depth, alpha, beta, maximizing_player, color):
    valid_moves = get_valid_moves(board, color)
    if depth == 0 or not valid_moves:
        return evaluate_board(board, color)

    if maximizing_player:
        max_eval = -math.inf
        for move in valid_moves:
            new_board = copy.deepcopy(board)
            apply_move(new_board, color, move[0], move[1])
            eval = minimax(new_board, depth - 1, alpha, beta, False, -color)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in valid_moves:
            new_board = copy.deepcopy(board)
            apply_move(new_board, color, move[0], move[1])
            eval = minimax(new_board, depth - 1, alpha, beta, True, -color)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# Determina la mejor jugada usando Minimax
def best_move(board, color, depth):
    best_score = -math.inf
    move_to_make = None
    for move in get_valid_moves(board, color):
        new_board = copy.deepcopy(board)
        apply_move(new_board, color, move[0], move[1])
        score = minimax(new_board, depth - 1, -math.inf, math.inf, False, -color)
        if score > best_score:
            best_score = score
            move_to_make = move
    return move_to_make

# Determina el ganador al finalizar el juego
def determine_winner(board):
    black_score = sum(row.count(BLACK_PLAYER) for row in board)
    white_score = sum(row.count(WHITE_PLAYER) for row in board)
    if black_score > white_score:
        return "¡Jugador Negro gana!", BLACK
    elif white_score > black_score:
        return "¡IA (Blanco) gana!", WHITE
    else:
        return "¡Empate!", GRAY

# Muestra la pantalla del ganador
def display_winner_screen(message, color):
    screen.fill(GREEN)
    winner_text = font.render(message, True, color)
    screen.blit(winner_text, (SCREEN_SIZE // 2 - winner_text.get_width() // 2, SCREEN_SIZE // 2))
    pygame.display.flip()
    pygame.time.wait(3000)  # Espera 3 segundos antes de cerrar el juego

# Pantalla de selección de color
def display_color_selection():
    screen.fill(GREEN)
    title_text = font.render("Selecciona tu color", True, WHITE)
    screen.blit(title_text, (SCREEN_SIZE // 2 - title_text.get_width() // 2, SCREEN_SIZE // 4))

    black_button = pygame.Rect(SCREEN_SIZE // 2 - 170, SCREEN_SIZE // 2 - 30, 120, 60)
    white_button = pygame.Rect(SCREEN_SIZE // 2 + 50, SCREEN_SIZE // 2 - 30, 120, 60)
    random_button = pygame.Rect(SCREEN_SIZE // 2 - 60, SCREEN_SIZE // 2 + 100, 160, 60)

    draw_rounded_rect(screen, BLACK, black_button, 15)
    draw_rounded_rect(screen, WHITE, white_button, 15)
    draw_rounded_rect(screen, GRAY, random_button, 15)

    black_text = font.render("Negro", True, WHITE)
    white_text = font.render("Blanco", True, BLACK)
    random_text = font.render("Aleatorio", True, WHITE)

    screen.blit(black_text, (black_button.centerx - black_text.get_width() // 2, black_button.centery - black_text.get_height() // 2))
    screen.blit(white_text, (white_button.centerx - white_text.get_width() // 2, white_button.centery - white_text.get_height() // 2))
    screen.blit(random_text, (random_button.centerx - random_text.get_width() // 2, random_button.centery - random_text.get_height() // 2))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if black_button.collidepoint(x, y):
                    return BLACK_PLAYER
                elif white_button.collidepoint(x, y):
                    return WHITE_PLAYER
                elif random_button.collidepoint(x, y):
                    selected_color = random.choice([BLACK_PLAYER, WHITE_PLAYER])
                    
                    # Mostrar mensaje del color seleccionado
                    color_text = "Negro" if selected_color == BLACK_PLAYER else "Blanco"
                    message = font.render(f"Color aleatorio: {color_text}", True, WHITE)
                    screen.blit(message, (SCREEN_SIZE // 2 - message.get_width() // 2, SCREEN_SIZE // 2 + 170))
                    pygame.display.flip()
                    pygame.time.wait(1000)  # Espera un segundo para mostrar el mensaje
                    
                    return selected_color

# Código principal
def main():
    clock = pygame.time.Clock()
    board = initialize_board()
    player_color = display_color_selection()
    if player_color is None:
        return
    ai_color = -player_color
    current_color = BLACK_PLAYER

    while True:
        draw_board(board)
        valid_moves = get_valid_moves(board, current_color)

        if not valid_moves:
            current_color = -current_color
            if not get_valid_moves(board, current_color):
                break
            continue

        if current_color == player_color:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    row, col = x // CELL_SIZE, y // CELL_SIZE
                    if (row, col) in valid_moves:
                        apply_move(board, current_color, row, col)
                        current_color = ai_color
        else:
            move = best_move(board, ai_color, 3)
            if move:
                apply_move(board, ai_color, move[0], move[1])
            current_color = player_color

        draw_board(board, valid_moves)
        pygame.display.flip()
        clock.tick(FPS)

    # Mostrar el mensaje del ganador
    winner_message, winner_color = determine_winner(board)
    display_winner_screen(winner_message, winner_color)

    pygame.quit()

if __name__ == "__main__":
    main()
