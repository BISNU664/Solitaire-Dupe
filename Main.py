import pygame


from Card import CARD_WIDTH, CARD_HEIGHT, CARD_IMAGES, load_card_images
from Game import Game
from ui import Button

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solitaire")

GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
GREY = (180, 180, 180)
YELLOW = (255, 230, 0)

CARD_GAP_X = 125
CARD_GAP_Y = 34

STOCK_POS = (50, 30)
WASTE_POS = (150, 30)
FOUNDATION_POSITIONS = [(700, 30), (800, 30), (900, 30), (1000, 30)]

font = pygame.font.SysFont(None, 30)

load_card_images()

game = Game()

moves = 0
start_time = pygame.time.get_ticks()
final_time = None
last_click_time = 0
DOUBLE_CLICK_TIME = 400  # milliseconds
draw_mode_button = Button(1030, 565, 140, 45, "Draw 3")
restart_button = Button(1030, 620, 140, 45, "Restart")
undo_button = Button(1030, 675, 140, 45, "Undo")
auto_button = Button(1030, 730, 140, 45, "Auto")

selected_stack = []
source_column_index = None
source_pile = None
dragging = False
offset_x = 0
offset_y = 0

stock_rect = pygame.Rect(STOCK_POS[0], STOCK_POS[1], CARD_WIDTH, CARD_HEIGHT)


def draw_placeholder(x, y, label):
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    pygame.draw.rect(screen, GREY, rect, 2, border_radius=8)

    text = font.render(label, True, WHITE)

    text_rect = text.get_rect(center=rect.center)

    screen.blit(text, text_rect)


def get_column_rect(column_index):
    start_x = 50
    start_y = 180
    x = start_x + column_index * CARD_GAP_X
    return pygame.Rect(x, start_y, CARD_WIDTH, 500)


def get_foundation_rect(index):
    x, y = FOUNDATION_POSITIONS[index]
    return pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

def get_waste_card_position(index_from_top):
    visible_waste = game.waste[-game.draw_count:]
    start_x = WASTE_POS[0]
    y = WASTE_POS[1]

    card_index = len(visible_waste) - 1 - index_from_top
    x = start_x + card_index * 18

    return x, y

def draw_stock_and_waste():
    if game.deck:
        screen.blit(CARD_IMAGES["back"], stock_rect)
    else:
        draw_placeholder(STOCK_POS[0], STOCK_POS[1], "RESET")

    draw_placeholder(WASTE_POS[0], WASTE_POS[1], "WASTE")

    visible_waste = game.waste[-game.draw_count:]
    start_x = WASTE_POS[0]
    y = WASTE_POS[1]

    for i, card in enumerate(visible_waste):
        x = start_x + i * 18

        if card not in selected_stack:
            card.draw(screen, font, x, y)



def draw_foundations():
    for i, foundation in enumerate(game.foundations):
        x, y = FOUNDATION_POSITIONS[i]

        suits = ["C", "D", "H", "S"]
        draw_placeholder(x, y, suits[i])

        if foundation and foundation[-1] not in selected_stack:
            foundation[-1].draw(screen, font, x, y)


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            current_time = pygame.time.get_ticks()
            double_click = (current_time - last_click_time) < DOUBLE_CLICK_TIME
            last_click_time = current_time
            selected_stack = []
            source_column_index = None
            source_pile = None

            if draw_mode_button.clicked(mouse_pos):
                if game.draw_count == 1:
                    game.draw_count = 3
                    draw_mode_button.text = "Draw 3"
                else:
                    game.draw_count = 1
                    draw_mode_button.text = "Draw 1"

                continue

            if (restart_button.clicked(mouse_pos)
                or (game.has_won() and Button(530, 415, 140, 45, "Restart").clicked(mouse_pos))
            ):
                game.reset()
                moves = 0
                start_time = pygame.time.get_ticks()
                final_time = None
                dragging = False
                continue

            if undo_button.clicked(mouse_pos):
                if game.undo():
                    moves = max(0, moves - 1)

                selected_stack = []
                source_column_index = None
                source_pile = None
                dragging = False

                continue

            if auto_button.clicked(mouse_pos):
                if game.auto_complete():
                    moves += 1

                selected_stack = []
                source_column_index = None
                source_pile = None
                dragging = False

                continue

            if stock_rect.collidepoint(mouse_pos):
                game.draw_from_stock()

            elif game.waste and pygame.Rect(
                get_waste_card_position(0)[0],
                get_waste_card_position(0)[1],
                CARD_WIDTH,
                CARD_HEIGHT
            ).collidepoint(mouse_pos):

                card = game.waste[-1]
                top_x, top_y = get_waste_card_position(0)

                if double_click:
                    for foundation_index in range(4):
                        if game.move_card_to_foundation(card, foundation_index, "waste"):
                            moves += 1
                            break
                    continue

                selected_stack = [card]
                source_pile = "waste"
                dragging = True

                offset_x = mouse_pos[0] - top_x
                offset_y = mouse_pos[1] - top_y

                card.x = top_x
                card.y = top_y
                card.rect.topleft = (top_x, top_y)

                card.original_x = card.x
                card.original_y = card.y

            elif any(foundation and foundation[-1].rect.collidepoint(mouse_pos) for foundation in game.foundations):
                for foundation_index, foundation in enumerate(game.foundations):
                    if foundation and foundation[-1].rect.collidepoint(mouse_pos):
                        card = foundation[-1]
                        selected_stack = [card]
                        source_pile = "foundation"
                        source_column_index = foundation_index
                        dragging = True

                        offset_x = mouse_pos[0] - card.x
                        offset_y = mouse_pos[1] - card.y

                        card.original_x = card.x
                        card.original_y = card.y

                        break
            else:
                for column_index, column in enumerate(game.tableau):
                    for card_index in range(len(column) - 1, -1, -1):
                        card = column[card_index]

                        if card.face_up and card.rect.collidepoint(mouse_pos):
                            if double_click:
                                for foundation_index in range(4):
                                    if game.move_card_to_foundation(
                                        card,
                                        foundation_index,
                                        "tableau",
                                        column_index
                                    ):
                                        moves += 1
                                        selected_stack = []
                                        dragging = False
                                        break

                                if not any(card in f for f in game.foundations):
                                    pass
                                else:
                                    break
                            selected_stack = column[card_index:]
                            source_column_index = column_index
                            source_pile = "tableau"
                            dragging = True

                            offset_x = mouse_pos[0] - card.x
                            offset_y = mouse_pos[1] - card.y

                            for moving_card in selected_stack:
                                moving_card.original_x = moving_card.x
                                moving_card.original_y = moving_card.y

                            break

                    if selected_stack:
                        break

        if event.type == pygame.MOUSEBUTTONUP:
            if selected_stack:
                moved = False
                first_card = selected_stack[0]

                if len(selected_stack) == 1:
                    for foundation_index in range(4):
                        if first_card.rect.colliderect(get_foundation_rect(foundation_index)):
                            moved = game.move_card_to_foundation(
                                first_card,
                                foundation_index,
                                source_pile,
                                source_column_index,
                            )
                            break

                if not moved:
                    for column_index in range(7):
                        if first_card.rect.colliderect(get_column_rect(column_index)):
                            if source_pile == "tableau":
                                moved = game.move_stack_to_column(
                                    selected_stack,
                                    source_column_index,
                                    column_index,
                                )
                            elif source_pile == "waste":
                                moved = game.move_waste_to_column(first_card, column_index)
                            elif source_pile == "foundation":
                                moved = game.move_foundation_to_column(
                                    first_card,
                                    source_column_index,
                                    column_index
                                )
                            break

                if moved: 
                    moves += 1

                if not moved:
                    for card in selected_stack:
                        card.x = card.original_x
                        card.y = card.original_y
                        card.rect.topleft = (card.x, card.y)

            dragging = False
            selected_stack = []
            source_column_index = None
            source_pile = None

        if event.type == pygame.MOUSEMOTION:
            if dragging and selected_stack:
                mouse_x, mouse_y = event.pos
                new_x = mouse_x - offset_x
                new_y = mouse_y - offset_y

                for i, card in enumerate(selected_stack):
                    card.x = new_x
                    card.y = new_y + i * CARD_GAP_Y
                    card.rect.topleft = (card.x, card.y)

    screen.fill(GREEN)

    draw_stock_and_waste()
    draw_foundations()
    draw_mode_button.draw(screen, font)
    restart_button.draw(screen, font)
    undo_button.draw(screen, font)
    auto_button.draw(screen, font)

    start_x = 50
    start_y = 180

    for column_index, column in enumerate(game.tableau):
        x = start_x + column_index * CARD_GAP_X

        for card_index, card in enumerate(column):
            y = start_y + card_index * CARD_GAP_Y

            if card not in selected_stack:
                card.draw(screen, font, x, y)

    if selected_stack:
        for card in selected_stack:
            card.draw(screen, font, card.x, card.y)

        pygame.draw.rect(screen, YELLOW, selected_stack[0].rect, 4, border_radius=8)

    if game.has_won() and final_time is None:
        final_time = (pygame.time.get_ticks() - start_time) // 1000

    elapsed_seconds = (
        final_time
        if final_time is not None
        else (pygame.time.get_ticks() - start_time) // 1000
    )

    if game.has_won():
        popup_rect = pygame.Rect(400, 250, 400, 250)

        pygame.draw.rect(screen, (240, 240, 240), popup_rect, border_radius=12)
        pygame.draw.rect(screen, (0, 0, 0), popup_rect, 3, border_radius=12)

        title_font = pygame.font.SysFont(None, 60)
        title_text = title_font.render("YOU WIN!", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(600, 310))
        screen.blit(title_text, title_rect)

        time_text = font.render(f"Time: {elapsed_seconds}s", True, (0, 0, 0))
        moves_text = font.render(f"Moves: {moves}", True, (0, 0, 0))

        screen.blit(time_text, (530, 360))
        screen.blit(moves_text, (530, 395))

        popup_restart_button = Button(530, 415, 140, 45, "Restart")
        popup_restart_button.draw(screen, font)

    timer_text = font.render(f"Time: {elapsed_seconds}s", True, WHITE)
    moves_text = font.render(f"Moves: {moves}", True, WHITE)

    screen.blit(timer_text, (300, 55))
    screen.blit(moves_text, (300, 90))
    pygame.display.flip()

pygame.quit()