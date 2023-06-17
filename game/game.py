import math
import sys
import threading

import pygame

from ai import AI

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 549
NAVY_BLUE_COLOR = (30, 47, 74)
GOLD_COLOR = (204, 152, 8)
ALMOST_WHITE_COLOR = (245, 245, 245)
PLAYER0_COLOR = (168, 62, 50)
PLAYER1_COLOR = (23, 128, 63)
DEFAULT_FONT = "assets/font/yoster.ttf"
MENU_BUTTON = pygame.image.load("assets/menu_button.png")
GAME_BUTTON = pygame.image.load("assets/game_button.png")


class Button:
    def __init__(self, image, x, y, text_input, font_size):
        self._image = image
        self._x = x
        self._y = y
        self._font = pygame.font.Font(DEFAULT_FONT, font_size)
        self._text_input = text_input
        self._text = self._font.render(self._text_input, True, NAVY_BLUE_COLOR)
        self._rect = self._image.get_rect(center=(self._x, self._y))
        self._text_rect = self._text.get_rect(center=(self._x, self._y))

    def update(self, screen):
        screen.blit(self._image, self._rect)
        screen.blit(self._text, self._text_rect)

    def check_for_input(self, x, y):
        if x in range(self._rect.left, self._rect.right) and y in range(self._rect.top, self._rect.bottom):
            return True
        return False

    def change_color(self, x, y):
        if x in range(self._rect.left, self._rect.right) and y in range(self._rect.top, self._rect.bottom):
            self._text = self._font.render(self._text_input, True, GOLD_COLOR)
        else:
            self._text = self._font.render(self._text_input, True, NAVY_BLUE_COLOR)


class Label:
    def __init__(self, screen, size, x, y, text):
        self._screen = screen
        self._size = size
        self._x = x
        self._y = y
        self._font = pygame.font.Font(DEFAULT_FONT, self._size - 14)
        self._text = self._font.render(text, True, ALMOST_WHITE_COLOR)
        self._text_rect = self._text.get_rect(center=(self._x + (self._size // 2), self._y + (self._size // 2)))

    def draw(self):
        label = pygame.Rect(self._x, self._y, self._size, self._size)
        pygame.draw.rect(self._screen, NAVY_BLUE_COLOR, label)
        self._screen.blit(self._text, self._text_rect)


class Field:
    def __init__(self, screen, size, x, y, index):
        self._screen = screen
        self._size = size
        self._x = x
        self._y = y
        self.index = index
        self._corrupted = False
        self._player = None
        self._font = pygame.font.Font(DEFAULT_FONT, self._size - 5)
        self._text = None
        self._text_rect = None
        self._won_field = False

    def draw(self, hovering=False):
        label = pygame.Rect(self._x, self._y, self._size, self._size)
        if hovering:
            hovering_label = pygame.Rect(self._x + 1, self._y + 1, self._size - 2, self._size - 2)
            pygame.draw.rect(self._screen, GOLD_COLOR, hovering_label)
        else:
            pygame.draw.rect(self._screen, NAVY_BLUE_COLOR, label, 1)
            if self._won_field:
                won_label = pygame.Rect(self._x + 1, self._y + 1, self._size - 2, self._size - 2)
                pygame.draw.rect(self._screen, GOLD_COLOR, won_label)
            if self._corrupted:
                self._screen.blit(self._text, self._text_rect)

    def change_color(self, x, y):
        if not self._corrupted:
            if x in range(self._x, self._x + self._size) and y in range(self._y, self._y + self._size):
                self.draw(True)
            else:
                self.draw()

    def check_for_input(self, x, y):
        if not self._corrupted and x in range(self._x, self._x + self._size) and y in range(self._y,
                                                                                            self._y + self._size):
            return True
        return False

    def update(self, player):
        if not self._corrupted:
            text = "X" if player == 0 else "O"
            color = PLAYER0_COLOR if player == 0 else PLAYER1_COLOR
            self._text = self._font.render(text, True, color)
            self._text_rect = self._text.get_rect(center=(self._x + (self._size // 2), self._y + (self._size // 2)))
            self._corrupted = True

    def set_won(self):
        self._won_field = True


class Board:
    def __init__(self, board_size, screen):
        self._topleft = (15, 64)
        self._size = 470
        self._screen = screen
        self._board_size = board_size
        self._square_size = self._size // (self._board_size + 1)
        self._labels = self._prepare_labels()
        self._fields = self._prepare_fields()

    def _prepare_labels(self):
        labels = []
        for y in range(self._board_size + 1):
            for x in range(self._board_size + 1):
                if y == 0 and x == 0:
                    continue
                if y == 0:
                    labels.append(
                        Label(self._screen, self._square_size, ((x * self._square_size) + self._topleft[0]),
                              ((y * self._square_size) + self._topleft[1]), str(x)))
            if y > 0:
                labels.append(Label(self._screen, self._square_size, ((0 * self._square_size) + self._topleft[0]),
                                    ((y * self._square_size) + self._topleft[1]), str(y)))
        return labels

    def _prepare_fields(self):
        fields = []
        for y in range(1, self._board_size + 1):
            for x in range(1, self._board_size + 1):
                fields.append(Field(self._screen, self._square_size, ((x * self._square_size) + self._topleft[0]),
                                    ((y * self._square_size) + self._topleft[1]),
                                    (self._board_size * y) - (self._board_size - x)))
        return fields

    def _get_corrupted_fields_from_game_state(self, game_state):
        corrupted_fields = {}
        for i in range(1, self._board_size ** 2 + 1):
            if game_state[(i - 1) * 2] == 1:
                corrupted_fields[i] = 0
            if game_state[((i - 1) * 2) + 1] == 1:
                corrupted_fields[i] = 1
        return corrupted_fields

    def draw(self):
        background = pygame.Rect(self._topleft[0] + self._square_size, self._topleft[1] + self._square_size,
                                 self._square_size * self._board_size, self._square_size * self._board_size)
        pygame.draw.rect(self._screen, ALMOST_WHITE_COLOR, background)
        for label in self._labels:
            label.draw()
        for field in self._fields:
            field.draw()

    def check_fields(self, x, y):
        for field in self._fields:
            field.change_color(x, y)

    def update_fields(self, game_state):
        corrupted_fields = self._get_corrupted_fields_from_game_state(game_state)
        for field in self._fields:
            if field.index in corrupted_fields:
                field.update(corrupted_fields[field.index])

    def check_for_input(self, x, y):
        for field in self._fields:
            if field.check_for_input(x, y):
                return True, field.index
        return False, None

    def set_won_line(self, line_fields):
        for line_field in line_fields:
            for field in self._fields:
                if line_field == field.index:
                    field.set_won()


class Game:
    def __init__(self, board_size):
        pygame.init()
        pygame.event.set_grab(True)
        pygame.display.set_caption("Gomoku")
        self._icon = pygame.image.load("assets/icon.png")
        pygame.display.set_icon(self._icon)
        self._board_size = board_size
        self._ai = AI(self._board_size)
        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._board = None
        self._game_state = None
        self._moving_thread_running = False

    def _change_player(self):
        self._current_player = "computer" if self._current_player == "human" else self._current_player == "computer"

    def _draw_information_message(self):
        text = pygame.font.Font(DEFAULT_FONT, 20).render(self._information_message, True, GOLD_COLOR)
        rect = text.get_rect(center=(485 - (text.get_size()[0] // 2), 22 + (text.get_size()[1] // 2)))
        self._screen.blit(text, rect)

    def _human_move(self, field_index):
        game_state_index = (field_index - 1) * 2
        if self._starting_player == "computer":
            game_state_index += 1
        self._game_state[game_state_index] = 1
        self._board.update_fields(self._game_state)
        player_won, line_fields = self._check_if_player_won(self._game_state, "human")
        if player_won:
            self._board.set_won_line(line_fields)
            self._current_player = None
            self._information_message = "Human won!"
        else:
            self._current_player = "computer"
            self._information_message = "Computer's thinking"

    def _computer_move(self):
        self._moving_thread_running = True
        field_index = self._ai.get_best_move(self._game_state)
        game_state_index = (field_index - 1) * 2
        if self._starting_player == "human":
            game_state_index += 1
        self._game_state[game_state_index] = 1
        self._board.update_fields(self._game_state)
        player_won, line_fields = self._check_if_player_won(self._game_state, "computer")
        if player_won:
            self._board.set_won_line(line_fields)
            self._current_player = None
            self._information_message = "Computer won!"
        else:
            self._current_player = "human"
            self._information_message = "Your move"
        self._moving_thread_running = False

    def _computer_move_thr(self):
        computer_move_thread = threading.Thread(target=self._computer_move)
        computer_move_thread.daemon = True
        computer_move_thread.start()

    def _transform_index_to_coordinate(self, index):
        return ((index - 1) % self._board_size) + 1, math.ceil(index / self._board_size)

    def _transform_coordinate_to_index(self, x, y):
        return (self._board_size * y) - (self._board_size - x)

    def _check_if_player_won(self, game_state, player):
        bonus = 0 if self._starting_player == player else 1
        corrupted_fields = []
        for index, value in enumerate(game_state[bonus::2]):
            if value == 1:
                corrupted_fields.append(self._transform_index_to_coordinate(index + 1))
        if len(corrupted_fields) < 5:
            return False, None
        for y in range(1, self._board_size + 1):
            fields = [corrupted_field for corrupted_field in corrupted_fields if corrupted_field[1] == y]
            if len(fields) < 5:
                continue
            else:
                for field in fields:
                    unwanted_fields = [(field[0] - 1, y), (field[0] + 5, y)]
                    if all(unwanted_field not in fields for unwanted_field in unwanted_fields):
                        wanted_fields = [(field[0] + i, y) for i in range(1, 5)]
                        if all(wanted_field in fields for wanted_field in wanted_fields):
                            line_fields = [self._transform_coordinate_to_index(field[0], field[1])]
                            [line_fields.append(self._transform_coordinate_to_index(wf[0], wf[1])) for wf in
                             wanted_fields]
                            return True, line_fields
        for x in range(1, self._board_size + 1):
            fields = [field for field in corrupted_fields if field[0] == x]
            if len(fields) < 5:
                continue
            else:
                for field in fields:
                    unwanted_fields = [(x, field[1] - 1), (x, field[1] + 5)]
                    if all(unwanted_field not in fields for unwanted_field in unwanted_fields):
                        wanted_fields = [(x, field[1] + i) for i in range(1, 5)]
                        if all(wanted_field in fields for wanted_field in wanted_fields):
                            line_fields = [self._transform_coordinate_to_index(field[0], field[1])]
                            [line_fields.append(self._transform_coordinate_to_index(wf[0], wf[1])) for wf in
                             wanted_fields]
                            return True, line_fields
        for field in corrupted_fields:
            unwanted_fields = [(field[0] - 1, field[1] - 1), (field[0] + 5, field[1] + 5)]
            if all(unwanted_field not in corrupted_fields for unwanted_field in unwanted_fields):
                wanted_fields = [(field[0] + i, field[1] + i) for i in range(1, 5)]
                if all(wanted_field in corrupted_fields for wanted_field in wanted_fields):
                    line_fields = [self._transform_coordinate_to_index(field[0], field[1])]
                    [line_fields.append(self._transform_coordinate_to_index(wf[0], wf[1])) for wf in wanted_fields]
                    return True, line_fields
        for field in corrupted_fields:
            unwanted_fields = [(field[0] + 1, field[1] - 1), (field[0] - 5, field[1] + 5)]
            if all(unwanted_field not in corrupted_fields for unwanted_field in unwanted_fields):
                wanted_fields = [(field[0] - i, field[1] + i) for i in range(1, 5)]
                if all(wanted_field in corrupted_fields for wanted_field in wanted_fields):
                    line_fields = [self._transform_coordinate_to_index(field[0], field[1])]
                    [line_fields.append(self._transform_coordinate_to_index(wf[0], wf[1])) for wf in wanted_fields]
                    return True, line_fields
        return False, None

    def _main_menu(self):
        while True:
            self._screen.fill(NAVY_BLUE_COLOR)
            mouse_coord = pygame.mouse.get_pos()
            menu_text = pygame.font.Font(DEFAULT_FONT, 25).render("Choose who starts first or exit",
                                                                  True,
                                                                  ALMOST_WHITE_COLOR)
            menu_rect = menu_text.get_rect(center=(250, 50))
            self._screen.blit(menu_text, menu_rect)
            human_button = Button(MENU_BUTTON, 250, 200, "Human", 35)
            computer_button = Button(MENU_BUTTON, 250, 300, "Computer", 35)
            exit_button = Button(MENU_BUTTON, 250, 400, "Exit", 35)
            for button in [human_button, computer_button, exit_button]:
                button.change_color(mouse_coord[0], mouse_coord[1])
                button.update(self._screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if human_button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        self._start_game("human")
                    if computer_button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        self._start_game("computer")
                    if exit_button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        pygame.quit()
                        sys.exit()
            pygame.display.update()

    def _start_game(self, player):
        self._board = Board(self._board_size, self._screen)
        self._game_state = [0 for _ in range((self._board_size ** 2) * 2)]
        self._starting_player = player
        self._current_player = player
        self._information_message = "Your move" if self._current_player == "human" else "Computer's thinking"
        while True:
            self._screen.fill(NAVY_BLUE_COLOR)
            self._draw_information_message()
            self._board.draw()
            mouse_coord = pygame.mouse.get_pos()
            menu_button = Button(GAME_BUTTON, 65, 32, "Menu", 20)
            restart_button = Button(GAME_BUTTON, 180, 32, "Restart", 20)
            for button in [menu_button, restart_button]:
                button.change_color(mouse_coord[0], mouse_coord[1])
                button.update(self._screen)
            if self._current_player == "computer" and not self._moving_thread_running:
                self._computer_move_thr()
            elif self._current_player == "human" and not self._moving_thread_running:
                self._board.check_fields(mouse_coord[0], mouse_coord[1])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        self._main_menu()
                    if restart_button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        if not all(value == 0 for value in self._game_state):
                            self._board = Board(self._board_size, self._screen)
                            self._game_state = [0 for _ in range((self._board_size ** 2) * 2)]
                            self._current_player = player
                            if self._current_player == "human":
                                self._information_message = "Your move"
                            else:
                                self._information_message = "Computer's thinking"
                    if self._current_player == "human" and not self._moving_thread_running:
                        field_not_corrupted, field_index = self._board.check_for_input(mouse_coord[0], mouse_coord[1])
                        if field_not_corrupted:
                            self._human_move(field_index)
            pygame.display.update()

    def run(self):
        self._main_menu()


def main():
    game = Game(15)
    game.run()


if __name__ == "__main__":
    main()
