from game import *
from itertools import chain, combinations
from game_playing import *
from math import inf


def powerset(s):
    return tuple(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))


def possible_attacks(defended_cards, undefended_cards, my_hand):
    # if there are defended or undefended cards
    if len(defended_cards) + len(undefended_cards) > 0:
        # just need to determine which cards can be put down
        # then do all combinations of them
        return powerset([c for c in my_hand if match(defended_cards, undefended_cards, c)])

    else:
        # if there are no defended or undefended cards
        # try every unique card in hand then do that our that plus each combo in possible_attacks for that
        all_possible = []
        seen = []
        for i in range(len(my_hand)):
            if my_hand[i].rank in seen:
                all_possible.append((my_hand[i],))
                continue
            temp_hand = my_hand[:]
            c = temp_hand.pop(i)
            seen.append(c.rank)
            combos = possible_attacks(defended_cards, undefended_cards + [c], temp_hand)
            for combo in combos:
                all_possible.append((c,) + combo)
        return all_possible


# def possible_attacks(defended_cards, undefended_cards, my_hand):
#     # super simple version
#     if len(defended_cards) + len(undefended_cards) > 0:
#         plist = []
#         for card in my_hand:
#             if match(defended_cards, undefended_cards, card):
#                 plist.append([card])
#         return plist
#     else:
#         plist = []
#         for card in my_hand:
#             plist.append([card])
#         return plist


def possible_defends(attacking_cards, my_hand):
    results = []
    other = 0

    for i in range(len(my_hand)):
        if my_hand[i] > attacking_cards[other]:
            temp_attacks = list(attacking_cards[:])
            temp_attacks.pop(other)
            temp_hand = my_hand[:]
            c = temp_hand.pop(i)
            if len(temp_hand) == 0 or len(temp_attacks) == 0:
                results += [[c]]
            else:
                # else: still have more attacks to defend
                for a in possible_defends(temp_attacks, temp_hand):
                    if a:
                        results += [[c] + a]
    if not results:
        return [[]]
    else:
        return results + [[]]


# testing possible attacks
import random

prevDepth = 0

depth = 0
depth_ceiling = 20
def min(my_cards, enemy_cards, att, defended_cards, undefended_cards, alpha, beta):
    global depth, depth_ceiling
    if depth > depth_ceiling:
        return -2
    depth += 1
    if len(my_cards) == 0 and len(enemy_cards) == 0:
        return 0
    elif len(my_cards) == 0:
        return -1
    elif len(enemy_cards) == 0:
        return 1
    # else
    if att:  # i am attacking
        p = possible_attacks(defended_cards, undefended_cards, my_cards)
        if not p[0]:
            # i cannot attack
            return max(enemy_cards, my_cards, True, dict(), [], alpha, beta)
        min_reward = 100000
        for attack in possible_attacks(defended_cards, undefended_cards, my_cards):
            temp_hand = my_cards[:]
            temp_undefended_cards = []
            for card in attack:
                temp_hand.remove(card)
                temp_undefended_cards.append(card)
            reward = max(enemy_cards, temp_hand, False, defended_cards, temp_undefended_cards, alpha, beta)
            if reward < min_reward:
                min_reward = reward

            if min_reward <= alpha:
                return min_reward
            if min_reward < beta:
                beta = min_reward
        # my reward is better if the enemy reward is negative
        return min_reward
    if not att:
        p = possible_defends(undefended_cards, my_cards)
        if len(p) == 1 and len(p[0]) == 0:
            # I cannot defend
            # pick up all cards, enemy turn attack me
            new_my_cards = []
            new_my_cards.extend(
                my_cards + list(defended_cards.keys()) + list(defended_cards.values()) + undefended_cards)
            return max(enemy_cards, new_my_cards, True, dict(), [], alpha, beta)
        min_reward = 100000
        for defense in p:
            if defense:
                temp_hand = my_cards[:]
                temp_defended_cards = dict()
                for a_card, card in zip(undefended_cards, defense):
                    temp_hand.remove(card)
                    temp_defended_cards[a_card] = card
                reward = max(enemy_cards, temp_hand, True, temp_defended_cards, [], alpha, beta)
            else:
                new_my_cards = []
                new_my_cards.extend(
                    my_cards + list(defended_cards.keys()) + list(defended_cards.values()) + undefended_cards)
                reward = max(enemy_cards, new_my_cards, True, dict(), [], alpha, beta)

            if reward < min_reward:
                min_reward = reward

            if min_reward <= alpha:
                return min_reward
            if min_reward < beta:
                beta = min_reward

        return min_reward


def max(my_cards, enemy_cards, att, defended_cards, undefended_cards, alpha, beta):
    if len(my_cards) == 0 and len(enemy_cards) == 0:
        return 0
    elif len(my_cards) == 0:
        return 1
    elif len(enemy_cards) == 0:
        return -1
    # else
    if att:  # i am attacking
        p = possible_attacks(defended_cards, undefended_cards, my_cards)
        if not p[0]:
            # i cannot attack
            return min(enemy_cards, my_cards, True, dict(), [], alpha, beta)
        max_reward = -100000
        for attack in possible_attacks(defended_cards, undefended_cards, my_cards):
            temp_hand = my_cards[:]
            temp_undefended_cards = []
            for card in attack:
                temp_hand.remove(card)
                temp_undefended_cards.append(card)
            reward = min(enemy_cards, temp_hand, False, defended_cards, temp_undefended_cards, alpha, beta)
            if reward > max_reward:
                max_reward = reward
            if max_reward >= beta:
                return max_reward
            if max_reward > alpha:
                alpha = max_reward
        # my reward is better if the enemy reward is negative
        return max_reward
    if not att:
        p = possible_defends(undefended_cards, my_cards)
        if len(p) == 1 and len(p[0]) == 0:
            # I cannot defend
            # pick up all cards, enemy turn attack me
            new_my_cards = []
            new_my_cards.extend(
                my_cards + list(defended_cards.keys()) + list(defended_cards.values()) + undefended_cards)
            return min(enemy_cards, new_my_cards, True, dict(), [], alpha, beta)
        max_reward = -100000
        for defense in p:
            if defense:
                temp_hand = my_cards[:]
                temp_defended_cards = dict()
                for a_card, card in zip(undefended_cards, defense):
                    temp_hand.remove(card)
                    temp_defended_cards[a_card] = card
                reward = min(enemy_cards, temp_hand, True, temp_defended_cards, [], alpha, beta)
            else:
                new_my_cards = []
                new_my_cards.extend(
                    my_cards + list(defended_cards.keys()) + list(defended_cards.values()) + undefended_cards)
                reward = min(enemy_cards, new_my_cards, True, dict(), [], alpha, beta)

            if reward > max_reward:
                max_reward = reward

            if max_reward >= beta:
                return max_reward
            if max_reward > alpha:
                alpha = max_reward

        return max_reward


def choose_best_attack(my_cards, enemy_cards, defended_cards, undefended_cards):
    global depth
    depth = 0
    if len(my_cards) == 0 and len(enemy_cards) == 0:
        return 0
    elif len(my_cards) == 0:
        return 1
    elif len(enemy_cards) == 0:
        return -1
    # else
    max_reward = -100000
    best_attack = None
    p = possible_attacks(defended_cards, undefended_cards, my_cards)
    if not p[0]:
        # no attacks
        return []
    for attack in p:
        temp_hand = my_cards[:]
        for card in attack:
            temp_hand.remove(card)
            undefended_cards.append(card)
        reward = min(enemy_cards, temp_hand, False, defended_cards, undefended_cards, -100001, 100001)
        if reward > max_reward:
            max_reward = reward
            best_attack = attack
    # my reward is better if the enemy reward is negative
    return list(best_attack)


def choose_best_defense(my_cards, enemy_cards, defended_cards, undefended_cards):
    global depth
    depth = 0
    if len(my_cards) == 0 and len(enemy_cards) == 0:
        return 0
    elif len(my_cards) == 0:
        return 1
    elif len(enemy_cards) == 0:
        return -1
    p = possible_defends(undefended_cards, my_cards)
    if len(p) == 1 and len(p[0]) == 0:
        # I cannot defend
        # pick up all cards, enemy turn attack me
        new_my_cards = []
        new_my_cards.extend(my_cards + list(defended_cards.keys()) + list(defended_cards.values()) + undefended_cards)
        return dict()
    max_reward = -100000
    best_defense = None
    for defense in possible_defends(undefended_cards, my_cards):
        temp_hand = my_cards[:]
        temp_defended_cards = dict()
        for a_card, card in zip(undefended_cards, defense):
            temp_hand.remove(card)
            temp_defended_cards[a_card] = card
        temp_undefended_cards = []
        reward = min(enemy_cards, temp_hand, True, temp_defended_cards, temp_undefended_cards, -100001, 100001)
        if reward > max_reward:
            max_reward = reward
            best_defense = defense
    d = dict()
    if not best_defense:
        return dict()
    for k, v in zip(undefended_cards, best_defense):
        d[k] = v
    return d


class AI(Player):
    def __init__(self, name, enemy, deck):
        super().__init__(name)
        self.enemy = enemy
        self.enemy_cards = enemy.hand
        self.all_cards = deck._all_cards.copy()
        self.unseen_cards = self.all_cards
        self.see_cards(self.hand)

    def expected_value(self):
        # what is the expected value from drawing a card?

        total = 0
        n = 0
        for card in self.unseen_cards:
            total += self.value(card)
            n += 1
        return total/n

    def value(self, card):
        # how many cards in the deck can this card defend against?
        v = 0
        for c in self.unseen_cards:
            if card > c:
                v += 1

        return v

    def expected_change(self, card):
        # how much i will expect to gain/lose in value from discarding a card and drawing a new one
        return self.expected_value() - self.value(card)

    def card_value(self, card):
        # how easily can i get rid of this card?
        # - will i be able to defend with this card in a given defense * number of times i will likely defend
        # - will i be able to add attack with this card * number of times i will likely be able to add
        # - will i be able to attack with this card * number of times i will likely attack

        # probability that this card will be replaced by a better card
        # number of cards better than this in the deck / total number of cards in the deck
        pass

    def attack_value(self, attack):
        # should I attack with these cards: how good is that
        # expected value change of each card
        v = 0
        expected_value_change = sum(self.expected_change(c) for c in attack)
        # + probability he cannot defend * (value of next attack) * (value of the cards he will pick up)
        # + probability he can defend * value of cards he loses
        v = expected_value_change
        return v

    def defend_value(self, defend):
        # should I defend with these cards?
        v = 0
        expected_value_change = sum(self.expected_change(c) for c in defend)
        # will other cards be added?
        # + probability other cards will be added that cannot be defended * value of those cards (negative)
        # + probability other cards will be added that can be defended * value of that defense

        v = expected_value_change
        return v


    def p_defend(self, attacks): # probability these cards will be defended
        # number of cards > than this card
        # math for how many cards he has in hand
        pass

    def attack_midgame(self):
        max = -inf
        max_pick = None
        for attack in possible_attacks(dict(), []. self.hand):
            av = self.attack_value(attack)
            if av > max:
                max = av
                max_pick = attack
        return max_pick

    def see_cards(self, cards):
        self.unseen_cards = [x for x in self.unseen_cards if x not in cards]

    def add_attack(self, defended_cards, undefended_cards=None):
        if len(self.unseen_cards) == self.enemy.hand_size: # empty deck
            self.enemy_cards = self.enemy.hand
            return choose_best_attack(self.hand, self.enemy_cards, defended_cards, undefended_cards)

    def attack(self):
        if len(self.unseen_cards) == self.enemy.hand_size: # empty deck
            self.enemy_cards = self.enemy.hand
            c = choose_best_attack(self.hand, self.enemy_cards, dict(), [])
            self.hand = [x for x in self.hand if x not in c]
            return c

    def defend(self, cards, defended_cards=None):
        if len(self.unseen_cards) == self.enemy.hand_size:  # empty deck
            self.enemy_cards = self.enemy.hand
            if defended_cards is None:
                defended_cards = dict()
            return choose_best_defense(self.hand, self.enemy_cards, defended_cards, cards)

def test_value():
    d = Deck(num_players=2)
    miles = Player('miles')
    d.deal_to(miles)
    gavin = AI('gavin', miles, d)
    print(d)
    d.deal_to(gavin)
    for card in gavin.hand:
        print(f"value of {card}: {gavin.value(card)}")
    print(f"expected value in deck: {gavin.expected_value()}")


def test_1():
    d = Deck(num_players=2)
    miles = Player('miles')
    d.deal_to(miles)
    gavin = AI('gavin', miles, d)
    print(d)
    d.deal_to(gavin)
    d.cards = []

    print(to_str(miles.hand))
    print(to_str(gavin.hand))

    play_game(d, miles, gavin)

    p = possible_attacks(dict(), [], miles.hand)
    print(f'Miles Possible Attacks: {p}')
    print('best attack: ')
    a = list(choose_best_attack(miles.hand, gavin.hand, dict(), []))
    print(a)
    for i in a:
        miles.hand.remove(i)
    b = choose_best_defense(gavin.hand, miles.hand, dict(), a)
    for i2 in b.values():
        gavin.hand.remove(i2)
    print('best defense: ')
    print(b)
