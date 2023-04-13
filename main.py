import random
import numpy as np
from xlwt import Workbook
import xlrd
import PySimpleGUI as sg

# Created By Arkadiusz Nowak, Dawid Pytak, Grzegorz Tokarz
# Only for academic purpose

# Liczba pol i armii w każdym graczu
NUM_FIELDS = 10
NUM_ARMIES = 100
STRAT = 0


# Klasa reprezentująca pojedynczego gracza
class Player:
    def __init__(self, strategy):
        self.strategy = strategy
        self.armies = [0] * NUM_FIELDS


# Funkcja symulująca cały mecz i zwracająca zwycięzcę
def play_game(p1, p2):
    # Gracze tworzą swoje armie
    p1.armies = p1.strategy()
    p2.armies = p2.strategy()

    p1score = p2score = remis = 0

    for i in range(NUM_FIELDS):
        if p1.armies[i] > p2.armies[i]:
            p1score += 1.0
        elif p1.armies[i] < p2.armies[i]:
            p2score += 1.0
        else:
            p1score += 0.5
            p2score += 0.5

    score = [p1score, p2score]

    return p1score, p2score, p1.armies, p2.armies


# Strategia Nasha - rozkłada armie równomiernie na wszystkich polach
def nash_strategy():
    return [NUM_ARMIES // NUM_FIELDS] * NUM_FIELDS


def nash_strategyv2():
    # Tworzymy wektor zawierający liczbę wojsk na każdym polu
    army_distribution = np.zeros(NUM_FIELDS)

    # Dzielimy armię równomiernie na wszystkie pola
    army_distribution += NUM_ARMIES / NUM_FIELDS

    # Wykonujemy iteracje algorytmu równowagi Nasha, aż do uzyskania stabilnego rozkładu
    while True:
        # Obliczamy każdy współczynnik zysku dla każdego pola
        gains = []
        for i in range(NUM_FIELDS):
            # Dla każdego pola obliczamy zysk, jaki przyniosłoby przesunięcie
            # jednej jednostki wojsk z tego pola na inne
            gain = 0
            for j in range(NUM_FIELDS):
                if i == j:
                    continue
                gain += army_distribution[j] * (army_distribution[j] - army_distribution[i] - 1)
            gains.append(gain)

        # Sprawdzamy, czy uzyskaliśmy stabilny rozkład armii
        if max(gains) <= 0:
            break

        # Przesuwamy jednostkę wojsk z pola o największym zysku na pole o najmniejszym zysku
        max_gain_index = np.argmax(gains)
        min_gain_index = np.argmin(gains)
        army_distribution[max_gain_index] -= 1
        army_distribution[min_gain_index] += 1

    return army_distribution


# Strategia losowa - losuje liczbę armii na każdym polu
def random_strategy():
    # Lista przechowująca liczbę armii na każdym polu
    armies = []

    # Losowanie liczby armii na każdym polu
    for i in range(NUM_FIELDS):
        if i == NUM_FIELDS - 1:
            # Ostatnie pole - na nim zostają wszystkie pozostałe armie
            armies.append(NUM_ARMIES - sum(armies))
        else:
            # Pozostałe pola - na każdym losujemy liczbę armii z zakresu 0-NUM_ARMIES
            armies.append(random.randint(0, NUM_ARMIES - sum(armies)))

    return armies


def test():
    armies = []

    # Wczytanie strategii z pliku do player_strategies
    # z pominieciem puntkow
    with xlrd.open_workbook('blotto_armies1.xls') as wb2:
        sheet = wb2.sheet_by_index(0)
        rows = []
        for row in sheet.get_rows():
            rows.append([cell.value for cell in row])

    player_strategies = rows
    row_count = sheet.utter_max_rows

    for i in range(1000):
        # player_strategies[i].pop()
        for j in range(10):
            player_strategies[i][j] = int(player_strategies[i][j])

    armies = player_strategies[STRAT]
    return armies


# Wczytywanie strategii z pola tekstowego aplikacji
def p_strat():
    current_text = window['array'].get()
    arr = current_text.split(',')
    armies = [int(numeric_string) for numeric_string in arr]
    return armies


playerNash = Player(nash_strategy)
playerRandom1 = Player(random_strategy)
playerRandom2 = Player(random_strategy)
playerHuman = Player(p_strat)
# Test pobierania strategii z pliku
playerCustomTactics = Player(test)
p1score = p2score = remis = 0
points = [p1score, p2score, remis]
number_of_games = 0

wb = Workbook()
sheet1 = wb.add_sheet('Sheet 1', cell_overwrite_ok=True)

layout = [
    [sg.Button('Human Vs Random Ai'), sg.Button('Nash Ai Vs Random Ai'), sg.Button('Custom tactics Ai Vs Random Ai'),
     sg.Button('Random Ai Vs Random Ai'), sg.Button('Custom one tactic Ai Vs Random one tactic Ai'),
     sg.Button('Clear'), ],
    [sg.Text('First player'), sg.Text(size=(62, 1)), sg.Text('Second player')],
    [sg.Multiline(size=(80, 12), key='first_player', disabled=True, default_text='[First player winning tactics]:'),
     sg.Multiline(size=(80, 12), key='second_player', disabled=True, default_text='[Second player winning tactics]:')],
    [sg.Text('Game'), sg.Text(size=(66, 1)), sg.Text('Draw')],
    [sg.Multiline(size=(80, 15), key='game', disabled=True,
                  default_text='[First player wins , Draw, Second player wins]:'),
     sg.Multiline(size=(80, 15), key='draw', disabled=True,
                  default_text='[Draw Player One and Player Two tactics]:')],
    [sg.Multiline(size=(80, 4), key='percents', default_text='[Percents of wins and draws]:', disabled=True),
     sg.Multiline(size=(80, 4),
                  default_text='[Instruction]:\n1. If you want to play, you need to insert array in the [Enter array '
                               'for human tactic],\n'
                               '2. If you want to play various mix of games just click other buttons,\n'
                               '3. To truncate use a clear button, ',
                  disabled=True)],
    [sg.Text('Enter array for human tactic:')],
    [sg.Input(key='array', size=(40, 1), default_text='10,10,10,10,10,10,10,10,10,10')]
]

window = sg.Window('Blotto Game Simulator', layout, size=(1200, 800), resizable=True)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Custom tactics Ai Vs Random Ai':
        for i in range(100):
            winner = play_game(playerCustomTactics, playerRandom1)
            if winner[1] > winner[0]:
                points[2] += 1
                current_text = window['second_player'].get()
                window['second_player'].update(current_text + '\n' + winner[3].__str__())
            elif winner[0] > winner[1]:
                points[0] += 1
                current_text = window['first_player'].get()
                window['first_player'].update(current_text + '\n' + winner[2].__str__())
            else:
                points[1] += 1
                current_text = window['draw'].get()
                window['draw'].update(current_text + '\n' + winner[2].__str__() + ' : ' + winner[3].__str__())
            current_text = window['game'].get()
            window['game'].update(current_text + '\n' + points.__str__())
            STRAT += 1
            number_of_games += 100
        percents_w = round((points[0] / number_of_games) * 10000, 2)
        percents_d = round((points[1] / number_of_games) * 10000, 2)
        percents_l = round((points[2] / number_of_games) * 10000, 2)
        window['percents'].update('First player wins: ' + str(percents_w) + '%' + '\n' + 'Draws: ' + str(
            percents_d) + '%''\n' + 'Second player wins:' + str(percents_l) + '%', '.2f')
        # pass
    elif event == 'Nash Ai Vs Random Ai':
        for i in range(100):
            winner = play_game(playerNash, playerRandom1)
            if winner[1] > winner[0]:
                points[2] += 1
                current_text = window['second_player'].get()
                window['second_player'].update(current_text + '\n' + winner[3].__str__())
            elif winner[0] > winner[1]:
                points[0] += 1
                current_text = window['first_player'].get()
                window['first_player'].update(current_text + '\n' + winner[2].__str__())
            else:
                points[1] += 1
                current_text = window['draw'].get()
                window['draw'].update(current_text + '\n' + winner[2].__str__() + ' : ' + winner[3].__str__())
            current_text = window['game'].get()
            window['game'].update(current_text + '\n' + points.__str__())
            STRAT += 1
            number_of_games += 100
        percents_w = round((points[0] / number_of_games) * 10000, 2)
        percents_d = round((points[1] / number_of_games) * 10000, 2)
        percents_l = round((points[2] / number_of_games) * 10000, 2)
        window['percents'].update('First player wins: ' + str(percents_w) + '%' + '\n' + 'Draws: ' + str(
            percents_d) + '%''\n' + 'Second player wins:' + str(percents_l) + '%', '.2f')
    elif event == 'Random Ai Vs Random Ai':
        for i in range(100):
            winner = play_game(playerRandom1, playerRandom2)
            if winner[1] > winner[0]:
                points[2] += 1
                current_text = window['second_player'].get()
                window['second_player'].update(current_text + '\n' + winner[3].__str__())
            elif winner[0] > winner[1]:
                points[0] += 1
                current_text = window['first_player'].get()
                window['first_player'].update(current_text + '\n' + winner[2].__str__())
            else:
                points[1] += 1
                current_text = window['draw'].get()
                window['draw'].update(current_text + '\n' + winner[2].__str__() + ' : ' + winner[3].__str__())
            current_text = window['game'].get()
            window['game'].update(current_text + '\n' + points.__str__())
            number_of_games += 100
        percents_w = round((points[0] / number_of_games) * 10000, 2)
        percents_d = round((points[1] / number_of_games) * 10000, 2)
        percents_l = round((points[2] / number_of_games) * 10000, 2)
        window['percents'].update('First player wins: ' + str(percents_w) + '%' + '\n' + 'Draws: ' + str(
            percents_d) + '%''\n' + 'Second player wins:' + str(percents_l) + '%', '.2f')
    elif event == 'Custom one tactic Ai Vs Random one tactic Ai':
        STRAT = random.randint(1, 1000)
        for i in range(1):
            winner = play_game(playerCustomTactics, playerRandom1)
            if winner[1] > winner[0]:
                points[2] += 1
                current_text = window['second_player'].get()
                window['second_player'].update(current_text + '\n' + winner[3].__str__())
            elif winner[0] > winner[1]:
                points[0] += 1
                current_text = window['first_player'].get()
                window['first_player'].update(current_text + '\n' + winner[2].__str__())
            else:
                points[1] += 1
                current_text = window['draw'].get()
                window['draw'].update(current_text + '\n' + winner[2].__str__() + ' : ' + winner[3].__str__())
            current_text = window['game'].get()
            window['game'].update(current_text + '\n' + points.__str__())
            number_of_games += 1
        percents_w = round((points[0] / number_of_games) * 100, 2)
        percents_d = round((points[1] / number_of_games) * 100, 2)
        percents_l = round((points[2] / number_of_games) * 100, 2)
        window['percents'].update('First player wins: ' + str(percents_w) + '%' + '\n' + 'Draws: ' + str(
            percents_d) + '%''\n' + 'Second player wins:' + str(percents_l) + '%', '.2f')
    elif event == 'Human Vs Random Ai':
        STRAT = random.randint(1, 1000)
        for i in range(1):
            winner = play_game(playerHuman, playerRandom1)
            if winner[1] > winner[0]:
                points[2] += 1
                current_text = window['second_player'].get()
                window['second_player'].update(current_text + '\n' + winner[3].__str__())
            elif winner[0] > winner[1]:
                points[0] += 1
                current_text = window['first_player'].get()
                window['first_player'].update(current_text + '\n' + winner[2].__str__())
            else:
                points[1] += 1
                current_text = window['draw'].get()
                window['draw'].update(current_text + '\n' + winner[2].__str__() + ' : ' + winner[3].__str__())
            current_text = window['game'].get()
            window['game'].update(current_text + '\n' + points.__str__())
            number_of_games += 1
        percents_w = round((points[0] / number_of_games) * 100, 2)
        percents_d = round((points[1] / number_of_games) * 100, 2)
        percents_l = round((points[2] / number_of_games) * 100, 2)
        window['percents'].update('First player wins: ' + str(percents_w) + '%' + '\n' + 'Draws: ' + str(
            percents_d) + '%''\n' + 'Second player wins:' + str(percents_l) + '%', '.2f')
    elif event == 'Clear':
        window['draw'].update('[Draw Player One and Player Two tactics]:')
        window['game'].update('[First player wins , Draw, Second player wins]:')
        window['first_player'].update('[First player winning tactics]:')
        window['second_player'].update('[Second player winning tactics]:')
        points = [0, 0, 0]
        number_of_games = 0
        window['percents'].update('[Percents of wins and draws]:')

    elif event == 'Browse':
        filepath = values['Browse']
        import openpyxl

        wb = openpyxl.load_workbook(filepath)

    elif event == 'Submit':
        array = values['array']
        array = array.split(',')
        array = [int(x) for x in array]

window.close()
