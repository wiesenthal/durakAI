from game import *
from colors import ColorHandler
from colorama import Fore, Back, Style, init, deinit

init()


# one turn:
# attacker attacks defender
# defender defends
# while num_attacks <= max_attacks:
# while attacker != defender and num_attacks < max_attacks:
#   person after defender attacks
# if given_up:
#   break
# defender blocks
# if not block:
#   give up

def one_turn(deck, players, attacker_id, defender_id):
    init_attacker_id = attacker_id
    defender = players[defender_id]
    attacker = players[attacker_id]
    max_attacks = defender.hand_size

    num_attacks = 0
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
    if d == dict():
        given_up = True
        new_attacks = [] + a
    else:
        given_up = False
        new_attacks = []

    # adding attackers
    while num_attacks < max_attacks:
        if given_up:
            refresh(deck)
            print(f'{defender.name} cannnot defend. Attackers have one more opportunity to add to the attack.')
            input('Press enter to continue...')
        # get next attacker
        attacker_id = next_id(defender_id, players)
        while attacker_id != defender_id:
            refresh(deck)
            attacker = players[attacker_id]
            print()
            print(to_str(d))
            print(to_str(new_attacks))
            input(f'{attacker.name}\'s turn to add to the attack on {defender.name}.\nPress enter to continue...')
            refresh(deck)
            added = attacker.add_attack(d, new_attacks)
            if not added:
                refresh(deck)
                input(f'{attacker.name} cannot add to the attack.\nPress enter to continue...')
            new_attacks.extend(added)
            num_attacks = len(new_attacks)
            attacker_id = next_id(attacker_id, players)

        if len(new_attacks) == 0 or given_up:
            break
        refresh(deck)
        print(f'{defender.name}, you\'ve been attacked more!')
        print(to_str(d))
        print(to_str(new_attacks))
        input(f'{defender.name}\'s turn to defend.\nPress enter to continue...')
        refresh(deck)
        defense = defender.defend(new_attacks, d)

        if defense == dict():  # failed defense
            given_up = True
        else:
            new_attacks = []
        d.update(defense)
    clear()
    if given_up:
        print(f'{defender.name} cannot defend! He picks up all the cards.')
        all_cards = new_attacks + list(d.keys()) + list(d.values())
        defender.pick_up(all_cards)
    else:
        print(f'Attacks done and {defender.name} successfully defended.')
    return given_up


def play_game(deck, *players):
    # assume deck is initialized
    for i, player in enumerate(players):
        deck.deal_to(player)
        player.id = i

    first_id = 0
    min_trump = 14
    for player in players:
        for c in player.hand:
            if c.rank < min_trump and c.trump:
                min_trump = c.rank
                first_id = player.id
    refresh(deck)

    refresh(deck)
    cur_id = first_id
    n_id = next_id(cur_id, players)
    while sum(p.hand_size == 0 for id, p in enumerate(players)) < 1:
        input(f'{players[cur_id].name}\'s turn to attack.\nPress enter to continue...')
        given_up = one_turn(deck, players, cur_id, n_id)

        print()
        print('Dealing out cards...')
        i = cur_id

        nc = deck.deal_to(players[i])
        print(f'Dealt {nc} cards to {players[i].name}.')
        i = prev_id(i, players)
        while i != cur_id:
            nc = deck.deal_to(players[i])
            print(f'Dealt {nc} cards to {players[i].name}.')
            i = prev_id(i, players)
        print()
        input('Press enter to continue...')
        refresh(deck)
        if given_up:
            cur_id = next_id(n_id, players)
        else:
            cur_id = n_id
        n_id = next_id(cur_id, players)
    for p in players:

        if p.hand_size > 0:
            clear()
            print(f'{ch.start(Fore.RED)}{p.name} is Durak!!!!{ch.end}')


if __name__ == '__main__':
    d = Deck(num_players=2)
    gavin = Player('gavin')
    miles = Player('miles')
    play_game(d, gavin, miles)

deinit()
