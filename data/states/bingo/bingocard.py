"""Classes that manage and display bingo cards"""

import random

from .settings import SETTINGS as S
from . import utils


class BingoLabel(utils.Clickable):
    """A label on a bingo card"""

    style_name = 'square-number'
    show_label = True
    show_mouse_over = True

    def __init__(self, name, card, offset, text):
        """Initialise the label"""
        self.name = name
        self.offset = offset
        self.text = text
        self.is_highlighted = False
        #
        self.x, self.y = card.x + offset[0], card.y + offset[1]
        self.label = utils.getLabel(self.style_name, (self.x, self.y), text)
        self.highlighter = utils.NamedSprite(
            'bingo-highlight', (self.x, self.y), scale=self.get_scale())
        self.mouse_highlight = utils.NamedSprite(
            'bingo-mouse-highlight', (self.x, self.y), scale=self.get_scale())
        #
        super(BingoLabel, self).__init__(name, self.label.rect)

    def get_scale(self):
        """Return the scale to use for graphics"""
        return S['{0}-scale'.format(self.style_name)]

    def handle_click(self):
        """Respond to being clicked on"""
        pass

    def draw(self, surface):
        """Draw the square"""
        if self.show_mouse_over and self.mouse_over:
            self.mouse_highlight.draw(surface)
        elif self.is_highlighted:
            self.highlighter.draw(surface)
        if self.show_label:
            self.label.draw(surface)

    def reset(self):
        """Reset the label"""
        self.is_highlighted = False


class BingoSquare(BingoLabel):
    """A square on a bingo card"""

    style_name = 'square-label'

    def __init__(self, name, card, offset, number):
        """Initialise the square"""
        super(BingoSquare, self).__init__(name, card, offset, number)
        #
        self.is_called = False
        self.marker = utils.NamedSprite(
            'bingo-marker', (self.x, self.y), scale=self.get_scale())

    def draw(self, surface):
        """Draw the square"""
        super(BingoSquare, self).draw(surface)
        if self.is_called:
            self.marker.draw(surface)

    def handle_click(self):
        """The number was clicked on"""
        self.marker.rotate_to(random.randrange(0, 360))
        self.is_called = not self.is_called

    def reset(self):
        """Reset the square"""
        super(BingoSquare, self).reset()
        self.is_called = False


class BingoCard(utils.Clickable):
    """A bingo card comprising a number of squares"""

    square_class = BingoSquare
    show_col_labels = True
    style_name = 'card-square'

    def __init__(self, name, position, state):
        """Initialise the bingo card"""
        super(BingoCard, self).__init__(name)
        #
        self.state = state
        self.x, self.y = position
        self.squares = utils.KeyedDrawableGroup()
        square_offset = S['{0}-offset'.format(self.style_name)]
        chosen_numbers = set()
        #
        # Create the numbered squares
        for x, y in S['card-square-scaled-offsets']:
            #
            # Get a number for this column
            number = self.get_random_number(x, chosen_numbers)
            chosen_numbers.add(number)
            #
            # Place on the card
            self.squares[(x, y)] = self.square_class(
                '{0} [{1}, {2}]'.format(self.name, x, y),
                self, (square_offset * x, square_offset * y), number
            )
        #
        # Create the labels
        self.labels = utils.KeyedDrawableGroup()
        if self.show_col_labels:
            y_offset = min(S['card-square-rows']) - 1
            for x, letter in zip(S['card-square-cols'], 'BINGO'):
                self.labels[x] = BingoLabel(
                    '{0} {1} label'.format(self.name, letter),
                    self, (square_offset * x, square_offset * y_offset), letter
                )
        #
        # The label for display of the remaining squares on the card
        label_offset = S['{0}-remaining-label-offset'.format(self.style_name)]
        self.remaining_label = utils.getLabel(
            'card-remaining-label',
            (self.x + label_offset[0], self.y + label_offset[1]),
            'Player card'
        )
        #
        self.clickables = utils.ClickableGroup(self.squares.values())
        self.drawables = utils.DrawableGroup([
            self.squares, self.labels, self.remaining_label,
        ])

    def get_random_number(self, column, chosen):
        """Return a random number for the column, making sure not to duplicate"""
        while True:
            number = random.choice(S['card-numbers'][column])
            if number not in chosen:
                return number

    def draw(self, surface):
        """Draw the square"""
        self.drawables.draw(surface)

    def process_events(self, event, scale=(1, 1)):
        """Process clicking events"""
        self.clickables.process_events(event, scale)

    def set_label(self, text):
        """Set the card label text"""
        self.remaining_label.set_text(str(text))

    def call_square(self, number):
        """Call a particular square"""
        for square in self.squares.values():
            if square.text == number:
                square.is_called = True

    def reset(self):
        """Reset the card"""
        for square in self.squares.values():
            square.reset()
        for label in self.labels.values():
            label.reset()


class CardCollection(utils.ClickableGroup, utils.DrawableGroup):
    """A set of bingo cards"""

    card_class = NotImplementedError

    def __init__(self, name, position, offsets, state):
        """Initialise the collection"""
        self.name = name
        self.x, self.y = position
        self.state = state
        #
        utils.ClickableGroup.__init__(self)
        utils.DrawableGroup.__init__(self, [self.card_class(
            '%s(%d)' % (self.name, i + 1),
            (self.x + x, self.y + y),
            state) for i, (x, y) in enumerate(offsets)]
        )

    def reset(self):
        """Reset all the cards"""
        for card in self:
            card.reset()
