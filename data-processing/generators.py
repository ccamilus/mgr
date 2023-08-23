import copy
import os
import random
from pathlib import Path

import utils as u

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
BOARD_SIZE = 15


class MainGenerator:
    def _get_data(self, file_dir):
        data = []
        with open(file_dir, "r") as file:
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
        train_data = ones + zeros
        test_data = all_ones[:len(all_ones) // 2] + all_zeros[:len(all_zeros) // 2]
        return train_data, ones, zeros, test_data

    def _create_clause_fields_around(self, target_field):
        depth_level = 1
        fields_around_target = []
        target_x, target_y = u.transform_index_to_coordinate(target_field, BOARD_SIZE)
        y = target_y - depth_level
        for i in range(0, (depth_level * 2) + 1):
            if i != 0:
                y += 1
            if 1 <= y <= BOARD_SIZE:
                for j in range(0, (depth_level * 2) + 1):
                    x = target_x - depth_level
                    if j != 0:
                        x += j
                    if 1 <= x <= BOARD_SIZE:
                        if not (x == target_x and y == target_y):
                            fields_around_target.append(u.transform_coordinate_to_index(x, y, BOARD_SIZE))
        clause = []
        for field in fields_around_target:
            clause.append((False, (field - 1) * 2))
            clause.append((False, ((field - 1) * 2) + 1))
        return clause

    def _create_clause_random_columns_random_rows(self, data, num_literals):
        used_rows = []
        used_columns = []
        clause = []
        for _ in range(num_literals):
            row_number = random.randint(0, len(data) - 1)
            while row_number in used_rows:
                row_number = random.randint(0, len(data) - 1)
            used_rows.append(row_number)
            column_number = random.randint(0, ((BOARD_SIZE ** 2) * 2) - 1)
            while column_number in used_columns:
                column_number = random.randint(0, ((BOARD_SIZE ** 2) * 2) - 1)
            used_columns.append(column_number)
            value = data[row_number][column_number]
            clause.append((False, column_number)) if value else clause.append((True, column_number))
        return clause

    def _create_clause_random_columns_same_row(self, data, num_literals):
        used_columns = []
        clause = []
        row_number = random.randint(0, len(data) - 1)
        for _ in range(num_literals):
            column_number = random.randint(0, ((BOARD_SIZE ** 2) * 2) - 1)
            while column_number in used_columns:
                column_number = random.randint(0, ((BOARD_SIZE ** 2) * 2) - 1)
            used_columns.append(column_number)
            value = data[row_number][column_number]
            clause.append((False, column_number)) if value else clause.append((True, column_number))
        return clause

    def _create_clause_maximum_range(self, data, num_literals):
        tmp_sums = [1 for _ in range(len(data[0]) - 1)]
        for row in data:
            for i in range(0, len(row) - 1):
                tmp_sums[i] += row[i]
        sums = [tmp_sums[0]]
        for i in range(1, len(tmp_sums)):
            sums.append(sums[-1] + tmp_sums[i])
        used_cols = []
        clause = []
        for _ in range(num_literals):
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

    def _create_clause_probability_columns(self, data, target_field, num_literals):
        levels = []
        target_x, target_y = u.transform_index_to_coordinate(target_field, BOARD_SIZE)
        depth_level = 1
        next_level_available = True
        while next_level_available:
            if target_x - depth_level <= 0 and target_y - depth_level <= 0 and \
                    target_x + depth_level > BOARD_SIZE and target_y + depth_level > BOARD_SIZE:
                next_level_available = False
            else:
                columns_in_level = []
                if 1 <= target_y - depth_level <= BOARD_SIZE:
                    for i in range(target_x - depth_level, target_x + depth_level + 1):
                        if 1 <= i <= BOARD_SIZE:
                            field = u.transform_coordinate_to_index(i, target_y - depth_level, BOARD_SIZE)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                if 1 <= target_y + depth_level <= BOARD_SIZE:
                    for i in range(target_x - depth_level, target_x + depth_level + 1):
                        if 1 <= i <= BOARD_SIZE:
                            field = u.transform_coordinate_to_index(i, target_y + depth_level, BOARD_SIZE)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                for i in range((target_y - depth_level) + 1, target_y + depth_level):
                    if 1 <= i <= BOARD_SIZE:
                        if target_x - depth_level >= 1:
                            field = u.transform_coordinate_to_index(target_x - depth_level, i, BOARD_SIZE)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                        if target_x + depth_level <= BOARD_SIZE:
                            field = u.transform_coordinate_to_index(target_x + depth_level, i, BOARD_SIZE)
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
        while len(clause) < num_literals:
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

    def _create_main_formula(self, data, clause_types, target_field, num_clauses, num_literals):
        tmp_number_of_clauses = num_clauses
        tmp_clause_types = clause_types
        formula = []
        if 0 in clause_types:
            formula.append(self._create_clause_fields_around(target_field))
            tmp_number_of_clauses -= 1
            tmp_clause_types.remove(0)
        for _ in range(tmp_number_of_clauses):
            random_clause_type = random.choice(tmp_clause_types)
            match random_clause_type:
                case 1:
                    formula.append(self._create_clause_random_columns_random_rows(data, num_literals))
                case 2:
                    formula.append(self._create_clause_random_columns_same_row(data, num_literals))
                case 3:
                    formula.append(self._create_clause_maximum_range(data, num_literals))
                case 4:
                    formula.append(self._create_clause_probability_columns(data, target_field, num_literals))
        return formula

    def _create_evaluation_formula(self, data, clause_types, num_clauses, num_literals):
        formula = []
        for _ in range(num_clauses):
            random_clause_type = random.choice(clause_types)
            match random_clause_type:
                case 1:
                    formula.append(self._create_clause_random_columns_random_rows(data, num_literals))
                case 2:
                    formula.append(self._create_clause_random_columns_same_row(data, num_literals))
                case 3:
                    formula.append(self._create_clause_maximum_range(data, num_literals))
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

    def _print_main_formulas_results(self, formula_type, field, num_generated_formulas, num_formulas):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{num_generated_formulas} out of {num_formulas} formulas (formula set type = {formula_type}) "
              f"were generated for field {field}")

    def _print_evaluation_formulas_results(self, num_generated_formulas, num_formulas, player):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{num_generated_formulas} out of {num_formulas} formulas were generated for player {player}")

    def _get_classifiers(self, field_index):
        x, y = u.transform_index_to_coordinate(field_index, BOARD_SIZE)
        board_center = BOARD_SIZE // 2
        oddity_bonus = 0
        if not BOARD_SIZE % 2 == 0:
            oddity_bonus = 1
            if y == board_center + oddity_bonus:
                return ["t"] if x <= board_center + oddity_bonus else ["v"]
            if x == board_center + oddity_bonus:
                if y < board_center + oddity_bonus:
                    return ["d1"]
                elif y > board_center + oddity_bonus:
                    return ["d2"]
        if x <= board_center and y <= board_center:
            if y >= x:
                return ["t"]
            else:
                return ["d1"]
        if x > board_center + oddity_bonus and y <= board_center:
            if y > BOARD_SIZE - x:
                return ["v"]
            else:
                return ["v", "d1"]
        if x > board_center + oddity_bonus and y > board_center + oddity_bonus:
            if y >= x:
                return ["d2"]
            else:
                return ["h", "v"]
        if x <= board_center and y > board_center + oddity_bonus:
            if y > BOARD_SIZE - x + 1:
                return ["h", "d1"]
            else:
                return ["h"]

    def _perform_symmetry_on_field(self, index, classifier):
        x, y = u.transform_index_to_coordinate(index, BOARD_SIZE)
        match classifier:
            case "t":
                return index
            case "v":
                return u.transform_coordinate_to_index(BOARD_SIZE - x + 1, y, BOARD_SIZE)
            case "h":
                return u.transform_coordinate_to_index(x, BOARD_SIZE - y + 1, BOARD_SIZE)
            case "d1":
                return u.transform_coordinate_to_index(y, x, BOARD_SIZE)
            case "d2":
                return u.transform_coordinate_to_index(BOARD_SIZE - y + 1, BOARD_SIZE - x + 1, BOARD_SIZE)

    def _perform_symmetry_on_clauses(self, clauses, classifier):
        new_clauses = []
        for clause in clauses:
            game_state_properties = []
            for game_state_property in clause:
                game_state_properties.append((game_state_property[0], game_state_property[1],
                                              self._perform_symmetry_on_field(game_state_property[2], classifier)))
            new_clauses.append(game_state_properties)
        return new_clauses

    def _get_clauses_as_tuples(self, file_lines):
        clauses = []
        for line in file_lines:
            game_state_properties = []
            raw_column_indexes = line.split()
            for raw_column_index in raw_column_indexes:
                if raw_column_index.startswith('-'):
                    column_index = int(raw_column_index[1:])
                    player = 0 if column_index % 2 == 0 else 1
                    field_index = ((column_index - player) // 2) + 1
                    game_state_properties.append((True, player, field_index))
                else:
                    column_index = int(raw_column_index)
                    player = 0 if column_index % 2 == 0 else 1
                    field_index = ((column_index - player) // 2) + 1
                    game_state_properties.append((False, player, field_index))
            clauses.append(game_state_properties)
        return clauses

    def _test_generated_formulas(self, test_data, first_type_formulas, second_type_formulas):
        well_guessed_rows = 0
        for row in test_data:
            first_type_formulas_result = 0
            second_type_formulas_result = 0
            for formula in first_type_formulas:
                clause_logic_values = []
                for clause in formula:
                    literal_logic_values = []
                    for literal in clause:
                        value = row[literal[1]]
                        literal_logic_values.append(not bool(value) if literal[0] else bool(value))
                    clause_logic_values.append(any(literal_logic_values))
                if all(clause_logic_values):
                    first_type_formulas_result += 1
            for formula in second_type_formulas:
                clause_logic_values = []
                for clause in formula:
                    literal_logic_values = []
                    for literal in clause:
                        value = row[literal[1]]
                        literal_logic_values.append(not bool(value) if literal[0] else bool(value))
                    clause_logic_values.append(any(literal_logic_values))
                if all(clause_logic_values):
                    second_type_formulas_result += 1
            proposal_value = first_type_formulas_result > second_type_formulas_result
            if row[-1] == proposal_value:
                well_guessed_rows += 1
        return round((well_guessed_rows * 100) / len(test_data), 2)

    def _save_testing_results_for_main_formulas(self, field, precision, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        fields = []
        oddity_bonus = 0 if BOARD_SIZE % 2 == 0 else 1
        center = (BOARD_SIZE // 2) + oddity_bonus
        for i in range(1, center + 1):
            for j in range(1, i + 1):
                fields.append((BOARD_SIZE * i) - (BOARD_SIZE - j))
        symmetry_fields = []
        for field_index in [index + 1 for index in range(BOARD_SIZE ** 2) if index + 1 not in fields]:
            classifiers = self._get_classifiers(field_index)
            symmetry_field = field_index
            for classifier in classifiers:
                symmetry_field = self._perform_symmetry_on_field(symmetry_field, classifier)
                if symmetry_field == field:
                    symmetry_fields.append(symmetry_field)
        with open(Path(output_path).joinpath(f"{field}_results.txt"), "w") as result_file:
            result_file.write(f"Precision for field {field} {str(symmetry_fields)} is {precision}%")

    def _save_testing_results_for_evaluation_formulas(self, precision, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with open(Path(output_path).joinpath(f"evaluation_results.txt"), "w") as result_file:
            result_file.write(f"Precision for evaluation function is {precision}%")

    def generate_main_formulas(self, field, ones_conf, zeros_conf, num_formulas):
        data = self._get_data(BASE_DIR.joinpath(f"csv/main/{field}.csv"))
        train_data, ones, zeros, test_data = self._divide_data(data)
        one_formulas = []
        self._print_main_formulas_results(1, field, len(one_formulas), num_formulas)
        while len(one_formulas) < num_formulas:
            formula = self._create_main_formula(train_data, ones_conf[2], field, ones_conf[1], ones_conf[0])
            s1, n1 = self._check_formula(formula, ones)
            s0, n0 = self._check_formula(formula, zeros)
            if (s1 + n0) > 2 * (s0 + n1) and s1 > 1.5 * n1:
                if formula not in one_formulas:
                    one_formulas.append(formula)
                    self._print_main_formulas_results(1, field, len(one_formulas), num_formulas)
        zero_formulas = []
        self._print_main_formulas_results(0, field, len(zero_formulas), num_formulas)
        while len(zero_formulas) < num_formulas:
            formula = self._create_main_formula(train_data, zeros_conf[2], field, zeros_conf[1], zeros_conf[0])
            s0, n0 = self._check_formula(formula, zeros)
            s1, n1 = self._check_formula(formula, ones)
            if (s0 + n1) > 2 * (s1 + n0) and n1 >= 0.7 * s1:
                if formula not in zero_formulas:
                    zero_formulas.append(formula)
                    self._print_main_formulas_results(0, field, len(zero_formulas), num_formulas)
        precision = self._test_generated_formulas(test_data, one_formulas, zero_formulas)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"The formulas for field {field} were generated with precision equals {precision}%")
        _save_formulas_as_cnf_file(one_formulas, field, BASE_DIR.joinpath("cnf/main"), 1, ones_conf[1], num_formulas)
        _save_formulas_as_cnf_file(zero_formulas, field, BASE_DIR.joinpath("cnf/main"), 0, zeros_conf[1], num_formulas)
        self._save_testing_results_for_main_formulas(field, precision, BASE_DIR.joinpath("cnf/main/results"))

    def generate_rest_main_formulas(self, formula_type):
        symmetry_fields_indexes = []
        oddity_bonus = 0 if BOARD_SIZE % 2 == 0 else 1
        center = (BOARD_SIZE // 2) + oddity_bonus
        for i in range(1, center + 1):
            for j in range(1, i + 1):
                symmetry_fields_indexes.append((BOARD_SIZE * i) - (BOARD_SIZE - j))
        rest_fields_indexes = [index + 1 for index in range(BOARD_SIZE ** 2) if
                               index + 1 not in symmetry_fields_indexes]
        for field_index in rest_fields_indexes:
            classifiers = self._get_classifiers(field_index)
            target_field = field_index
            for classifier in classifiers:
                target_field = self._perform_symmetry_on_field(target_field, classifier)
            classifiers.reverse()
            with open(BASE_DIR.joinpath(f"cnf/main/{target_field}_{formula_type}.cnf"), "r") as cnf_file:
                content = [line.strip() for line in cnf_file if not line.startswith('c')]
                parameters = content[0]
                clauses = self._get_clauses_as_tuples(content[1:])
            new_clauses = copy.deepcopy(clauses)
            for classifier in classifiers:
                new_clauses = self._perform_symmetry_on_clauses(new_clauses, classifier)
            with open(BASE_DIR.joinpath(f"cnf/main/{field_index}_{formula_type}.cnf"), "w") as cnf_file:
                cnf_file.write(f"c {field_index}_{formula_type}.cnf\nc\n")
                cnf_file.write(f"c field = {field_index}\nc formula set type = {formula_type}\nc\n")
                cnf_file.write(f"{parameters}\n")
                for clause in new_clauses:
                    for game_state_property in clause:
                        column_index = ((game_state_property[2] - 1) * 2) + game_state_property[1]
                        if game_state_property[0]:
                            cnf_file.write(f"-{column_index} ")
                        else:
                            cnf_file.write(f"{column_index} ")
                    cnf_file.write("\n")

    def generate_evaluation_formulas(self, ones_conf, zeros_conf, num_formulas):
        data = self._get_data(BASE_DIR.joinpath("csv/evaluation/evaluation.csv"))
        train_data, ones, zeros, test_data = self._divide_data(data)
        one_formulas = []
        self._print_evaluation_formulas_results(len(one_formulas), num_formulas, 1)
        while len(one_formulas) < num_formulas:
            formula = self._create_evaluation_formula(train_data, ones_conf[2], ones_conf[1], ones_conf[0])
            s1, n1 = self._check_formula(formula, ones)
            s0, n0 = self._check_formula(formula, zeros)
            if (s1 + n0) > 2 * (s0 + n1) and s1 > 1.5 * n1:
                if formula not in one_formulas:
                    one_formulas.append(formula)
                    self._print_evaluation_formulas_results(len(one_formulas), num_formulas, 1)
        zero_formulas = []
        self._print_evaluation_formulas_results(len(zero_formulas), num_formulas, 0)
        while len(zero_formulas) < num_formulas:
            formula = self._create_evaluation_formula(train_data, zeros_conf[2], zeros_conf[1], zeros_conf[0])
            s0, n0 = self._check_formula(formula, zeros)
            s1, n1 = self._check_formula(formula, ones)
            if (s0 + n1) > 2 * (s1 + n0) and s0 > 1.5 * n0:
                if formula not in zero_formulas:
                    zero_formulas.append(formula)
                    self._print_evaluation_formulas_results(len(zero_formulas), num_formulas, 0)
        precision = self._test_generated_formulas(test_data, one_formulas, zero_formulas)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"The evaluation formulas were generated with precision equals {precision}%")
        _save_formulas_as_cnf_file(one_formulas, None, BASE_DIR.joinpath("cnf/evaluation"), 1, ones_conf[1],
                                   num_formulas)
        _save_formulas_as_cnf_file(zero_formulas, None, BASE_DIR.joinpath("cnf/evaluation"), 0, zeros_conf[1],
                                   num_formulas)
        self._save_testing_results_for_evaluation_formulas(precision, BASE_DIR.joinpath("cnf/evaluation/results"))


class AdditionalGenerator:
    def _four_in_line_checker(self, field):
        formulas = []
        x, y = u.transform_index_to_coordinate(field, BOARD_SIZE)
        hx = x - 4
        for i in range(5):
            not_negated_indexes = []
            negated_indexes = []
            first_negate_x = x - 5 + i
            second_negate_x = x + 1 + i
            if 0 < first_negate_x <= BOARD_SIZE:
                negated_indexes.append((u.transform_coordinate_to_index(first_negate_x, y, BOARD_SIZE) - 1) * 2)
            if 0 < second_negate_x <= BOARD_SIZE:
                negated_indexes.append((u.transform_coordinate_to_index(second_negate_x, y, BOARD_SIZE) - 1) * 2)
            for j in range(5):
                tmp_hx = hx + i + j
                if 0 < tmp_hx <= BOARD_SIZE:
                    if tmp_hx != x:
                        not_negated_indexes.append((u.transform_coordinate_to_index(tmp_hx, y, BOARD_SIZE) - 1) * 2)
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
            if 0 < first_negate_y <= BOARD_SIZE:
                negated_indexes.append((u.transform_coordinate_to_index(x, first_negate_y, BOARD_SIZE) - 1) * 2)
            if 0 < second_negate_y <= BOARD_SIZE:
                negated_indexes.append((u.transform_coordinate_to_index(x, second_negate_y, BOARD_SIZE) - 1) * 2)
            for j in range(5):
                tmp_vy = vy + i + j
                if 0 < tmp_vy <= BOARD_SIZE:
                    if tmp_vy != y:
                        not_negated_indexes.append((u.transform_coordinate_to_index(x, tmp_vy, BOARD_SIZE) - 1) * 2)
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
            if 0 < first_negate_x <= BOARD_SIZE and 0 < first_negate_y <= BOARD_SIZE:
                negated_indexes.append(
                    (u.transform_coordinate_to_index(first_negate_x, first_negate_y, BOARD_SIZE) - 1) * 2)
            if 0 < second_negate_x <= BOARD_SIZE and 0 < second_negate_y <= BOARD_SIZE:
                negated_indexes.append(
                    (u.transform_coordinate_to_index(second_negate_x, second_negate_y, BOARD_SIZE) - 1) * 2)
            for j in range(5):
                tmp_d1x = d1x + i + j
                tmp_d1y = d1y + i + j
                if 0 < tmp_d1x <= BOARD_SIZE and 0 < tmp_d1y <= BOARD_SIZE:
                    if tmp_d1x != x and tmp_d1y != y:
                        not_negated_indexes.append(
                            (u.transform_coordinate_to_index(tmp_d1x, tmp_d1y, BOARD_SIZE) - 1) * 2)
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
            if 0 < first_negate_x <= BOARD_SIZE and 0 < first_negate_y <= BOARD_SIZE:
                negated_indexes.append(
                    (u.transform_coordinate_to_index(first_negate_x, first_negate_y, BOARD_SIZE) - 1) * 2)
            if 0 < second_negate_x <= BOARD_SIZE and 0 < second_negate_y <= BOARD_SIZE:
                negated_indexes.append(
                    (u.transform_coordinate_to_index(second_negate_x, second_negate_y, BOARD_SIZE) - 1) * 2)
            for j in range(5):
                tmp_d2x = d2x - i - j
                tmp_d2y = d2y + i + j
                if 0 < tmp_d2x <= BOARD_SIZE and 0 < tmp_d2y <= BOARD_SIZE:
                    if tmp_d2x != x and tmp_d2y != y:
                        not_negated_indexes.append(
                            (u.transform_coordinate_to_index(tmp_d2x, tmp_d2y, BOARD_SIZE) - 1) * 2)
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
            _save_formulas_as_cnf_file(value, field, BASE_DIR.joinpath("cnf/additional"), f"4_checker_{key}cl", key,
                                       len(value))

    def _three_in_line_checker(self, field):
        formulas = []
        x, y = u.transform_index_to_coordinate(field, BOARD_SIZE)
        hx = x - 3
        for i in range(4):
            not_negated_coordinates = []
            enemy_negated_coordinates = []
            first_enemy_negate_x = x - 4 + i
            second_enemy_negate_x = x + 1 + i
            if 0 < first_enemy_negate_x <= BOARD_SIZE:
                enemy_negated_coordinates.append((first_enemy_negate_x, y))
            if 0 < second_enemy_negate_x <= BOARD_SIZE:
                enemy_negated_coordinates.append((second_enemy_negate_x, y))
            if enemy_negated_coordinates:
                for j in range(4):
                    tmp_hx = hx + i + j
                    if 0 < tmp_hx <= BOARD_SIZE:
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
                    if 0 < min_x - 1 <= BOARD_SIZE and min_x - 1 != x:
                        self_negated_coordinates.append((min_x - 1, y))
                    if 0 < max_x + 1 <= BOARD_SIZE and max_x + 1 != x:
                        self_negated_coordinates.append((max_x + 1, y))
                    formulas.append(
                        [[(False, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, ((u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                   enemy_negated_coordinate[1],
                                                                   BOARD_SIZE) - 1) * 2) + 1)]] +
                        [[(True, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2)]
                         for coordinate in self_negated_coordinates])
                    formulas.append(
                        [[(False,
                           ((u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2) + 1)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, (u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                  enemy_negated_coordinate[1], BOARD_SIZE) - 1) * 2)]] +
                        [[(True,
                           ((u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2) + 1)]
                         for coordinate in self_negated_coordinates])
        vy = y - 3
        for i in range(4):
            not_negated_coordinates = []
            enemy_negated_coordinates = []
            first_enemy_negate_y = y - 4 + i
            second_enemy_negate_y = y + 1 + i
            if 0 < first_enemy_negate_y <= BOARD_SIZE:
                enemy_negated_coordinates.append((x, first_enemy_negate_y))
            if 0 < second_enemy_negate_y <= BOARD_SIZE:
                enemy_negated_coordinates.append((x, second_enemy_negate_y))
            if enemy_negated_coordinates:
                for j in range(4):
                    tmp_vy = vy + i + j
                    if 0 < tmp_vy <= BOARD_SIZE:
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
                    if 0 < min_y - 1 <= BOARD_SIZE and min_y - 1 != y:
                        self_negated_coordinates.append((x, min_y - 1))
                    if 0 < max_y + 1 <= BOARD_SIZE and max_y + 1 != y:
                        self_negated_coordinates.append((x, max_y + 1))
                    formulas.append(
                        [[(False, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, ((u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                   enemy_negated_coordinate[1],
                                                                   BOARD_SIZE) - 1) * 2) + 1)]] +
                        [[(True, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2)]
                         for coordinate in self_negated_coordinates])
                    formulas.append(
                        [[(False,
                           ((u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2) + 1)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, (u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                  enemy_negated_coordinate[1], BOARD_SIZE) - 1) * 2)]] +
                        [[(True, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                   BOARD_SIZE) - 1) * 2) + 1)]
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
            if 0 < first_enemy_negate_x <= BOARD_SIZE and 0 < first_enemy_negate_y <= BOARD_SIZE:
                enemy_negated_coordinates.append((first_enemy_negate_x, first_enemy_negate_y))
            if 0 < second_enemy_negate_x <= BOARD_SIZE and 0 < second_enemy_negate_y <= BOARD_SIZE:
                enemy_negated_coordinates.append((second_enemy_negate_x, second_enemy_negate_y))
            if enemy_negated_coordinates:
                for j in range(4):
                    tmp_d1x = d1x + i + j
                    tmp_d1y = d1y + i + j
                    if 0 < tmp_d1x <= BOARD_SIZE and 0 < tmp_d1y <= BOARD_SIZE:
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
                    if (0 < min_x - 1 <= BOARD_SIZE and min_x - 1 != x) and (
                            0 < min_y - 1 <= BOARD_SIZE and min_y - 1 != y):
                        self_negated_coordinates.append((min_x - 1, min_y - 1))
                    if (0 < max_x + 1 <= BOARD_SIZE and max_x + 1 != x) and (
                            0 < max_y + 1 <= BOARD_SIZE and max_y + 1 != y):
                        self_negated_coordinates.append((max_x + 1, max_y + 1))
                    formulas.append(
                        [[(False, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, ((u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                   enemy_negated_coordinate[1],
                                                                   BOARD_SIZE) - 1) * 2) + 1)]] +
                        [[(True, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2)]
                         for coordinate in self_negated_coordinates])
                    formulas.append(
                        [[(False, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                    BOARD_SIZE) - 1) * 2) + 1)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, (u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                  enemy_negated_coordinate[1],
                                                                  BOARD_SIZE) - 1) * 2)]] +
                        [[(True, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                   BOARD_SIZE) - 1) * 2) + 1)]
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
            if 0 < first_enemy_negate_x <= BOARD_SIZE and 0 < first_enemy_negate_y <= BOARD_SIZE:
                enemy_negated_coordinates.append((first_enemy_negate_x, first_enemy_negate_y))
            if 0 < second_enemy_negate_x <= BOARD_SIZE and 0 < second_enemy_negate_y <= BOARD_SIZE:
                enemy_negated_coordinates.append((second_enemy_negate_x, second_enemy_negate_y))
            if enemy_negated_coordinates:
                for j in range(4):
                    tmp_d2x = d2x - i - j
                    tmp_d2y = d2y + i + j
                    if 0 < tmp_d2x <= BOARD_SIZE and 0 < tmp_d2y <= BOARD_SIZE:
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
                    if (0 < max_x + 1 <= BOARD_SIZE and max_x + 1 != x) and (
                            0 < min_y - 1 <= BOARD_SIZE and min_y - 1 != y):
                        self_negated_coordinates.append((max_x + 1, min_y - 1))
                    if (0 < min_x - 1 <= BOARD_SIZE and min_x - 1 != x) and (
                            0 < max_y + 1 <= BOARD_SIZE and max_y + 1 != y):
                        self_negated_coordinates.append((min_x - 1, max_y + 1))
                    formulas.append(
                        [[(False, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, ((u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                   enemy_negated_coordinate[1],
                                                                   BOARD_SIZE) - 1) * 2) + 1)]] +
                        [[(True, (u.transform_coordinate_to_index(coordinate[0], coordinate[1], BOARD_SIZE) - 1) * 2)]
                         for coordinate in self_negated_coordinates])
                    formulas.append(
                        [[(False, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                    BOARD_SIZE) - 1) * 2) + 1)]
                         for coordinate in not_negated_coordinates] +
                        [[(True, (u.transform_coordinate_to_index(enemy_negated_coordinate[0],
                                                                  enemy_negated_coordinate[1], BOARD_SIZE) - 1) * 2)]] +
                        [[(True, ((u.transform_coordinate_to_index(coordinate[0], coordinate[1],
                                                                   BOARD_SIZE) - 1) * 2) + 1)]
                         for coordinate in self_negated_coordinates])
        formula_dict = {}
        for formula in formulas:
            number_of_clauses = len(formula)
            if number_of_clauses not in formula_dict:
                formula_dict[number_of_clauses] = []
            formula_dict[number_of_clauses].append(formula)
        for key, value in formula_dict.items():
            _save_formulas_as_cnf_file(value, field, BASE_DIR.joinpath("cnf/additional"), f"3_checker_{key}cl", key,
                                       len(value))

    def _nearby_field_checker(self, field):
        nearby_fields_indexes = []
        x, y = u.transform_index_to_coordinate(field, BOARD_SIZE)
        nearby_field_y = y - 1
        for i in range(0, 3):
            if i != 0:
                nearby_field_y += 1
            if 1 <= nearby_field_y <= BOARD_SIZE:
                for j in range(0, 3):
                    nearby_field_x = x - 1
                    if j != 0:
                        nearby_field_x += j
                    if 1 <= nearby_field_x <= BOARD_SIZE:
                        if not (nearby_field_x == x and nearby_field_y == y):
                            nearby_fields_indexes.append(
                                (u.transform_coordinate_to_index(nearby_field_x, nearby_field_y, BOARD_SIZE) - 1) * 2)
        clause = []
        for nearby_field_index in nearby_fields_indexes:
            clause.append((False, nearby_field_index))
            clause.append((False, nearby_field_index + 1))
        _save_formulas_as_cnf_file([[clause]], field, BASE_DIR.joinpath("cnf/additional"), "nearby_field_checker",
                                   1, 1)

    def generate(self):
        for field in range(1, (BOARD_SIZE ** 2) + 1):
            self._four_in_line_checker(field)
            self._three_in_line_checker(field)
            self._nearby_field_checker(field)


def _save_formulas_as_cnf_file(formulas, field, output_path, formula_type, number_of_clauses, number_of_formulas):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if field:
        file_dir = Path(output_path).joinpath(f"{field}_{formula_type}.cnf")
        comments = (f"c {field}_{formula_type}.cnf\n"
                    f"c\n"
                    f"c field = {field}\n"
                    f"c formula set type = {formula_type}\n"
                    f"c\n"
                    f"p cnf {number_of_clauses} {number_of_formulas}\n")
    else:
        file_dir = Path(output_path).joinpath(f"evaluation_player_{formula_type}.cnf")
        comments = (f"c evaluation_player_{formula_type}.cnf\n"
                    f"c\n"
                    f"c evaluation function\n"
                    f"c player = {formula_type}\n"
                    f"c\n"
                    f"p cnf {number_of_clauses} {number_of_formulas}\n")
    with open(file_dir, "w") as cnf_file:
        cnf_file.write(comments)
        for formula in formulas:
            for clause in formula:
                for literal in clause:
                    cnf_file.write(f"-{literal[1]} ") if literal[0] else cnf_file.write(f"{literal[1]} ")
                cnf_file.write("\n")


def main():
    ag = AdditionalGenerator()
    ag.generate()
    mg = MainGenerator()
    mg.generate_evaluation_formulas([3, 25, [1, 2, 3]], [3, 45, [1, 2]], 100)
    fields = [1, 17, 32, 33, 47, 48, 49, 61, 62, 63, 64, 65, 76, 77, 78, 79, 80, 91, 92, 93, 94, 97, 106, 107, 108, 109,
              110, 112]
    for field in fields:
        mg.generate_main_formulas(field, [3, 25, [0, 3, 4]], [3, 25, [1, 2]], 100)
    fields = [31, 46]
    for field in fields:
        mg.generate_main_formulas(field, [4, 25, [0, 3, 4]], [3, 25, [1, 2]], 100)
    fields = [16]
    for field in fields:
        mg.generate_main_formulas(field, [4, 20, [0, 3, 4]], [3, 25, [1, 2]], 100)
    fields = [113]
    for field in fields:
        mg.generate_main_formulas(field, [3, 45, [0, 3, 4]], [3, 25, [1, 2]], 100)
    fields = [81, 95, 96, 111]
    for field in fields:
        mg.generate_main_formulas(field, [3, 70, [1, 2, 3, 4]], [3, 25, [1, 2]], 100)
    mg.generate_rest_main_formulas(0)
    mg.generate_rest_main_formulas(1)


if __name__ == "__main__":
    main()
