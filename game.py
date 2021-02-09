from random import shuffle
from colorama import Fore, Back, Style, init
from colors import ColorHandler

ch = ColorHandler()


def to_str(card_list):
    output = ''
    if isinstance(card_list, list):
        for card in card_list:
            output += f'{repr(card)}\n'
    elif isinstance(card_list, dict):
        for card, response in card_list.items():
            output += f'{repr(card)}  <  {repr(response)}\n'
    return output


def options(card_list, highlighted_cards=None, hl=Fore.WHITE + Style.BRIGHT, nl=Style.DIM + Fore.WHITE):
    top = ''
    bottom = ''
    for i, card in enumerate(card_list):
        if card == '':
            card = '[ X ]'

        bt = f' {card} '
        tp = str(i + 1)
        half = len(bt) // 2
        rest = (len(bt) - len(tp)) - half

        if highlighted_cards:
            if card in highlighted_cards:
                tp = ch(hl) + tp + ch.end
                bt = ch(hl) + bt + ch.end
            else:
                tp = ch(nl) + tp + ch.end
                bt = ch(nl) + bt + ch.end

        top += ' ' * half + tp + ' ' * rest
        bottom += bt

    return top + '\n' + bottom


def is_matching_attack(defended_cards, undefended_cards, attack):
    for card in attack:
        if not match(defended_cards, undefended_cards, card):
            return False
    return True


def match(defended_cards, undefended_cards, card):
    if len(defended_cards) + len(undefended_cards) == 0:
        return True
    all_possibilities = [] + list(defended_cards.keys()) + list(defended_cards.values()) + list(undefended_cards)
    match = False
    for other in all_possibilities:
        if card.rank == other.rank:
            match = True
    return match


def selection_to_cards(selection, hand):
    played_cards = []
    for index in selection:
        i = int(index) - 1
        played_cards.append(hand[i])
    return played_cards


class Card:
    SUITS = {1: '♥', 2: '♦', 3: '♣', 4: '♠'}
    CHR_SUITS = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}

    @staticmethod
    def suit_to_num(suit):
        reversed_suits = {value: key for (key, value) in Card.SUITS.items()}
        return reversed_suits[suit]

    @staticmethod
    def num_to_suit(suit):
        return Card.SUITS[suit]

    def __init__(self, rank, suit, deck):
        if isinstance(suit, str):
            self.suit = suit
        elif isinstance(suit, int):
            self.suit = Card.num_to_suit(suit)
        else:
            raise TypeError
        self.rank = rank
        self.deck = deck

    def suit_num(self):
        reversed_suits = {value: key for (key, value) in Card.SUITS.items()}
        return reversed_suits[self.suit]

    @property
    def trump(self):
        return self.suit == self.deck.trump_suit

    def __gt__(self, other):
        # will return true only iff this card can successfully defend against another
        if self.trump:
            if not other.trump:
                return True
            else:
                return self.rank > other.rank
        else:
            if other.trump:
                return False
            if self.suit != other.suit:
                return False
            else:
                return self.rank > other.rank

    def __repr__(self):
        letters = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        letter = letters.get(self.rank, str(self.rank))
        num_spaces = 2 - len(str(letter))
        return f"{letter}{' ' * num_spaces}{self.suit}"

    def __str__(self):
        letters = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        letter = letters.get(self.rank, str(self.rank))
        num_spaces = 2 - len(str(letter))
        return f"[{letter}{' ' * num_spaces}{self.suit}]"


class Deck:
    PLAYER_TO_RANK = {4: 6, 3: 6, 2: 6, 5: 5, 6: 4, 7: 3, 8: 2}

    def __init__(self, **kargs):
        # deal with arguments
        keys = kargs.keys()
        self.num_players = None
        if 'num_players' in keys:
            self.lowest_rank = Deck.PLAYER_TO_RANK[kargs['num_players']]
            self.num_players = kargs['num_players']
        if 'lowest_rank' in keys:
            self.lowest_rank = kargs['lowest_rank']
        if 'num_players' not in keys and 'lowest_rank' not in keys:
            self.lowest_rank = 6

        self.cards = []
        # generate cards
        for rank in range(self.lowest_rank, 15):
            for suit in Card.SUITS.keys():
                self.cards.append(Card(rank, suit, self))
        # shuffle
        self.shuffle()
        # find trump suit and card
        self.trump_card = str(self.cards[0])
        self.trump_suit = self.cards[0].suit
        self._all_cards = self.cards.copy()

    def shuffle(self):
        shuffle(self.cards)

    def deal_one(self):
        if len(self.cards) <= 0:
            raise IndexError
        return self.cards.pop()

    def deal(self, num_cards):
        cards = []
        for i in range(num_cards):
            try:
                cards.append(self.deal_one())
            except IndexError:
                break
        return cards

    def deal_to(self, player):
        if player.hand_size >= Player.STARTING_HAND_SIZE:
            return 0
        old_hand_size = player.hand_size
        player.pick_up(self.deal(Player.STARTING_HAND_SIZE - player.hand_size))
        if player.hand_size < Player.STARTING_HAND_SIZE:
            print('DECK OUT OF CARDS!')
        return player.hand_size - old_hand_size

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        output = ''
        output += to_str(self.cards)
        last_line = f'Trump: {repr(self.trump_card)}\n'
        output += self.trump_suit * (len(last_line) - 1) + '\n'
        output += last_line
        return output

    def __str__(self):
        output = ''
        output += f'Trump: {self.trump_card}\n'

        last_line = f'{len(self)} cards in deck\n'
        output += self.trump_suit * (len(last_line) - 1) + '\n'
        output += last_line
        return output


class Player:
    STARTING_HAND_SIZE = 6

    def __init__(self, name):
        self.name = name.capitalize()
        self.hand = []
        self.finished = False

    def sort_hand(self):
        self.hand.sort(key=lambda c: (c.trump, c.rank, c.suit_num()))

    def pick_up(self, *cards):
        if isinstance(cards[0], list):
            self.hand.extend(cards[0])
        elif isinstance(cards[0], Card):
            self.hand.extend(cards)
        else:
            raise TypeError
        self.sort_hand()

    def choose(self, cards, prompt, deny='', one_option=False):

        def parse(s):
            if ',' in s:
                s = s.split(',')
            elif ' ' in s:
                s = s.split(' ')
            else:
                return [s.strip()]
            return [x.strip() for x in s]

        def is_valid(s):
            if len(s) == 0:
                return False
            if len(s) > 1 and one_option:
                return False
            seen_choices = []
            for choice in s:
                try:
                    if s == '':
                        return False
                    elif int(choice) > len(self.hand) or int(choice) < 1:
                        return False
                    else:
                        if int(choice) in seen_choices:
                            return False
                        seen_choices.append(int(choice))
                except (TypeError, ValueError):
                    return False

            return True

        selection = []
        while not is_valid(selection):
            if one_option:
                s_text = f'{prompt} (index 1 to {str(len(cards))}): '
            else:
                s_text = f'{prompt} (indices 1 through {str(len(cards))}): '
            if deny:
                deny_text = f'(TYPE "{str(deny)}" FOR NO SELECTION)'
                print(' ' * (len(s_text)) + deny_text)
            selection = input(s_text)
            if deny and selection == deny:
                return []
            selection = parse(selection)
            if not is_valid(selection):
                print('Invalid.')
        return selection

    def attack(self):
        print('Your hand:')
        print(options(self.hand))
        print()
        do_match = False
        selection = []
        while not do_match:
            selection = self.choose(self.hand, 'Which card(s) to attack with?')
            rank = self.hand[int(selection[0]) - 1].rank
            # check if they all match
            do_match = True
            for index in selection:
                i = int(index) - 1
                if self.hand[i].rank != rank:
                    do_match = False
            if not do_match:
                print('The selected cards do not have the same rank.')
        # selection is now a list of card indices
        played_cards = []
        for index in sorted(selection, reverse=True):
            played_cards.append(self.hand.pop(int(index) - 1))

        return played_cards

    def add_attack(self, defended_cards, undefended_cards=None):
        if undefended_cards is None:
            undefended_cards = []

        matching_cards = []
        for c in self.hand:
            if match(defended_cards, undefended_cards, c):
                matching_cards.append(c)

        if not matching_cards:
            return []

        print('Add to the attack?')
        print(to_str(defended_cards))
        print(to_str(undefended_cards))
        print('Your hand (playable cards in yellow):')
        print(options(self.hand, matching_cards, hl=Fore.YELLOW))
        print()

        selection = self.choose(self.hand, 'Which card(s) to add to the attack? ', deny='0')
        while not is_matching_attack(defended_cards, undefended_cards, selection_to_cards(selection, self.hand)) or len(
                list(defended_cards.keys()) + undefended_cards) + len(selection) > 6:
            if is_matching_attack(defended_cards, undefended_cards, selection_to_cards(selection, self.hand)):
                print('Too many attacking cards. No greater than 6.')
            else:
                print('Those cards do not match the ones on the table.')
            selection = self.choose(self.hand, 'Which card(s) to add to the attack? ', deny='0')

        # selection is now a list of card indices
        played_cards = []
        for index in sorted(selection, reverse=True):
            i = int(index) - 1
            played_cards.append(self.hand.pop(i))
        return played_cards

    def defend(self, cards, defended_cards=None):
        if defended_cards is None:
            defended_cards = dict()
        else:
            print("Already defended: ")
            print(to_str(defended_cards))
        highlighted_cards = []
        for _card in cards:
            blocked = False
            for my_card in self.hand:
                if my_card > _card:
                    highlighted_cards.append(my_card)
                    blocked = True
            if not blocked:
                # cannot defend
                return dict()

        print("Attacked by: ")
        print(to_str(cards))
        print("Your hand (playable cards in yellow): ")
        print(options(self.hand, highlighted_cards, hl=Fore.YELLOW + Style.BRIGHT))
        print()
        defense = dict()
        selection = []
        for card in cards:
            can_defend = False
            i = -1
            while not can_defend:
                pick = self.choose(self.hand, f'Which card to defend against {card}?', deny='0', one_option=True)
                if not pick:
                    return dict()
                i = int(pick[0]) - 1
                c = self.hand[i]
                if c in defense.values():
                    print(f'{c} is already being used to defend a card.')
                    clear()
                    return self.defend(cards, defended_cards)
                if c > card:
                    can_defend = True
                    selection.append(i)
                else:
                    print(f'{c} cannot defend against {card}')

            c = self.hand[i]
            defense[card] = c
        for index in sorted(selection, reverse=True):
            self.hand.pop(index)
        return defense

    @property
    def hand_size(self):
        return len(self.hand)

    def __repr__(self):
        output = f'{self.name}\n'
        output += to_str(self.hand)
        return output


from os import system, name


# helpers
def clear():  # clear screen
    if name == 'nt':
        system('cls')
    else:
        system('clear')


def refresh(deck):
    clear()
    print(deck)
    print()


def next_id(x, players):
    orig_x = x
    x = (x + 1) % len(players)
    while players[x].hand_size == 0:
        x = (x + 1) % len(players)
        if x == orig_x:  # if cycled around
            return orig_x
    return x


def prev_id(x, players):
    orig_x = x
    x = (x + 1) % len(players)
    while players[x].hand_size == 0:
        x = (x + len(players) - 1) % len(players)
        if x == orig_x:  # if cycled around
            return orig_x
    return x
