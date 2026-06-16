import os
import pygame

CARD_WIDTH = 90
CARD_HEIGHT = 130

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
BLUE = (40, 80, 180)

VALUE_RANKS = {
    "A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13,
}

CARD_IMAGES = {}


def load_card_images():
    suits = ["S", "H", "D", "C"]
    values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    for suit in suits:
        for value in values:
            filename = f"{value}{suit}.png"
            path = os.path.join("assets", "cards", filename)

            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))

            CARD_IMAGES[f"{value}{suit}"] = image

    back_path = os.path.join("assets", "cards", "back.png")
    back_image = pygame.image.load(back_path).convert_alpha()
    back_image = pygame.transform.scale(back_image, (CARD_WIDTH, CARD_HEIGHT))

    CARD_IMAGES["back"] = back_image


class Card:
    def __init__(self, suit, value, face_up=False):
        self.suit = suit
        self.value = value
        self.face_up = face_up

        self.x = 0
        self.y = 0
        self.original_x = 0
        self.original_y = 0

        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)

    def colour(self):
        return "red" if self.suit in ["H", "D"] else "black"

    def rank(self):
        return VALUE_RANKS[self.value]

    def draw(self, screen, font, x, y):
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)

        if CARD_IMAGES:
            if self.face_up:
                image = CARD_IMAGES[f"{self.value}{self.suit}"]
            else:
                image = CARD_IMAGES["back"]

            screen.blit(image, self.rect)
            return

        # Fallback if images do not load
        if self.face_up:
            pygame.draw.rect(screen, WHITE, self.rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)

            text_colour = RED if self.colour() == "red" else BLACK
            text = font.render(f"{self.value}{self.suit}", True, text_colour)
            screen.blit(text, (x + 10, y + 10))
        else:
            pygame.draw.rect(screen, BLUE, self.rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)