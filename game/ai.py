import glob
import math
import os
import random
from pathlib import Path

from numba import njit
from numba.typed import List, Dict
from numpy import array, int16, uint8

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class AI:
    def __init__(self, board_size):
        self._board_size = board_size
        self._main_formulas_dict = self._prepare_main_formulas()
        self._evaluation_formulas_dict = self._prepare_evaluation_formulas()
        self._four_checker_formulas_dict = self._prepare_additional_formulas("4_checker")
        self._three_checker_formulas_dict = self._prepare_additional_formulas("3_checker")
        self._nearby_field_checker_formulas_dict = self._prepare_additional_formulas("nearby_field_checker")

    def _create_formulas(self, number_of_clauses, data):
        raw_formulas = [data[i:i + int(number_of_clauses)] for i in range(0, len(data), int(number_of_clauses))]
        formulas = List()
        for raw_formula in raw_formulas:
            formula = List()
            for raw_clause in raw_formula:
                formula.append(array([int(literal) for literal in raw_clause.split()], dtype=int16))
            formulas.append(formula)
        return formulas

    def _prepare_main_formulas(self):
        fields = [index + 1 for index in range(self._board_size ** 2)]
        main_formulas_dict = Dict()
        for f in fields:
            with open(BASE_DIR.joinpath(f"cnf/main/{f}_0.cnf"), "r") as file:
                all_data = [line.strip() for line in file if not line.startswith('c')]
                zeros = List(self._create_formulas(all_data[0].split()[2], all_data[1:]))
            with open(BASE_DIR.joinpath(f"cnf/main/{f}_1.cnf"), "r") as file:
                all_data = [line.strip() for line in file if not line.startswith('c')]
                ones = List(self._create_formulas(all_data[0].split()[2], all_data[1:]))
            main_formulas_dict[f] = zeros, ones
        return main_formulas_dict

    def _prepare_evaluation_formulas(self):
        evaluation_formulas_dict = Dict()
        with open(BASE_DIR.joinpath("cnf/evaluation/evaluation_player_0.cnf"), "r") as file:
            all_data = [line.strip() for line in file if not line.startswith('c')]
            evaluation_formulas_dict[0] = List(self._create_formulas(all_data[0].split()[2], all_data[1:]))
        with open(BASE_DIR.joinpath("cnf/evaluation/evaluation_player_1.cnf"), "r") as file:
            all_data = [line.strip() for line in file if not line.startswith('c')]
            evaluation_formulas_dict[1] = List(self._create_formulas(all_data[0].split()[2], all_data[1:]))
        return evaluation_formulas_dict

    def _prepare_additional_formulas(self, formula_type):
        fields = [index + 1 for index in range(self._board_size ** 2)]
        additional_formulas_dict = Dict()
        for f in fields:
            files = glob.glob(str(BASE_DIR.joinpath(f"cnf/additional/{f}_{formula_type}*.cnf")))
            formulas = []
            for file in files:
                with open(file, "r") as cnf_file:
                    all_data = [line.strip() for line in cnf_file if not line.startswith('c')]
                    formulas += self._create_formulas(all_data[0].split()[2], all_data[1:])
            additional_formulas_dict[f] = List(formulas)
        return additional_formulas_dict

    def get_best_move(self, game_state, computer_position_in_game_state, player_options_tuple):
        non_corrupted_fields = [i for i in range(1, (self._board_size ** 2) + 1) if
                                not game_state[(i - 1) * 2] == 1 and not game_state[((i - 1) * 2) + 1] == 1]
        if sum(game_state) == 0:
            result = check_main_formulas(self._main_formulas_dict, array(non_corrupted_fields, dtype=uint8),
                                         array(game_state, dtype=int16))
            return random.choice(result[:10])[1]
        else:
            field_scores = []
            fields = prepare_fields(self._four_checker_formulas_dict, self._three_checker_formulas_dict,
                                    self._nearby_field_checker_formulas_dict, self._main_formulas_dict,
                                    self._board_size, array(game_state, dtype=int16), player_options_tuple[3],
                                    player_options_tuple[1])
            for field in fields:
                game_state[((field - 1) * 2) + computer_position_in_game_state] = 1
                score = minmax(self._four_checker_formulas_dict, self._three_checker_formulas_dict,
                               self._nearby_field_checker_formulas_dict, self._main_formulas_dict,
                               self._evaluation_formulas_dict, array(game_state, dtype=int16),
                               computer_position_in_game_state, player_options_tuple[4], self._board_size, False,
                               player_options_tuple[3], player_options_tuple[2], player_options_tuple[1], -2, 2)
                game_state[((field - 1) * 2) + computer_position_in_game_state] = 0
                if score == 1:
                    return field
                else:
                    field_scores.append((score, field))
            max_score = max(field_scores)[0]
            return random.choice([field[1] for field in field_scores if field[0] == max_score])


@njit(nogil=True)
def minmax(four_checker_formulas_dict, three_checker_formulas_dict, nearby_field_checker_formulas_dict,
           main_formulas_dict, evaluation_formulas_dict, game_state, computer_position_in_game_state, depth, board_size,
           maximizer, minmax_number_of_fields_value, evaluation_function_option_value, minmax_option_value, alpha,
           beta):
    score = get_score(evaluation_formulas_dict, game_state, board_size, computer_position_in_game_state,
                      evaluation_function_option_value)
    if depth == 1 or score == 1 or score == -1 or sum(game_state) == (board_size ** 2):
        return score
    if maximizer:
        best_score = -2
        bonus = 0 + computer_position_in_game_state
        fields = prepare_fields(four_checker_formulas_dict, three_checker_formulas_dict,
                                nearby_field_checker_formulas_dict, main_formulas_dict, board_size, game_state,
                                minmax_number_of_fields_value, minmax_option_value)
        for field in fields:
            game_state[((field - 1) * 2) + bonus] = 1
            minmax_result = minmax(four_checker_formulas_dict, three_checker_formulas_dict,
                                   nearby_field_checker_formulas_dict, main_formulas_dict, evaluation_formulas_dict,
                                   game_state, computer_position_in_game_state, depth - 1, board_size, False,
                                   minmax_number_of_fields_value, evaluation_function_option_value, minmax_option_value,
                                   alpha, beta)
            game_state[((field - 1) * 2) + bonus] = 0
            if minmax_result == 1:
                return minmax_result
            best_score = max(best_score, minmax_result)
            alpha = max(alpha, minmax_result)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = 2
        bonus = 1 - computer_position_in_game_state
        fields = prepare_fields(four_checker_formulas_dict, three_checker_formulas_dict,
                                nearby_field_checker_formulas_dict, main_formulas_dict, board_size, game_state,
                                minmax_number_of_fields_value, minmax_option_value)
        for field in fields:
            game_state[((field - 1) * 2) + bonus] = 1
            minmax_result = minmax(four_checker_formulas_dict, three_checker_formulas_dict,
                                   nearby_field_checker_formulas_dict, main_formulas_dict, evaluation_formulas_dict,
                                   game_state, computer_position_in_game_state, depth - 1, board_size, True,
                                   minmax_number_of_fields_value, evaluation_function_option_value, minmax_option_value,
                                   alpha, beta)
            game_state[((field - 1) * 2) + bonus] = 0
            if minmax_result == -1:
                return minmax_result
            best_score = min(best_score, minmax_result)
            beta = min(beta, minmax_result)
            if beta <= alpha:
                break
        return best_score


@njit(nogil=True)
def prepare_fields(four_checker_formulas_dict, three_checker_formulas_dict, nearby_field_checker_formulas_dict,
                   main_formulas_dict, board_size, game_state, minmax_number_of_fields_value, minmax_option_value):
    non_corrupted_fields = [index for index in range(1, (board_size ** 2) + 1) if
                            not game_state[(index - 1) * 2] == 1 and not game_state[((index - 1) * 2) + 1] == 1]
    if minmax_option_value == "all non corrupted fields":
        return List(non_corrupted_fields)
    if minmax_option_value == "nearby fields":
        return check_additional_formulas(nearby_field_checker_formulas_dict, non_corrupted_fields, game_state)
    if minmax_option_value == "fields chosen by formulas":
        fields = check_additional_formulas(four_checker_formulas_dict, non_corrupted_fields, game_state)
        [fields.append(field) for field in
         check_additional_formulas(three_checker_formulas_dict, non_corrupted_fields, game_state) if
         field not in fields]
        if len(fields) < minmax_number_of_fields_value:
            nfc_fields = [field for field in
                          check_additional_formulas(nearby_field_checker_formulas_dict, non_corrupted_fields,
                                                    game_state) if field not in fields]
            mfc_fields = check_main_formulas(main_formulas_dict, nfc_fields, game_state)
            number_of_missing_fields = minmax_number_of_fields_value - len(fields)
            [fields.append(result[1]) for result in mfc_fields[:number_of_missing_fields] if result[1] not in fields]
            return fields
        else:
            return fields[:minmax_number_of_fields_value]


@njit(nogil=True)
def check_additional_formulas(additional_formulas_dict, non_corrupted_fields, game_state):
    result = List()
    for field in non_corrupted_fields:
        score = 0
        for formula in additional_formulas_dict[field]:
            formula_logic_value = True
            for clause in formula:
                clause_logic_value = False
                for literal in clause:
                    if literal < 0:
                        if not bool(game_state[literal * -1]):
                            clause_logic_value = True
                            break
                    else:
                        if bool(game_state[literal]):
                            clause_logic_value = True
                            break
                if not clause_logic_value:
                    formula_logic_value = False
                    break
            if formula_logic_value:
                score += 1
        if score > 0:
            result.append(field)
    return result


@njit(nogil=True)
def check_main_formulas(main_formulas_dict, non_corrupted_fields, game_state):
    result = List()
    for field in non_corrupted_fields:
        zero_formula_type_score = 0
        for formula in main_formulas_dict[field][0]:
            formula_logic_value = True
            for clause in formula:
                clause_logic_value = False
                for literal in clause:
                    if literal < 0:
                        if not bool(game_state[literal * -1]):
                            clause_logic_value = True
                            break
                    else:
                        if bool(game_state[literal]):
                            clause_logic_value = True
                            break
                if not clause_logic_value:
                    formula_logic_value = False
                    break
            if formula_logic_value:
                zero_formula_type_score += 1
        one_formula_type_score = 0
        for formula in main_formulas_dict[field][1]:
            formula_logic_value = True
            for clause in formula:
                clause_logic_value = False
                for literal in clause:
                    if literal < 0:
                        if not bool(game_state[literal * -1]):
                            clause_logic_value = True
                            break
                    else:
                        if bool(game_state[literal]):
                            clause_logic_value = True
                            break
                if not clause_logic_value:
                    formula_logic_value = False
                    break
            if formula_logic_value:
                one_formula_type_score += 1
        result.append((one_formula_type_score - zero_formula_type_score, field))
    result.sort(reverse=True)
    return result


@njit(nogil=True)
def check_evaluation_formulas(evaluation_formulas_dict, game_state, computer_position_in_game_state):
    player_0_score = 0
    for formula in evaluation_formulas_dict[0]:
        formula_logic_value = True
        for clause in formula:
            clause_logic_value = False
            for literal in clause:
                if literal < 0:
                    if not bool(game_state[literal * -1]):
                        clause_logic_value = True
                        break
                else:
                    if bool(game_state[literal]):
                        clause_logic_value = True
                        break
            if not clause_logic_value:
                formula_logic_value = False
                break
        if formula_logic_value:
            player_0_score += 1
    player_1_score = 0
    for formula in evaluation_formulas_dict[1]:
        formula_logic_value = True
        for clause in formula:
            clause_logic_value = False
            for literal in clause:
                if literal < 0:
                    if not bool(game_state[literal * -1]):
                        clause_logic_value = True
                        break
                else:
                    if bool(game_state[literal]):
                        clause_logic_value = True
                        break
            if not clause_logic_value:
                formula_logic_value = False
                break
        if formula_logic_value:
            player_1_score += 1
    if player_1_score > player_0_score:
        result = ((player_1_score - player_0_score) / 100) if computer_position_in_game_state == 1 \
            else ((player_1_score - player_0_score) / 100) * -1
        return result
    elif player_0_score > player_1_score:
        result = ((player_0_score - player_1_score) / 100) if computer_position_in_game_state == 0 \
            else ((player_0_score - player_1_score) / 100) * -1
        return result
    elif player_1_score == player_0_score:
        return 0


@njit(nogil=True)
def get_score(evaluation_formulas_dict, game_state, board_size, computer_position_in_game_state,
              evaluation_function_option_value):
    corrupted_fields_by_computer = []
    corrupted_fields_by_human = []
    human_position_in_game_state = 0 if computer_position_in_game_state == 1 else 1
    for index, value in enumerate(game_state[computer_position_in_game_state::2]):
        if value == 1:
            corrupted_fields_by_computer.append(transform_index_to_coordinate(index + 1, board_size))
    for index, value in enumerate(game_state[human_position_in_game_state::2]):
        if value == 1:
            corrupted_fields_by_human.append(transform_index_to_coordinate(index + 1, board_size))
    if len(corrupted_fields_by_computer) < 5 and len(corrupted_fields_by_human) < 5:
        if evaluation_function_option_value == "on":
            return check_evaluation_formulas(evaluation_formulas_dict, game_state, computer_position_in_game_state)
        else:
            return 0
    for index, corrupted_fields in enumerate([corrupted_fields_by_computer, corrupted_fields_by_human]):
        for y in range(1, board_size + 1):
            fields = [corrupted_field for corrupted_field in corrupted_fields if corrupted_field[1] == y]
            if len(fields) < 5:
                continue
            else:
                for field in fields:
                    unwanted_fields = [(field[0] - 1, y), (field[0] + 5, y)]
                    if check_elements_membership(unwanted_fields, fields, False):
                        wanted_fields = [(field[0] + i, y) for i in range(1, 5)]
                        if check_elements_membership(wanted_fields, fields, True):
                            return 1 if index == 0 else -1
        for x in range(1, board_size + 1):
            fields = [field for field in corrupted_fields if field[0] == x]
            if len(fields) < 5:
                continue
            else:
                for field in fields:
                    unwanted_fields = [(x, field[1] - 1), (x, field[1] + 5)]
                    if check_elements_membership(unwanted_fields, fields, False):
                        wanted_fields = [(x, field[1] + i) for i in range(1, 5)]
                        if check_elements_membership(wanted_fields, fields, True):
                            return 1 if index == 0 else -1
        for field in corrupted_fields:
            unwanted_fields = [(field[0] - 1, field[1] - 1), (field[0] + 5, field[1] + 5)]
            if check_elements_membership(unwanted_fields, corrupted_fields, False):
                wanted_fields = [(field[0] + i, field[1] + i) for i in range(1, 5)]
                if check_elements_membership(wanted_fields, corrupted_fields, True):
                    return 1 if index == 0 else -1
        for field in corrupted_fields:
            unwanted_fields = [(field[0] + 1, field[1] - 1), (field[0] - 5, field[1] + 5)]
            if check_elements_membership(unwanted_fields, corrupted_fields, False):
                wanted_fields = [(field[0] - i, field[1] + i) for i in range(1, 5)]
                if check_elements_membership(wanted_fields, corrupted_fields, True):
                    return 1 if index == 0 else -1
    if evaluation_function_option_value == "on":
        return check_evaluation_formulas(evaluation_formulas_dict, game_state, computer_position_in_game_state)
    else:
        return 0


@njit(nogil=True)
def check_elements_membership(iterable_to_check, target_iterable, should_be_in_target_iterable):
    for element in iterable_to_check:
        if should_be_in_target_iterable and element not in target_iterable:
            return False
        if not should_be_in_target_iterable and element in target_iterable:
            return False
    return True


@njit(nogil=True)
def transform_index_to_coordinate(index, board_size):
    return ((index - 1) % board_size) + 1, math.ceil(index / board_size)
