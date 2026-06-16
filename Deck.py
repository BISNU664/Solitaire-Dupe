import random
from Card import Card

SUITS = ["S", "H", "D", "C"]
VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def create_deck():
    deck = []

    for suit in SUITS:
        for value in VALUES:
            deck.append(Card(suit, value))

    random.shuffle(deck)
    return deck


def deal_tableau(deck):
    tableau = [[] for _ in range(7)]

    for column_index in range(7):
        for card_index in range(column_index + 1):
            card = deck.pop()
            card.face_up = card_index == column_index
            tableau[column_index].append(card)

    return tableau