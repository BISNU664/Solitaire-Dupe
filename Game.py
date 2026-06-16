from Deck import create_deck, deal_tableau
import copy


class Game:
    def __init__(self):
        self.deck = create_deck()
        self.tableau = deal_tableau(self.deck)
        self.waste = []
        self.foundations = [[] for _ in range(4)]
        self.move_history = []
        self.draw_count = 3
        self.foundation_suits = ["C", "D", "H", "S"]

    def reset(self):
        self.__init__()

    def save_state(self):
        state = {
            "deck": copy.deepcopy(self.deck),
            "waste": copy.deepcopy(self.waste),
            "tableau": copy.deepcopy(self.tableau),
            "foundations": copy.deepcopy(self.foundations),
            "draw_count": self.draw_count,
        }

        self.move_history.append(state)

    def undo(self):
        if not self.move_history:
            return False

        state = self.move_history.pop()

        self.deck = state["deck"]
        self.waste = state["waste"]
        self.tableau = state["tableau"]
        self.foundations = state["foundations"]
        self.draw_count = state["draw_count"]

        return True

    def is_valid_tableau_move(self, card, target_column):
        if len(target_column) == 0:
            return card.value == "K"

        top_card = target_column[-1]

        return (
            top_card.face_up
            and card.colour() != top_card.colour()
            and card.rank() == top_card.rank() - 1
        )

    def is_valid_foundation_move(self, card, foundation, foundation_index=None):
        if foundation_index is not None:
            required_suit = self.foundation_suits[foundation_index]
            if card.suit != required_suit:
                return False

        if len(foundation) == 0:
            return card.value == "A"

        top_card = foundation[-1]
        return card.suit == top_card.suit and card.rank() == top_card.rank() + 1

    def move_stack_to_column(self, stack, source_column_index, target_column_index):
        if source_column_index == target_column_index:
            return False

        source_column = self.tableau[source_column_index]
        target_column = self.tableau[target_column_index]

        if not self.is_valid_tableau_move(stack[0], target_column):
            return False

        self.save_state()

        for card in stack:
            source_column.remove(card)
            target_column.append(card)

        if len(source_column) > 0:
            source_column[-1].face_up = True

        return True

    def move_waste_to_column(self, card, target_column_index):
        target_column = self.tableau[target_column_index]

        if self.waste and self.waste[-1] == card:
            if self.is_valid_tableau_move(card, target_column):
                self.save_state()
                self.waste.pop()
                target_column.append(card)
                return True

        return False

    def move_card_to_foundation(self, card, foundation_index, source_pile, source_column_index=None):
        foundation = self.foundations[foundation_index]

        if not self.is_valid_foundation_move(card, foundation, foundation_index):
            return False

        self.save_state()

        if source_pile == "waste" and self.waste and self.waste[-1] == card:
            self.waste.pop()
            foundation.append(card)
            return True

        if source_pile == "tableau":
            source_column = self.tableau[source_column_index]

            if source_column and source_column[-1] == card:
                source_column.pop()
                foundation.append(card)

                if source_column:
                    source_column[-1].face_up = True

                return True

        self.move_history.pop()
        return False

    def move_foundation_to_column(self, card, foundation_index, target_column_index):
        foundation = self.foundations[foundation_index]
        target_column = self.tableau[target_column_index]

        if not foundation or foundation[-1] != card:
            return False

        if not self.is_valid_tableau_move(card, target_column):
            return False

        self.save_state()

        foundation.pop()
        target_column.append(card)

        return True

    def draw_from_stock(self):
        self.save_state()

        if self.deck:
            for _ in range(self.draw_count):
                if self.deck:
                    card = self.deck.pop()
                    card.face_up = True
                    self.waste.append(card)
        else:
            while self.waste:
                card = self.waste.pop()
                card.face_up = False
                self.deck.append(card)

    def can_auto_complete(self):
        for column in self.tableau:
            for card in column:
                if not card.face_up:
                    return False
        return True


    def auto_complete(self):
        if not self.can_auto_complete():
            return False

        moved_any = False
        self.save_state()

        keep_moving = True

        while keep_moving:
            keep_moving = False

            # Move tableau cards to foundations
            for column in self.tableau:
                if column:
                    card = column[-1]

                    for foundation in self.foundations:
                        if self.is_valid_foundation_move(card, foundation):
                            column.pop()
                            foundation.append(card)
                            moved_any = True
                            keep_moving = True
                            break

            # Move waste card to foundations
            if self.waste:
                card = self.waste[-1]

                for foundation in self.foundations:
                    if self.is_valid_foundation_move(card, foundation):
                        self.waste.pop()
                        foundation.append(card)
                        moved_any = True
                        keep_moving = True
                        break

        if not moved_any:
            self.move_history.pop()
            return False

        return True
    
    def has_won(self):
        return all(len(foundation) == 13 for foundation in self.foundations)