import glob
import math
import os
import random
from pathlib import Path


class MainGenerator:
    def __init__(self, csv_files_directories, board_size, time_snapshot):
        self._csv_files_directories = csv_files_directories
        self._board_size = board_size
        self._goal_column = (board_size ** 2) * 2
        self._time_snapshot = time_snapshot

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

    def _transform_index_to_coordinate(self, index):
        return ((index - 1) % self._board_size) + 1, math.ceil(index / self._board_size)

    def _transform_coordinate_to_index(self, x, y):
        return (self._board_size * y) - (self._board_size - x)

    def _create_clause_fields_around(self, target_field, depth_level):
        fields_around_target = []
        target_x, target_y = self._transform_index_to_coordinate(target_field)
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
                            fields_around_target.append(self._transform_coordinate_to_index(x, y))
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
        target_x, target_y = self._transform_index_to_coordinate(target_field)
        depth_level = 1
        next_level_available = True
        while next_level_available:
            if target_x - depth_level <= 0 and \
                    target_y - depth_level <= 0 and \
                    target_x + depth_level > self._board_size and \
                    target_y + depth_level > self._board_size:
                next_level_available = False
            else:
                columns_in_level = []
                if 1 <= target_y - depth_level <= self._board_size:
                    for i in range(target_x - depth_level, target_x + depth_level + 1):
                        if 1 <= i <= self._board_size:
                            field = self._transform_coordinate_to_index(i, target_y - depth_level)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                if 1 <= target_y + depth_level <= self._board_size:
                    for i in range(target_x - depth_level, target_x + depth_level + 1):
                        if 1 <= i <= self._board_size:
                            field = self._transform_coordinate_to_index(i, target_y + depth_level)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                for i in range((target_y - depth_level) + 1, target_y + depth_level):
                    if 1 <= i <= self._board_size:
                        if target_x - depth_level >= 1:
                            field = self._transform_coordinate_to_index(target_x - depth_level, i)
                            columns_in_level.append((field - 1) * 2)
                            columns_in_level.append(((field - 1) * 2) + 1)
                        if target_x + depth_level <= self._board_size:
                            field = self._transform_coordinate_to_index(target_x + depth_level, i)
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

    def _save_formulas_as_cnf_file(self, formulas, field, formula_type, number_of_clauses, number_of_formulas):
        base_path = Path(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.exists(base_path.joinpath(f"cnf/{self._time_snapshot}")):
            os.makedirs(base_path.joinpath(f"cnf/{self._time_snapshot}"))
        with open(base_path.joinpath(f"cnf/{self._time_snapshot}/{field}_{formula_type}.cnf"), "w") as cnf:
            cnf.write(f"c {field}_{formula_type}.cnf\nc\n")
            cnf.write(f"c field = {field}\nc formula set type = {formula_type}\nc\n")
            cnf.write(f"p cnf {number_of_clauses} {number_of_formulas}\n")
            for formula in formulas:
                for clause in formula:
                    for literal in clause:
                        cnf.write(f"-{literal[1]} ") if literal[0] else cnf.write(f"{literal[1]} ")
                    cnf.write("\n")

    def _print_results(self, number_of_generated_files, number_of_files, field, number_of_generated_formulas,
                       number_of_formulas):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"ready {number_of_generated_files} of {number_of_files} files")
        print(f"{number_of_generated_formulas} out of {number_of_formulas} formulas were generated for field {field}")

    def run(self, formula_type, clause_types, number_of_literals, number_of_clauses, number_of_formulas, depth_level=1):
        number_of_generated_files = 0
        for file_directory in self._csv_files_directories:
            data = self._get_data(file_directory)
            ones, zeros, test_data = self._divide_data(data)
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
                self._save_formulas_as_cnf_file(one_formulas, field, formula_type, number_of_clauses,
                                                number_of_formulas)
                number_of_generated_files += 1
            if formula_type == 0:
                zero_formulas = []
                self._print_results(number_of_generated_files, len(self._csv_files_directories), field,
                                    len(zero_formulas), number_of_formulas)
                while len(zero_formulas) < number_of_formulas:
                    formula = self._create_formula(zeros, clause_types, field, number_of_clauses, number_of_literals,
                                                   depth_level)
                    s1, n1 = self._check_formula(formula, zeros)
                    s0, n0 = self._check_formula(formula, ones)
                    if (s1 + n0) > 2 * (s0 + n1) and n0 >= s0:
                        if formula not in zero_formulas:
                            zero_formulas.append(formula)
                            self._print_results(number_of_generated_files, len(self._csv_files_directories), field,
                                                len(zero_formulas), number_of_formulas)
                self._save_formulas_as_cnf_file(zero_formulas, field, formula_type, number_of_clauses,
                                                number_of_formulas)
                number_of_generated_files += 1


def main():
    base_directory = Path(os.path.dirname(os.path.abspath(__file__)))
    time_snapshot = "174223.838237"
    board_size = 15

    fields = [78, 93]
    csv_files_directories = [glob.glob(str(base_directory.joinpath(f"csv/{time_snapshot}/{field}.csv")))[0] for field in
                             fields]
    generator = MainGenerator(csv_files_directories, board_size, time_snapshot)
    formula_type = 0
    clause_types = [1, 2]
    number_of_literals = 3
    number_of_clauses = 25
    number_of_formulas = 100
    generator.run(formula_type, clause_types, number_of_literals, number_of_clauses, number_of_formulas)


if __name__ == "__main__":
    main()
