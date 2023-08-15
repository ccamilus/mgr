import math
import os
import sys
import threading
import uuid
from pathlib import Path

import pygame

from ai import AI

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 640
FPS = 60

BLUE_WHALE_COLOR = (30, 47, 74)
BLUE_WHALE_DARK_COLOR = (23, 35, 54)
SHIP_COVE_COLOR = (128, 143, 175)
DARK_GOLDENROD_COLOR = (204, 152, 8)
WHITE_SMOKE_COLOR = (245, 245, 245)
MEDIUM_CARMINE_COLOR = (168, 62, 50)
SALEM_COLOR = (23, 128, 63)

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FONT = BASE_PATH.joinpath("assets/font/yoster.ttf")
ICON = pygame.image.load(BASE_PATH.joinpath("assets/icon.png"))


class Button:
    def __init__(self, center_x, center_y, width, height, text_input, font_size, value=None):
        self._center_x = center_x
        self._center_y = center_y
        self._width = width
        self._height = height
        self._text_input = text_input
        self._font = pygame.font.Font(DEFAULT_FONT, font_size)
        self._background = pygame.Rect(self._center_x - (self._width // 2) + 1,
                                       self._center_y - (self._height // 2) + 1, self._width - 2, self._height - 2)
        self._border = pygame.Rect(self._center_x - (self._width // 2), self._center_y - (self._height // 2),
                                   self._width, self._height)
        self._border_width = 2
        self._text = self._font.render(self._text_input, True, SHIP_COVE_COLOR)
        self._text_rect = self._text.get_rect(center=(self._center_x, self._center_y))
        self.value = value

    def update(self, screen):
        pygame.draw.rect(screen, BLUE_WHALE_DARK_COLOR, self._background)
        pygame.draw.rect(screen, SHIP_COVE_COLOR, self._border, self._border_width)
        screen.blit(self._text, self._text_rect)

    def check_for_input(self, x, y):
        if x in range(self._border.left, self._border.right) and y in range(self._border.top, self._border.bottom):
            return True
        return False

    def change_color(self, x, y):
        if x in range(self._border.left, self._border.right) and y in range(self._border.top, self._border.bottom):
            self._text = self._font.render(self._text_input, True, WHITE_SMOKE_COLOR)
            self._border_width = 0
        else:
            self._text = self._font.render(self._text_input, True, SHIP_COVE_COLOR)
            self._border_width = 2


class ToggleButton(Button):
    def __init__(self, center_x, center_y, width, height, text_input, font_size, text_outside_button, selected,
                 value=None):
        super().__init__(center_x, center_y, width, height, text_input, font_size, value)
        if text_outside_button:
            self._text_rect = self._text.get_rect(left=(center_x + (width // 2) + 10), centery=center_y)
        self.selected = selected

    def change_color(self, x, y):
        if self.selected:
            self._text = self._font.render(self._text_input, True, WHITE_SMOKE_COLOR)
            self._border_width = 0
        else:
            super().change_color(x, y)


class NaturalNumberInput:
    def __init__(self, left, top, font_size, max_number_of_digits, default_number):
        self._left = left
        self._top = top
        self._font_size = font_size
        self._max_number_of_digits = max_number_of_digits
        self._default_number = str(default_number)
        self._active = False
        self._cursor_blink_interval = 500
        self._show_cursor = True
        self._last_cursor_toggle = pygame.time.get_ticks()
        self.value = self._default_number

    def handle(self, screen, events):
        mouse_coord = pygame.mouse.get_pos()
        if self._active:
            input_numbers_text = pygame.font.Font(DEFAULT_FONT, self._font_size).render(self.value, True,
                                                                                        WHITE_SMOKE_COLOR)
            input_numbers_rect = input_numbers_text.get_rect(topleft=(self._left, self._top))
            background_rect = pygame.Rect(input_numbers_rect.left - 3, input_numbers_rect.top - 3,
                                          input_numbers_rect.width + 7, input_numbers_rect.height + 7)
            pygame.draw.rect(screen, SHIP_COVE_COLOR, background_rect)
            current_time = pygame.time.get_ticks()
            if current_time - self._last_cursor_toggle >= self._cursor_blink_interval:
                self._show_cursor = not self._show_cursor
                self._last_cursor_toggle = current_time
            if self._show_cursor:
                pygame.draw.line(screen, WHITE_SMOKE_COLOR, (background_rect.right - 3, background_rect.top + 2),
                                 (background_rect.right - 3, background_rect.bottom - 3), 1)
            screen.blit(input_numbers_text, input_numbers_rect)
        else:
            input_numbers_text = pygame.font.Font(DEFAULT_FONT, self._font_size).render(self.value, True,
                                                                                        SHIP_COVE_COLOR)
            input_numbers_rect = input_numbers_text.get_rect(topleft=(self._left, self._top))
            background_rect = pygame.Rect(input_numbers_rect.left - 3, input_numbers_rect.top - 3,
                                          input_numbers_rect.width + 7, input_numbers_rect.height + 7)
            pygame.draw.rect(screen, BLUE_WHALE_DARK_COLOR, background_rect)
            if (mouse_coord[0] in range(background_rect.left, background_rect.right) and
                    mouse_coord[1] in range(background_rect.top, background_rect.bottom)):
                pygame.draw.rect(screen, SHIP_COVE_COLOR, background_rect)
                input_numbers_text = pygame.font.Font(DEFAULT_FONT, self._font_size).render(self.value, True,
                                                                                            WHITE_SMOKE_COLOR)
            else:
                pygame.draw.rect(screen, SHIP_COVE_COLOR, background_rect, 2)
            screen.blit(input_numbers_text, input_numbers_rect)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (mouse_coord[0] in range(background_rect.left, background_rect.right) and
                        mouse_coord[1] in range(background_rect.top, background_rect.bottom)):
                    self._active = True
                else:
                    if len(self.value) == 0:
                        self.value = self._default_number
                    self._active = False
            if event.type == pygame.KEYDOWN:
                if self._active:
                    if event.key == pygame.K_ESCAPE:
                        self.value = self._default_number
                        self._active = False
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if len(self.value) == 0:
                            self.value = self._default_number
                        self._active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.value = self.value[:-1]
                    else:
                        if event.unicode.isdigit():
                            if len(self.value) < self._max_number_of_digits and not (
                                    len(self.value) == 0 and event.unicode == "0"):
                                self.value += event.unicode


class PlayerOptions:
    def __init__(self, player_id, left, top):
        self._player_id = player_id
        self._left = left
        self._top = top
        self._human_toggle_button = ToggleButton(self._left + 304, self._top, 90, 29, "human", 15, False,
                                                 True if player_id == 0 else False)
        self._computer_toggle_button = ToggleButton(self._left + 404, self._top, 90, 29, "computer", 15, False,
                                                    False if player_id == 0 else True)
        self._minmax_first_option_button = ToggleButton(self._left + 25, self._top + 53, 15, 15,
                                                        "fields chosen by formulas", 13, True, True,
                                                        "fields chosen by formulas")
        self._minmax_second_option_button = ToggleButton(self._left + 25, self._top + 78, 15, 15,
                                                         "all non corrupted fields", 13, True, False,
                                                         "all non corrupted fields")
        self._minmax_third_option_button = ToggleButton(self._left + 25, self._top + 103, 15, 15, "nearby fields", 13,
                                                        True, False, "nearby fields")
        self._evaluation_function_on_button = ToggleButton(self._left + 283, self._top + 55, 40, 20, "on", 13, False,
                                                           True, "on")
        self._evaluation_function_off_button = ToggleButton(self._left + 333, self._top + 55, 40, 20, "off", 13, False,
                                                            False, "off")
        self._minmax_number_of_fields_input = NaturalNumberInput(self._left + 202, self._top + 122, 15, 2, 5)
        self._minmax_depth_input = NaturalNumberInput(self._left + 369, self._top + 77, 15, 2, "6")

    def _update_toggle_buttons_group(self, buttons_group, screen, events):
        mouse_coord = pygame.mouse.get_pos()
        for button in buttons_group:
            button.change_color(mouse_coord[0], mouse_coord[1])
            button.update(screen)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons_group:
                    if button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        for other_button in buttons_group:
                            other_button.selected = (other_button == button)

    def handle(self, screen, events):
        option_border = pygame.Rect(self._left, self._top, SCREEN_WIDTH - 40, 150)
        pygame.draw.rect(screen, SHIP_COVE_COLOR, option_border, 2)
        player_sign_text = pygame.font.Font(DEFAULT_FONT, 25).render("X" if self._player_id == 0 else "0", True,
                                                                     MEDIUM_CARMINE_COLOR if self._player_id == 0 else SALEM_COLOR)
        player_sign_rect = player_sign_text.get_rect(left=35, centery=option_border.y)
        options_title_text = pygame.font.Font(DEFAULT_FONT, 15).render("player options", True, SHIP_COVE_COLOR)
        options_title_rect = options_title_text.get_rect(left=60, centery=option_border.y)
        title_rect = pygame.Rect(player_sign_rect.left - 4, player_sign_rect.top - 2,
                                 (options_title_rect.right - player_sign_rect.left) + 10,
                                 (player_sign_rect.bottom - player_sign_rect.top) + 4)
        pygame.draw.rect(screen, BLUE_WHALE_COLOR, title_rect, 0)
        pygame.draw.rect(screen, SHIP_COVE_COLOR, title_rect, 2)
        screen.blit(options_title_text, options_title_rect)
        screen.blit(player_sign_text, player_sign_rect)
        self._update_toggle_buttons_group([self._human_toggle_button, self._computer_toggle_button], screen, events)
        if self._human_toggle_button.selected:
            message_text = pygame.font.Font(DEFAULT_FONT, 15).render("options for human player not available", True,
                                                                     SHIP_COVE_COLOR)
            message_rect = message_text.get_rect(centerx=option_border.centerx, centery=option_border.centery)
            screen.blit(message_text, message_rect)
        if self._computer_toggle_button.selected:
            pygame.draw.line(screen, SHIP_COVE_COLOR, (option_border.centerx + 15, option_border.top),
                             (option_border.centerx + 15, option_border.bottom - 1), 2)
            minmax_message_text = pygame.font.Font(DEFAULT_FONT, 13).render("minmax fields selection:", True,
                                                                            SHIP_COVE_COLOR)
            minmax_message_rect = minmax_message_text.get_rect(
                topleft=(option_border.left + 15, option_border.top + 25))
            screen.blit(minmax_message_text, minmax_message_rect)
            self._update_toggle_buttons_group(
                [self._minmax_first_option_button, self._minmax_second_option_button, self._minmax_third_option_button],
                screen, events)
            if self._minmax_first_option_button.selected:
                minmax_fields_number_text = pygame.font.Font(DEFAULT_FONT, 13).render(
                    "number of chosen fields:", True, SHIP_COVE_COLOR)
                minmax_fields_number_rect = minmax_fields_number_text.get_rect(
                    topleft=(option_border.left + 15, option_border.top + 125))
                screen.blit(minmax_fields_number_text, minmax_fields_number_rect)
                self._minmax_number_of_fields_input.handle(screen, events)
            self._minmax_depth_input.handle(screen, events)
            evaluation_function_text = pygame.font.Font(DEFAULT_FONT, 13).render("evaluation function:", True,
                                                                                 SHIP_COVE_COLOR)
            evaluation_function_rect = evaluation_function_text.get_rect(left=option_border.centerx + 30,
                                                                         top=option_border.top + 25)
            screen.blit(evaluation_function_text, evaluation_function_rect)
            self._update_toggle_buttons_group(
                [self._evaluation_function_on_button, self._evaluation_function_off_button], screen, events)
            minmax_depth_text = pygame.font.Font(DEFAULT_FONT, 13).render("minmax depth:", True, SHIP_COVE_COLOR)
            minmax_depth_rect = minmax_depth_text.get_rect(left=option_border.centerx + 30, top=option_border.top + 80)
            screen.blit(minmax_depth_text, minmax_depth_rect)

    def get_values(self):
        player_name = None
        minmax_option_value = None
        evaluation_function_option_value = None
        minmax_number_of_fields_value = None
        minmax_depth_value = None
        if self._human_toggle_button.selected:
            player_name = "human"
        if self._computer_toggle_button.selected:
            player_name = "computer"
            for button in [self._minmax_first_option_button, self._minmax_second_option_button,
                           self._minmax_third_option_button]:
                if button.selected:
                    minmax_option_value = button.value
                    break
            for button in [self._evaluation_function_on_button, self._evaluation_function_off_button]:
                if button.selected:
                    evaluation_function_option_value = button.value
                    break
            minmax_number_of_fields_value = int(self._minmax_number_of_fields_input.value)
            minmax_depth_value = int(self._minmax_depth_input.value)
        return (self._player_id,
                player_name), minmax_option_value, evaluation_function_option_value, minmax_number_of_fields_value, minmax_depth_value


class Label:
    def __init__(self, screen, size, left, top, text):
        self._screen = screen
        self._size = size
        self._left = left
        self._top = top
        self._font = pygame.font.Font(DEFAULT_FONT, self._size - 14)
        self._text = self._font.render(text, True, SHIP_COVE_COLOR)
        self._text_rect = self._text.get_rect(center=(self._left + (self._size // 2), self._top + (self._size // 2)))

    def draw(self):
        label = pygame.Rect(self._left, self._top, self._size, self._size)
        pygame.draw.rect(self._screen, BLUE_WHALE_COLOR, label)
        self._screen.blit(self._text, self._text_rect)


class Field:
    def __init__(self, screen, size, left, top, index):
        self._screen = screen
        self._size = size
        self._left = left
        self._top = top
        self._font = pygame.font.Font(DEFAULT_FONT, self._size - 5)
        self._corrupted = False
        self._player = None
        self._text = None
        self._text_rect = None
        self.index = index
        self.won_field = False
        self.last_move = False

    def draw(self, hovering=False):
        label = pygame.Rect(self._left, self._top, self._size, self._size)
        if hovering:
            hovering_label = pygame.Rect(self._left + 1, self._top + 1, self._size - 2, self._size - 2)
            pygame.draw.rect(self._screen, DARK_GOLDENROD_COLOR, hovering_label)
        else:
            pygame.draw.rect(self._screen, BLUE_WHALE_COLOR, label, 1)
            if self.won_field:
                won_label = pygame.Rect(self._left + 1, self._top + 1, self._size - 2, self._size - 2)
                pygame.draw.rect(self._screen, DARK_GOLDENROD_COLOR, won_label)
            if self._corrupted:
                if self.last_move:
                    last_move_label = pygame.Rect(self._left + 1, self._top + 1, self._size - 2, self._size - 2)
                    pygame.draw.rect(self._screen, DARK_GOLDENROD_COLOR, last_move_label, 2)
                self._screen.blit(self._text, self._text_rect)

    def change_color(self, x, y):
        if not self._corrupted:
            if x in range(self._left, self._left + self._size) and y in range(self._top, self._top + self._size):
                self.draw(True)
            else:
                self.draw()

    def check_for_input(self, x, y):
        if not self._corrupted and x in range(self._left, self._left + self._size) and y in range(self._top,
                                                                                                  self._top + self._size):
            return True
        return False

    def update(self, player):
        if not self._corrupted:
            text = "X" if player == 0 else "O"
            color = MEDIUM_CARMINE_COLOR if player == 0 else SALEM_COLOR
            self._text = self._font.render(text, True, color)
            self._text_rect = self._text.get_rect(
                center=(self._left + (self._size // 2), self._top + (self._size // 2)))
            self._corrupted = True


class Board:
    def __init__(self, board_size, screen, left, top, size):
        self._board_size = board_size
        self._screen = screen
        self._left = left
        self._top = top
        self._size = size
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
                    labels.append(Label(self._screen, self._square_size, ((x * self._square_size) + self._left),
                                        ((y * self._square_size) + self._top), str(x)))
            if y > 0:
                labels.append(Label(self._screen, self._square_size, ((0 * self._square_size) + self._left),
                                    ((y * self._square_size) + self._top), str(y)))
        return labels

    def _prepare_fields(self):
        fields = []
        for y in range(1, self._board_size + 1):
            for x in range(1, self._board_size + 1):
                fields.append(Field(self._screen, self._square_size, ((x * self._square_size) + self._left),
                                    ((y * self._square_size) + self._top),
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
        background = pygame.Rect(self._left + self._square_size, self._top + self._square_size,
                                 self._square_size * self._board_size, self._square_size * self._board_size)
        pygame.draw.rect(self._screen, WHITE_SMOKE_COLOR, background)
        for label in self._labels:
            label.draw()
        for field in self._fields:
            field.draw()

    def check_fields(self, x, y):
        for field in self._fields:
            field.change_color(x, y)

    def update_fields(self, game_state, field_index):
        corrupted_fields = self._get_corrupted_fields_from_game_state(game_state)
        for field in self._fields:
            if field.index in corrupted_fields:
                field.last_move = True if field.index == field_index else False
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
                    field.won_field = True


class Game:
    def __init__(self, board_size):
        pygame.init()
        pygame.event.set_grab(True)
        pygame.display.set_caption("Gomoku")
        pygame.display.set_icon(ICON)
        self._clock = pygame.time.Clock()
        self._board_size = board_size
        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._first_player_options = PlayerOptions(0, 20, 176)
        self._second_player_options = PlayerOptions(1, 20, 361)
        self._ai = None

    def _load_ai(self):
        self._ai = AI(self._board_size)

    def _load_ai_thr(self):
        ai_loading_thread = threading.Thread(target=self._load_ai)
        ai_loading_thread.daemon = True
        ai_loading_thread.start()

    def _transform_index_to_coordinate(self, index):
        return ((index - 1) % self._board_size) + 1, math.ceil(index / self._board_size)

    def _transform_coordinate_to_index(self, x, y):
        return (self._board_size * y) - (self._board_size - x)

    def _draw_player_information(self, player_options_tuple, sign, sign_color, center_x, center_y):
        sign_text = pygame.font.Font(DEFAULT_FONT, 20).render(sign, True, sign_color)
        sign_rect = sign_text.get_rect(center=(center_x, center_y))
        self._screen.blit(sign_text, sign_rect)
        if self._current_player == player_options_tuple and not self._game_ended:
            information_message = "player <"
            information_message_color = DARK_GOLDENROD_COLOR
        else:
            information_message = "player"
            information_message_color = SHIP_COVE_COLOR
        information_text = pygame.font.Font(DEFAULT_FONT, 15).render(information_message, True,
                                                                     information_message_color)
        information_rect = information_text.get_rect(left=sign_rect.right + 5, centery=540)
        self._screen.blit(information_text, information_rect)
        player_text = pygame.font.Font(DEFAULT_FONT, 13).render(f"{player_options_tuple[0][1]}", True,
                                                                SHIP_COVE_COLOR)
        player_rect = player_text.get_rect(left=sign_rect.left + 5, top=sign_rect.bottom + 5)
        self._screen.blit(player_text, player_rect)
        if player_options_tuple[0][1] == "computer":
            if player_options_tuple[1] == "fields chosen by formulas":
                minmax_fields_selection_text = pygame.font.Font(DEFAULT_FONT, 13).render(
                    f"{player_options_tuple[1]} = {player_options_tuple[3]}", True, SHIP_COVE_COLOR)
            else:
                minmax_fields_selection_text = pygame.font.Font(DEFAULT_FONT, 13).render(
                    f"{player_options_tuple[1]}", True, SHIP_COVE_COLOR)
            minmax_fields_selection_rect = minmax_fields_selection_text.get_rect(left=sign_rect.left + 5,
                                                                                 top=player_rect.bottom + 5)
            self._screen.blit(minmax_fields_selection_text, minmax_fields_selection_rect)
            evaluation_function_text = pygame.font.Font(DEFAULT_FONT, 13).render(
                f"evaluation function = {player_options_tuple[2]}", True, SHIP_COVE_COLOR)
            evaluation_function_rect = evaluation_function_text.get_rect(left=sign_rect.left + 5,
                                                                         top=minmax_fields_selection_rect.bottom + 5)
            self._screen.blit(evaluation_function_text, evaluation_function_rect)
            minmax_depth_text = pygame.font.Font(DEFAULT_FONT, 13).render(
                f"minmax depth = {player_options_tuple[4]}", True, SHIP_COVE_COLOR)
            minmax_depth_rect = evaluation_function_text.get_rect(left=sign_rect.left + 5,
                                                                  top=evaluation_function_rect.bottom + 5)
            self._screen.blit(minmax_depth_text, minmax_depth_rect)

    def _draw_information_message(self):
        text = pygame.font.Font(DEFAULT_FONT, 20).render(self._information_message, True,
                                                         DARK_GOLDENROD_COLOR if self._game_ended else SHIP_COVE_COLOR)
        rect = text.get_rect(center=(485 - (text.get_size()[0] // 2), 22 + (text.get_size()[1] // 2)))
        self._screen.blit(text, rect)

    def _initialize_new_game(self, first_player_options_tuple, second_player_options_tuple):
        self._board = Board(self._board_size, self._screen, 15, 60, 470)
        self._game_state = [0 for _ in range((self._board_size ** 2) * 2)]
        self._first_player = first_player_options_tuple
        self._second_player = second_player_options_tuple
        self._current_player = self._first_player
        self._information_message = "Game in progress•••"
        self._moving_thread_running = False
        self._game_ended = False
        self._current_thread_uuid = None

    def _check_if_player_won(self):
        bonus = 0 if self._first_player == self._current_player else 1
        corrupted_fields = []
        for index, value in enumerate(self._game_state[bonus::2]):
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

    def _computer_move(self, thread_uuid):
        self._moving_thread_running = True
        computer_position_in_game_state = 0 if self._first_player == self._current_player else 1
        field_index = self._ai.get_best_move(self._game_state, computer_position_in_game_state, self._current_player)
        if self._current_thread_uuid == thread_uuid:
            game_state_index = (field_index - 1) * 2
            if self._first_player != self._current_player:
                game_state_index += 1
            self._game_state[game_state_index] = 1
            self._board.update_fields(self._game_state, field_index)
            self._game_ended, line_fields = self._check_if_player_won()
            if self._game_ended:
                self._board.set_won_line(line_fields)
                self._information_message = "First player won!" if self._current_player == self._first_player else "Second player won!"
            else:
                if self._current_player == self._first_player:
                    self._current_player = self._second_player
                else:
                    self._current_player = self._first_player
            self._moving_thread_running = False

    def _computer_move_thr(self):
        thread_uuid = uuid.uuid4()
        self._current_thread_uuid = thread_uuid
        computer_move_thread = threading.Thread(target=self._computer_move, args=(thread_uuid,))
        computer_move_thread.daemon = True
        computer_move_thread.start()

    def _human_move(self, field_index):
        game_state_index = (field_index - 1) * 2
        if self._first_player != self._current_player:
            game_state_index += 1
        self._game_state[game_state_index] = 1
        self._board.update_fields(self._game_state, field_index)
        self._game_ended, line_fields = self._check_if_player_won()
        if self._game_ended:
            self._board.set_won_line(line_fields)
            self._information_message = "First player won!" if self._current_player == self._first_player else "Second player won!"
        else:
            if self._current_player == self._first_player:
                self._current_player = self._second_player
            else:
                self._current_player = self._first_player

    def _perform_player_move(self, mouse_coord, events):
        if not self._game_ended:
            if not self._moving_thread_running and self._current_player[0][1] == "human":
                self._board.check_fields(mouse_coord[0], mouse_coord[1])
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        field_not_corrupted, field_index = self._board.check_for_input(mouse_coord[0], mouse_coord[1])
                        if field_not_corrupted:
                            self._human_move(field_index)
            if not self._moving_thread_running and self._current_player[0][1] == "computer":
                self._computer_move_thr()

    def _main_menu(self):
        while True:
            self._clock.tick(FPS)
            events = pygame.event.get()
            mouse_coord = pygame.mouse.get_pos()
            self._screen.fill(BLUE_WHALE_COLOR)
            title_text = pygame.font.Font(DEFAULT_FONT, 60).render("Gomoku", True, WHITE_SMOKE_COLOR)
            title_rect = title_text.get_rect(center=((SCREEN_WIDTH // 2) - 17, 80))
            self._screen.blit(title_text, title_rect)
            title_icon = pygame.transform.scale(ICON, (70, 70))
            title_icon_rect = title_icon.get_rect(center=((SCREEN_WIDTH // 2) + 110, 58))
            self._screen.blit(title_icon, title_icon_rect)
            self._first_player_options.handle(self._screen, events)
            self._second_player_options.handle(self._screen, events)
            exit_button = Button((SCREEN_WIDTH // 2) + 110, 571, 110, 50, "Exit", 35)
            play_button = Button((SCREEN_WIDTH // 2) - 110, 571, 110, 50, "Play", 35)
            for button in [play_button, exit_button]:
                button.change_color(mouse_coord[0], mouse_coord[1])
                button.update(self._screen)
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        first_player_options_tuple = self._first_player_options.get_values()
                        second_player_options_tuple = self._second_player_options.get_values()
                        if ((first_player_options_tuple[0][1] == "human" and
                             second_player_options_tuple[0][1] == "human") or self._ai):
                            self._start_game(first_player_options_tuple, second_player_options_tuple)
                        self._loading_screen(first_player_options_tuple, second_player_options_tuple)
                    if exit_button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        pygame.quit()
                        sys.exit()
            pygame.display.update()

    def _loading_screen(self, first_player_options_tuple, second_player_options_tuple):
        loading_message_update_interval = 500
        last_loading_message_update = pygame.time.get_ticks()
        loading_message = "loading formulas"
        current_dot_numbers = 0
        while True:
            self._clock.tick(FPS)
            if self._ai:
                self._start_game(first_player_options_tuple, second_player_options_tuple)
            else:
                self._screen.fill(BLUE_WHALE_COLOR)
                title_text = pygame.font.Font(DEFAULT_FONT, 60).render("Gomoku", True, WHITE_SMOKE_COLOR)
                title_rect = title_text.get_rect(center=((SCREEN_WIDTH // 2) - 17, 200))
                self._screen.blit(title_text, title_rect)
                title_icon = pygame.transform.scale(ICON, (70, 70))
                title_icon_rect = title_icon.get_rect(center=((SCREEN_WIDTH // 2) + 110, 178))
                self._screen.blit(title_icon, title_icon_rect)
                loading_text = pygame.font.Font(DEFAULT_FONT, 20).render(loading_message, True, SHIP_COVE_COLOR)
                loading_rect = loading_text.get_rect(left=150, centery=450)
                self._screen.blit(loading_text, loading_rect)
                current_time = pygame.time.get_ticks()
                if current_time - last_loading_message_update >= loading_message_update_interval:
                    last_loading_message_update = current_time
                    if current_dot_numbers == 3:
                        loading_message = loading_message[:-3]
                        current_dot_numbers = 0
                    else:
                        current_dot_numbers += 1
                        loading_message += "•"
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                pygame.display.update()

    def _start_game(self, first_player_options_tuple, second_player_options_tuple):
        self._initialize_new_game(first_player_options_tuple, second_player_options_tuple)
        while True:
            self._clock.tick(FPS)
            self._screen.fill(BLUE_WHALE_COLOR)
            self._draw_information_message()
            self._board.draw()
            mouse_coord = pygame.mouse.get_pos()
            events = pygame.event.get()
            menu_button = Button(55, 32, 80, 30, "Menu", 20)
            restart_button = Button(160, 32, 110, 30, "Restart", 20)
            for button in [menu_button, restart_button]:
                button.change_color(mouse_coord[0], mouse_coord[1])
                button.update(self._screen)
            if self._game_state.count(1) == self._board_size ** 2:
                self._game_ended = True
                self._information_message = "Tie!"
            self._perform_player_move(mouse_coord, events)
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        self._main_menu()
                    if restart_button.check_for_input(mouse_coord[0], mouse_coord[1]):
                        if not all(value == 0 for value in self._game_state):
                            self._initialize_new_game(first_player_options_tuple, second_player_options_tuple)
            self._draw_player_information(first_player_options_tuple, "X", MEDIUM_CARMINE_COLOR, 30, 540)
            self._draw_player_information(second_player_options_tuple, "O", SALEM_COLOR, (SCREEN_WIDTH // 2) + 20, 540)
            pygame.display.update()

    def run(self):
        self._load_ai_thr()
        self._main_menu()


def main():
    game = Game(15)
    game.run()


if __name__ == "__main__":
    main()
