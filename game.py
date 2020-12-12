from random import shuffle


def to_str(card_list):
    output = ''
    for card in card_list:
        output += f'{repr(card)}\n'
    return output


def options(card_list):
    top = ''
    bottom = ''
    for i, card in enumerate(card_list):
        bt = f' {card} '
        tp = str(i + 1)
        half = len(bt) // 2
        rest = (len(bt) - len(tp)) - half
        top += ' ' * half + tp + ' ' * rest
        bottom += bt
    return top + '\n' + bottom


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
    PLAYER_TO_RANK = {4: 6, 3: 7, 2: 8, 5: 5, 6: 4, 7: 3, 8: 2}

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
        player.pick_up(self.deal(Player.MAX_CARDS - player.hand_size))

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
    MAX_CARDS = 6

    def __init__(self, name):
        self.name = name.capitalize()
        self.hand = []

    def pick_up(self, *cards):
        if isinstance(cards[0], list):
            self.hand.extend(cards[0])
        elif isinstance(cards[0], Card):
            self.hand.extend(cards)
        else:
            raise TypeError

    def choose(self, cards, prompt, deny='', one_option=False):

        def parse(s):
            if ',' in s:
                s = s.split(',')
            elif ' ' in s:
                s = s.split(' ')
            if len(s) == 1:
                return [s.strip()]
            else:
                return [x.strip() for x in s]

        def is_valid(s):
            if len(s) == 0:
                return False
            if len(s) > 1 and one_option:
                return False

            for choice in s:
                try:
                    if s == '':
                        return False
                    elif int(choice) > len(self.hand) or int(choice) < 1:
                        return False
                    else:
                        pass
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
                return selection
            selection = parse(selection)
            if not is_valid(selection):
                print('Invalid.')
        return selection

    def attack(self):
        print('Your hand:')
        print(options(self.hand))
        print()
        do_match = False
        while not do_match:
            selection = self.choose(self.hand, 'Which card(s) to attack?')
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

    def add_attack(self, cards_on_table):
        print('Your hand:')
        print(options(self.hand))
        print()
        do_match = False
        while not do_match:
            selection = self.choose(self.hand, 'Which card(s) to attack?')
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

    def defend(self, cards):
        print("Attacked by: ")
        print(to_str(cards))
        print("Your hand: ")
        print(options(self.hand))
        print()
        defense = dict()
        for card in cards:
            can_defend = False
            i = -1
            while not can_defend:
                selection = self.choose(self.hand, f'Which card to defend {card}?', deny='0', one_option=True)
                i = int(selection[0]) - 1
                c = self.hand[i]
                if c > card:
                    can_defend = True
                else:
                    print(f'{c} cannot defend aganst {card}')
            c = self.hand.pop(int(selection[0]) - 1)
            defense[card] = c

    @property
    def hand_size(self):
        return len(self.hand)

    def __repr__(self):
        output = f'{self.name}\n'
        output += to_str(self.hand)
        return output


from os import system, name


def clear():  # clear screen
    if name == 'nt':
        system('cls')
    else:
        system('clear')


def refresh(deck):
    clear()
    print(deck)
    print()


def one_turn(deck, attacker, defender):
    max_attacks = defender.hand_size

    num_attacks = 0
    while num_attacks < max_attacks:
        refresh(deck)
        print(f'{attacker.name} attacking {defender.name}!')
        a = attacker.attack()
        num_attacks += len(a)
        refresh(deck)
        print(f'{attacker.name} attacking {defender.name}!')
        print(to_str(a))
        input(f'{defender.name}\'s turn to defend.\nPress enter to continue...')
        refresh(deck)
        d = defender.defend(a)


from time import sleep


def play_game(deck, *players):
    # assume deck is initialized
    for i, player in enumerate(players):
        deck.deal_to(player)
        player.id = i

    def next_id(x):
        return (x + 1) % len(players)

    first_id = 0
    min_trump = 14
    for player in players:
        for c in player.hand:
            if c.rank < min_trump and c.trump:
                min_trump = c.rank
                first_id = player.id
    refresh(deck)
    input(f'{players[first_id].name} goes first.\nPress enter to continue...')
    refresh(deck)
    cur_id = first_id
    n_id = next_id(cur_id)
    one_turn(deck, players[cur_id], players[n_id])


if __name__ == '__main__':
    d = Deck()
    gavin = Player('gavin')
    miles = Player('miles')
    play_game(d, gavin, miles)
