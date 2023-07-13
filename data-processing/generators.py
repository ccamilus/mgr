import os
import random
from pathlib import Path

import utils as u


class MainGenerator:
    def __init__(self, csv_files_directories, board_size):
        self._csv_files_directories = csv_files_directories
        self._board_size = board_size
        self._goal_column = (board_size ** 2) * 2

    def _get_data(self, file_directory):
        data = []
        with open(file_directory, "r") as file:
            next(file)
            for line in file:
                data.append([int(value) for value in (line.strip()).split(",")])
        return data

    def _divide_data(self, data):
        all_ones = []
        all_zeros = []
        for row in data:
            all_ones.append(row) if row[-1] == 1 else all_zeros.append(row)
        ones = all_ones[len(all_ones) // 2:]
        zeros = all_zeros[len(all_zeros) // 2:]
        test_data = all_ones[:len(all_ones) // 2] + all_zeros[:len(all_zeros) // 2]
        return ones, zeros, test_data

    def _create_clause_fields_around(self, target_field, depth_level):
        fields_around_target = []
        target_x, target_y = u.transform_index_to_coordinate(target_field, self._board_size)
        y = target_y - depth_level
        for i in range(0, (depth_level * 2) + 1):
            if i != 0:
                y += 1
            if 1 <= y <= self._board_size:
                for j in range(0, (depth_level * 2) + 1):
                    x = target_x - depth_level
                    if j != 0:
                        x += j
                    if 1 <= x <= self._board_size:
                        if not (x == target_x and y == target_y):
                            fields_around_target.append(u.transform_coordinate_to_index(x, y, self._board_size))
        clause = []
        for field in fields_around_target:
            clause.append((False, (field - 1) * 2))
            clause.append((False, ((field - 1) * 2) + 1))
        return clause

    def _create_clause_random_columns_random_rows(self, data, number_of_literals):
        used_rows = []
        used_columns = []
        clause = []
        for _ in range(number_of_literals):
            row_number = random.randint(0, len(data) - 1)
            while row_number in used_rows:
                row_number = random.randint(0, len(data) - 1)
            used_rows.append(row_number)
            column_number = random.randint(0, self._goal_column - 1)
            while column_number in used_columns:
                column_number = random.randint(0, self._goal_column - 1)
            used_columns.append(column_number)
            value = data[row_number][column_number]
            clause.append((False, column_number)) if value else clause.append((True, column_number))
        return clause

    def _create_clause_random_columns_same_row(self, data, number_of_literals):
        used_columns = []
        clause = []
        row_number = random.randint(0, len(data) - 1)
        for _ in range(number_of_literals):
            column_number = random.randint(0, self._goal_column - 1)
            while column_number in used_columns:
                column_number = random.randint(0, self._goal_column - 1)
            used_columns.append(column_number)
            value = data[row_number][column_number]
            clause.append((False, column_number)) if value else clause.append((True, column_number))
        return clause

    def _create_clause_maximum_range(self, data, number_of_literals):
        tmp_sums = [1 for _ in range(len(data[0]) - 1)]
        for row in data:
            for i in range(0, len(row) - 1):
                tmp_sums[i] += row[i]
        sums = [tmp_sums[0]]
        for i in range(1, len(tmp_sums)):
            sums.append(sums[-1] + tmp_sums[i])
        used_cols = []
        clause = []
        for _ in range(number_of_literals):
            last = 0
            random_index = random.randint(1, max(sums))
            for i in range(len(sums)):
                if random_index > sums[i]:
                    last = i
                else:
                    break
            while last in used_cols:
                last -= 1
            used_cols.append(last)
            rand_n = random.randint(1, len(data))
            no_ones = tmp_sums[last] - 1
            if rand_n <= no_ones:
                clause.append((False, last))
            else:
                clause.append((True, last))
        return clause

    def _create_clause_probability_columns(self, data, target_field, number_of_literals):
        levels = []
        target_x, target_y = u.transform_index_to_coordinate(target_field, self._board_size)
        depth_level = 1
        next_level_available = True
        while next_level_available:
            if target_x - depth_level <= 0 and target_y - depth_level <= 0 and \
                    target_x + depth_level > self._board_size and target_y + depth_level > self._board_size:
                next_level_available = False
            else:
                columns_in_level = []
                if 1 <= target_y - depth_level <= self._board_size:
                    for i in range(target_x - depth_level, target_x + depth_level + 1):
                        if 1 <= i <= self._board_size:
                            field = u.transform_coordinate_to_index(i, target_y - depth_level, self._board_size)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                if 1 <= target_y + depth_level <= self._board_size:
                    for i in range(target_x - depth_level, target_x + depth_level + 1):
                        if 1 <= i <= self._board_size:
                            field = u.transform_coordinate_to_index(i, target_y + depth_level, self._board_size)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                for i in range((target_y - depth_level) + 1, target_y + depth_level):
                    if 1 <= i <= self._board_size:
                        if target_x - depth_level >= 1:
                            field = u.transform_coordinate_to_index(target_x - depth_level, i, self._board_size)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                        if target_x + depth_level <= self._board_size:
                            field = u.transform_coordinate_to_index(target_x + depth_level, i, self._board_size)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                depth_level += 1
                levels.append(columns_in_level)
        max_range = 10000
        ranges = []
        for _ in range(len(levels) + 1):
            ranges.append(max_range)
            max_range = int(max_range // 2)
        clause = []
        chosen_columns = []
        while len(clause) < number_of_literals:
            random_range_value = random.randint(ranges[-1], ranges[0] - 1)
            index = 0
            while random_range_value < ranges[index]:
                index += 1
            chosen_column = random.choice(levels[index - 1])
            if chosen_column not in chosen_columns:
                row_number = random.randint(0, len(data) - 1)
                value = data[row_number][chosen_column]
                clause.append((False, chosen_column)) if value else clause.append((True, chosen_column))
                chosen_columns.append(chosen_column)
        return clause

    def _create_formula(self, data, clause_types, target_field, number_of_clauses, number_of_literals, depth_level):
        tmp_number_of_clauses = number_of_clauses
        tmp_clause_types = clause_types
        formula = []
        if 0 in clause_types:
            formula.append(self._create_clause_fields_around(target_field, depth_level))
            tmp_number_of_clauses -= 1
            tmp_clause_types.remove(0)
        for _ in range(0, tmp_number_of_clauses):
            random_clause_type = random.choice(tmp_clause_types)
            match random_clause_type:
                case 1:
                    formula.append(self._create_clause_random_columns_random_rows(data, number_of_literals))
                case 2:
                    formula.append(self._create_clause_random_columns_same_row(data, number_of_literals))
                case 3:
                    formula.append(self._create_clause_maximum_range(data, number_of_literals))
                case 4:
                    formula.append(self._create_clause_probability_columns(data, target_field, number_of_literals))
        return formula

    def _check_formula(self, formula, data):
        logic_values = []
        for row in data:
            clause_logic_values = []
            for clause in formula:
                literal_logic_values = []
                for literal in clause:
                    value = row[literal[1]]
                    literal_logic_values.append(not bool(value) if literal[0] else bool(value))
                clause_logic_values.append(any(literal_logic_values))
            logic_values.append(all(clause_logic_values))
        return sum(logic_values), len(logic_values) - sum(logic_values)

    def _print_results(self, number_of_generated_files, number_of_files, field, number_of_generated_formulas,
                       number_of_formulas):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"ready {number_of_generated_files} of {number_of_files} files")
        print(f"{number_of_generated_formulas} out of {number_of_formulas} formulas were generated for field {field}")

    def generate(self, output_path, formula_type, clause_types, number_of_literals, number_of_clauses,
                 number_of_formulas, depth_level=1):
        number_of_generated_files = 0
        for file_directory in self._csv_files_directories:
            data = self._get_data(file_directory)
            ones, zeros, _ = self._divide_data(data)
            field = int(Path(file_directory).stem)
            if formula_type == 1:
                one_formulas = []
                self._print_results(number_of_generated_files, len(self._csv_files_directories), field,
                                    len(one_formulas), number_of_formulas)
                while len(one_formulas) < number_of_formulas:
                    formula = self._create_formula(ones, clause_types, field, number_of_clauses, number_of_literals,
                                                   depth_level)
                    s1, n1 = self._check_formula(formula, ones)
                    s0, n0 = self._check_formula(formula, zeros)
                    if (s1 + n0) > 2 * (s0 + n1) and s1 > 1.5 * n1:
                        if formula not in one_formulas:
                            one_formulas.append(formula)
                            self._print_results(number_of_generated_files, len(self._csv_files_directories), field,
                                                len(one_formulas), number_of_formulas)
                u.save_formulas_as_cnf_file(one_formulas, field, output_path, formula_type, number_of_clauses,
                                            number_of_formulas)
                number_of_generated_files += 1
            if formula_type == 0:
                zero_formulas = []
                self._print_results(number_of_generated_files, len(self._csv_files_directories), field,
                                    len(zero_formulas), number_of_formulas)
                while len(zero_formulas) < number_of_formulas:
                    formula = self._create_formula(zeros, clause_types, field, number_of_clauses, number_of_literals,
                                                   depth_level)
                    s0, n0 = self._check_formula(formula, zeros)
                    s1, n1 = self._check_formula(formula, ones)
                    if (s0 + n1) > 2 * (s1 + n0) and n1 >= 0.7 * s1:
                        if formula not in zero_formulas:
                            zero_formulas.append(formula)
                            self._print_results(number_of_generated_files, len(self._csv_files_directories), field,
                                                len(zero_formulas), number_of_formulas)
                u.save_formulas_as_cnf_file(zero_formulas, field, output_path, formula_type, number_of_clauses,
                                            number_of_formulas)
                number_of_generated_files += 1


class AdditionalGenerator:
    def _four_in_line_checker(self, field, board_size, output_path):
        formulas = []
        x, y = u.transform_index_to_coordinate(field, board_size)
        hx = x - 4
        for i in range(5):
            not_negated_indexes = []
            negated_indexes = []
            first_negate_x = x - 5 + i
            second_negate_x = x + 1 + i
            if 0 < first_negate_x <= board_size:
                negated_indexes.append((u.transform_coordinate_to_index(first_negate_x, y, board_size) - 1) * 2)
            if 0 < second_negate_x <= board_size:
                negated_indexes.append((u.transform_coordinate_to_index(second_negate_x, y, board_size) - 1) * 2)
            for j in range(5):
                tmp_hx = hx + i + j
                if 0 < tmp_hx <= board_size:
                    if tmp_hx != x:
                        not_negated_indexes.append((u.transform_coordinate_to_index(tmp_hx, y, board_size) - 1) * 2)
                else:
                    not_negated_indexes.clear()
                    negated_indexes.clear()
                    break
            if not_negated_indexes:
                formulas.append(
                    [[(False, index)] for index in not_negated_indexes] +
                    [[(True, index)] for index in negated_indexes])
                formulas.append(
                    [[(False, index + 1)] for index in not_negated_indexes] +
                    [[(True, index + 1)] for index in negated_indexes])
        vy = y - 4
        for i in range(5):
            not_negated_indexes = []
            negated_indexes = []
            first_negate_y = y - 5 + i
            second_negate_y = y + 1 + i
            if 0 < first_negate_y <= board_size:
                negated_indexes.append((u.transform_coordinate_to_index(x, first_negate_y, board_size) - 1) * 2)
            if 0 < second_negate_y <= board_size:
                negated_indexes.append((u.transform_coordinate_to_index(x, second_negate_y, board_size) - 1) * 2)
            for j in range(5):
                tmp_vy = vy + i + j
                if 0 < tmp_vy <= board_size:
                    if tmp_vy != y:
                        not_negated_indexes.append((u.transform_coordinate_to_index(x, tmp_vy, board_size) - 1) * 2)
                else:
                    not_negated_indexes.clear()
                    negated_indexes.clear()
                    break
            if not_negated_indexes:
                formulas.append(
                    [[(False, index)] for index in not_negated_indexes] +
                    [[(True, index)] for index in negated_indexes])
                formulas.append(
                    [[(False, index + 1)] for index in not_negated_indexes] +
                    [[(True, index + 1)] for index in negated_indexes])
        d1x = x - 4
        d1y = y - 4
        for i in range(5):
            not_negated_indexes = []
            negated_indexes = []
            first_negate_x = x - 5 + i
            first_negate_y = y - 5 + i
            second_negate_x = x + 1 + i
            second_negate_y = y + 1 + i
            if 0 < first_negate_x <= board_size and 0 < first_negate_y <= board_size:
                negated_indexes.append(
                    (u.transform_coordinate_to_index(first_negate_x, first_negate_y, board_size) - 1) * 2)
            if 0 < second_negate_x <= board_size and 0 < second_negate_y <= board_size:
                negated_indexes.append(
                    (u.transform_coordinate_to_index(second_negate_x, second_negate_y, board_size) - 1) * 2)
            for j in range(5):
                tmp_d1x = d1x + i + j
                tmp_d1y = d1y + i + j
                if 0 < tmp_d1x <= board_size and 0 < tmp_d1y <= board_size:
                    if tmp_d1x != x and tmp_d1y != y:
                        not_negated_indexes.append(
                            (u.transform_coordinate_to_index(tmp_d1x, tmp_d1y, board_size) - 1) * 2)
                else:
                    not_negated_indexes.clear()
                    negated_indexes.clear()
                    break
            if not_negated_indexes:
                formulas.append(
                    [[(False, index)] for index in not_negated_indexes] +
                    [[(True, index)] for index in negated_indexes])
                formulas.append(
                    [[(False, index + 1)] for index in not_negated_indexes] +
                    [[(True, index + 1)] for index in negated_indexes])
        d2x = x + 4
        d2y = y - 4
        for i in range(5):
            not_negated_indexes = []
            negated_indexes = []
            first_negate_x = x + 5 - i
            first_negate_y = y - 5 + i
            second_negate_x = x - 1 - i
            second_negate_y = y + 1 + i
            if 0 < first_negate_x <= board_size and 0 < first_negate_y <= board_size:
                negated_indexes.append(
                    (u.transform_coordinate_to_index(first_negate_x, first_negate_y, board_size) - 1) * 2)
            if 0 < second_negate_x <= board_size and 0 < second_negate_y <= board_size:
                negated_indexes.append(
                    (u.transform_coordinate_to_index(second_negate_x, second_negate_y, board_size) - 1) * 2)
            for j in range(5):
                tmp_d2x = d2x - i - j
                tmp_d2y = d2y + i + j
                if 0 < tmp_d2x <= board_size and 0 < tmp_d2y <= board_size:
                    if tmp_d2x != x and tmp_d2y != y:
                        not_negated_indexes.append(
                            (u.transform_coordinate_to_index(tmp_d2x, tmp_d2y, board_size) - 1) * 2)
                else:
                    not_negated_indexes.clear()
                    negated_indexes.clear()
                    break
            if not_negated_indexes:
                formulas.append(
                    [[(False, index)] for index in not_negated_indexes] +
                    [[(True, index)] for index in negated_indexes])
                formulas.append(
                    [[(False, index + 1)] for index in not_negated_indexes] +
                    [[(True, index + 1)] for index in negated_indexes])
        formula_dict = {}
        for formula in formulas:
            number_of_clauses = len(formula)
            if number_of_clauses not in formula_dict:
                formula_dict[number_of_clauses] = []
            formula_dict[number_of_clauses].append(formula)
        for key, value in formula_dict.items():
            u.save_formulas_as_cnf_file(value, field, output_path, f"4_checker_{key}cl", key, len(value))

    def _three_in_line_checker(self, field, board_size, output_path):
        formulas = []
        x, y = u.transform_index_to_coordinate(field, board_size)
        hx = x - 3
        for i in range(4):
            not_negated_coordinates = []
            enemy_negated_coordinates = []
            first_enemy_negate_x = x - 4 + i
            second_enemy_negate_x = x + 1 + i
            if 0 < first_enemy_negate_x <= board_size:
                enemy_negated_coordinates.append((first_enemy_negate_x, y))
            if 0 < second_enemy_negate_x <= board_size:
                enemy_negated_coordinates.append((second_enemy_negate_x, y))
            if enemy_negated_coordinates:
                for j in range(4):
                    tmp_hx = hx + i + j
                    if 0 < tmp_hx <= board_size:
                        if tmp_hx != x:
                            not_negated_coordinates.append((tmp_hx, y))
                    else:
                        not_negated_coordinates.clear()
                        enemy_negated_coordinates.clear()
                        break
            if not_negated_coordinates:
                for enemy_negated_coordinate in enemy_negated_coordinates:
                    self_negated_coordinates = []
                    min_x = min(
                        coordinate[0] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    max_x = max(
                        coordinate[0] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    if 0 < min_x - 1 <= board_size and min_x - 1 != x:
                        self_negated_coordinates.append((min_x - 1, y))
                    if 0 < max_x + 1 <= board_size and max_x + 1 != x:
                        self_negated_coordinates.append((max_x + 1, y))
                    formulas.append(
                        [[(False, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, ((u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                   enemy_negated_coordinate[1],
                                                                   board_size) - 1) * 2) + 1)]] +
                        [[(True, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2)]
                         for coordinate in self_negated_coordinates])
                    formulas.append(
                        [[(False,
                           ((u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2) + 1)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, (u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                  enemy_negated_coordinate[1], board_size) - 1) * 2)]] +
                        [[(True,
                           ((u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2) + 1)]
                         for coordinate in self_negated_coordinates])
        vy = y - 3
        for i in range(4):
            not_negated_coordinates = []
            enemy_negated_coordinates = []
            first_enemy_negate_y = y - 4 + i
            second_enemy_negate_y = y + 1 + i
            if 0 < first_enemy_negate_y <= board_size:
                enemy_negated_coordinates.append((x, first_enemy_negate_y))
            if 0 < second_enemy_negate_y <= board_size:
                enemy_negated_coordinates.append((x, second_enemy_negate_y))
            if enemy_negated_coordinates:
                for j in range(4):
                    tmp_vy = vy + i + j
                    if 0 < tmp_vy <= board_size:
                        if tmp_vy != y:
                            not_negated_coordinates.append((x, tmp_vy))
                    else:
                        not_negated_coordinates.clear()
                        enemy_negated_coordinates.clear()
                        break
            if not_negated_coordinates:
                for enemy_negated_coordinate in enemy_negated_coordinates:
                    self_negated_coordinates = []
                    min_y = min(
                        coordinate[1] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    max_y = max(
                        coordinate[1] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    if 0 < min_y - 1 <= board_size and min_y - 1 != y:
                        self_negated_coordinates.append((x, min_y - 1))
                    if 0 < max_y + 1 <= board_size and max_y + 1 != y:
                        self_negated_coordinates.append((x, max_y + 1))
                    formulas.append(
                        [[(False, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, ((u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                   enemy_negated_coordinate[1],
                                                                   board_size) - 1) * 2) + 1)]] +
                        [[(True, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2)]
                         for coordinate in self_negated_coordinates])
                    formulas.append(
                        [[(False,
                           ((u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2) + 1)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, (u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                  enemy_negated_coordinate[1], board_size) - 1) * 2)]] +
                        [[(True, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                   board_size) - 1) * 2) + 1)]
                         for coordinate in self_negated_coordinates])
        d1x = x - 3
        d1y = y - 3
        for i in range(4):
            not_negated_coordinates = []
            enemy_negated_coordinates = []
            first_enemy_negate_x = x - 4 + i
            first_enemy_negate_y = y - 4 + i
            second_enemy_negate_x = x + 1 + i
            second_enemy_negate_y = y + 1 + i
            if 0 < first_enemy_negate_x <= board_size and 0 < first_enemy_negate_y <= board_size:
                enemy_negated_coordinates.append((first_enemy_negate_x, first_enemy_negate_y))
            if 0 < second_enemy_negate_x <= board_size and 0 < second_enemy_negate_y <= board_size:
                enemy_negated_coordinates.append((second_enemy_negate_x, second_enemy_negate_y))
            if enemy_negated_coordinates:
                for j in range(4):
                    tmp_d1x = d1x + i + j
                    tmp_d1y = d1y + i + j
                    if 0 < tmp_d1x <= board_size and 0 < tmp_d1y <= board_size:
                        if tmp_d1x != x and tmp_d1y != y:
                            not_negated_coordinates.append((tmp_d1x, tmp_d1y))
                    else:
                        not_negated_coordinates.clear()
                        enemy_negated_coordinates.clear()
                        break
            if not_negated_coordinates:
                for enemy_negated_coordinate in enemy_negated_coordinates:
                    self_negated_coordinates = []
                    min_x = min(
                        coordinate[0] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    min_y = min(
                        coordinate[1] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    max_x = max(
                        coordinate[0] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    max_y = max(
                        coordinate[1] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    if (0 < min_x - 1 <= board_size and min_x - 1 != x) and (
                            0 < min_y - 1 <= board_size and min_y - 1 != y):
                        self_negated_coordinates.append((min_x - 1, min_y - 1))
                    if (0 < max_x + 1 <= board_size and max_x + 1 != x) and (
                            0 < max_y + 1 <= board_size and max_y + 1 != y):
                        self_negated_coordinates.append((max_x + 1, max_y + 1))
                    formulas.append(
                        [[(False, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, ((u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                   enemy_negated_coordinate[1],
                                                                   board_size) - 1) * 2) + 1)]] +
                        [[(True, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2)]
                         for coordinate in self_negated_coordinates])
                    formulas.append(
                        [[(False, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                    board_size) - 1) * 2) + 1)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, (u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                  enemy_negated_coordinate[1],
                                                                  board_size) - 1) * 2)]] +
                        [[(True, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                   board_size) - 1) * 2) + 1)]
                         for coordinate in self_negated_coordinates])
        d2x = x + 3
        d2y = y - 3
        for i in range(4):
            not_negated_coordinates = []
            enemy_negated_coordinates = []
            first_enemy_negate_x = x + 4 - i
            first_enemy_negate_y = y - 4 + i
            second_enemy_negate_x = x - 1 - i
            second_enemy_negate_y = y + 1 + i
            if 0 < first_enemy_negate_x <= board_size and 0 < first_enemy_negate_y <= board_size:
                enemy_negated_coordinates.append((first_enemy_negate_x, first_enemy_negate_y))
            if 0 < second_enemy_negate_x <= board_size and 0 < second_enemy_negate_y <= board_size:
                enemy_negated_coordinates.append((second_enemy_negate_x, second_enemy_negate_y))
            if enemy_negated_coordinates:
                for j in range(4):
                    tmp_d2x = d2x - i - j
                    tmp_d2y = d2y + i + j
                    if 0 < tmp_d2x <= board_size and 0 < tmp_d2y <= board_size:
                        if tmp_d2x != x and tmp_d2y != y:
                            not_negated_coordinates.append((tmp_d2x, tmp_d2y))
                    else:
                        not_negated_coordinates.clear()
                        enemy_negated_coordinates.clear()
                        break
            if not_negated_coordinates:
                for enemy_negated_coordinate in enemy_negated_coordinates:
                    self_negated_coordinates = []
                    max_x = max(
                        coordinate[0] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    min_y = min(
                        coordinate[1] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    min_x = min(
                        coordinate[0] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    max_y = max(
                        coordinate[1] for coordinate in not_negated_coordinates + [enemy_negated_coordinate, (x, y)])
                    if (0 < max_x + 1 <= board_size and max_x + 1 != x) and (
                            0 < min_y - 1 <= board_size and min_y - 1 != y):
                        self_negated_coordinates.append((max_x + 1, min_y - 1))
                    if (0 < min_x - 1 <= board_size and min_x - 1 != x) and (
                            0 < max_y + 1 <= board_size and max_y + 1 != y):
                        self_negated_coordinates.append((min_x - 1, max_y + 1))
                    formulas.append(
                        [[(False, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, ((u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                   enemy_negated_coordinate[1],
                                                                   board_size) - 1) * 2) + 1)]] +
                        [[(True, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], board_size) - 1) * 2)]
                         for coordinate in self_negated_coordinates])
                    formulas.append(
                        [[(False, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                    board_size) - 1) * 2) + 1)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, (u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                  enemy_negated_coordinate[1], board_size) - 1) * 2)]] +
                        [[(True, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                   board_size) - 1) * 2) + 1)]
                         for coordinate in self_negated_coordinates])
        formula_dict = {}
        for formula in formulas:
            number_of_clauses = len(formula)
            if number_of_clauses not in formula_dict:
                formula_dict[number_of_clauses] = []
            formula_dict[number_of_clauses].append(formula)
        for key, value in formula_dict.items():
            u.save_formulas_as_cnf_file(value, field, output_path, f"3_checker_{key}cl", key, len(value))

    def _nearby_field_checker(self, field, board_size, output_path):
        nearby_fields_indexes = []
        x, y = u.transform_index_to_coordinate(field, board_size)
        nearby_field_y = y - 1
        for i in range(0, 3):
            if i != 0:
                nearby_field_y += 1
            if 1 <= nearby_field_y <= board_size:
                for j in range(0, 3):
                    nearby_field_x = x - 1
                    if j != 0:
                        nearby_field_x += j
                    if 1 <= nearby_field_x <= board_size:
                        if not (nearby_field_x == x and nearby_field_y == y):
                            nearby_fields_indexes.append(
                                (u.transform_coordinate_to_index(nearby_field_x, nearby_field_y, board_size) - 1) * 2)
        clause = []
        for nearby_field_index in nearby_fields_indexes:
            clause.append((False, nearby_field_index))
            clause.append((False, nearby_field_index + 1))
        u.save_formulas_as_cnf_file([[clause]], field, output_path, "nearby_field_checker", 1, 1)

    def generate(self, board_size, output_path):
        for field in range(1, (board_size ** 2) + 1):
            self._four_in_line_checker(field, board_size, output_path)
            self._three_in_line_checker(field, board_size, output_path)
            self._nearby_field_checker(field, board_size, output_path)
