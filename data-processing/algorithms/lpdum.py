import os
import random
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


class FormulaGenerationAlgorithm:
    def _create_files_with_formulas(self, literal_number, clause_number, multi_number, formulas_labels, formulas_array,
                                    output_path, filename):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with open(output_path.joinpath(filename), "a") as file:
            file.write(f"c {filename}\n")
            file.write("c\n")
            for labels_index in range(len(formulas_labels)):
                file.write(f"c {labels_index} = {formulas_labels[labels_index]}\n")
            file.write("c\n")
            file.write(f"p cnf {literal_number} {clause_number} {multi_number}\n")
            for formulas in formulas_array:
                for clause in formulas:
                    for literal in clause:
                        if literal[1] == 0:
                            file.write(f"-{literal[0]}")
                        else:
                            file.write(str(literal[0]))
                        file.write(" ")
                    file.write("\n")

    def _get_best_formulas(self, formulas, formulas_statistics):
        best_formulas = []
        for formula_index in range(len(formulas)):
            tp = formulas_statistics[formula_index][0]
            fp = formulas_statistics[formula_index][1]
            tn = formulas_statistics[formula_index][2]
            fn = formulas_statistics[formula_index][3]
            if (tp + tn) / (fp + fn) > 2:
                best_formulas.append(formulas[formula_index])
        return best_formulas

    def _check_formulas_correctness_on_data_frame(self, data_frame, formulas, goal_index, goal_label_value):
        formulas_correctness_count = np.zeros(len(data_frame))
        formulas_effective_count = np.zeros(len(formulas))
        formulas_statistic = np.zeros((len(formulas), 4))
        for y in range(len(data_frame)):
            x = data_frame.iloc[y, :].values.tolist()
            index = 0
            for form in formulas:
                form_is_false = False
                for clause in form:
                    value_true = False
                    for literal in clause:
                        if x[literal[0]] == literal[1]:
                            value_true = True
                            break
                    if not value_true:
                        form_is_false = True
                        break
                if not form_is_false:
                    formulas_correctness_count[y] += 1
                    if bool(x[goal_index]) is goal_label_value:
                        formulas_effective_count[index] += 1
                        formulas_statistic[index][0] += 1
                    else:
                        formulas_effective_count[index] -= 1
                        formulas_statistic[index][1] += 1
                else:
                    if bool(x[goal_index]) is not goal_label_value:
                        formulas_effective_count[index] -= 1
                        formulas_statistic[index][2] += 1
                    else:
                        formulas_effective_count[index] += 1
                        formulas_statistic[index][3] += 1
                index += 1
        return formulas_correctness_count, formulas_effective_count, formulas_statistic

    def _create_formulas(self, data_frame, opposite_data_frame, literal_number, clause_number, formula_number):
        def create_positive_formula_array(data_frame_, literal_number_, clause_number_, formula_number_):
            row_number = len(data_frame_)
            column_number = len(data_frame_[0])
            formulas_array = []
            for _ in range(formula_number_):
                formula = []
                for clause in range(clause_number_):
                    clause = []
                    column_used = []
                    row_used = []
                    row_index = random.randint(0, row_number - 1)
                    column_index = random.randint(0, column_number - 1)
                    for _ in range(literal_number_):
                        while row_index in row_used:
                            row_index = random.randint(0, row_number - 1)
                        row_used.append(row_index)
                        while column_index in column_used:
                            column_index = random.randint(0, column_number - 1)
                        column_used.append(column_index)
                        values = data_frame_[row_index]
                        clause.append([column_index, values[column_index]])
                    formula.append(clause)
                formulas_array.append(formula)
            return formulas_array

        def create_negative_formula_array(data_frame_, literal_number_, clause_number_, formula_number_):
            row_number = len(data_frame_)
            column_number = len(data_frame_[0])
            formulas_array = []
            for _ in range(formula_number_):
                formula = []
                for clause in range(clause_number_):
                    clause = []
                    row_index = random.randint(0, row_number - 1)
                    column_used = []
                    column_index = random.randint(0, column_number - 1)
                    for literal in range(literal_number_):
                        while column_index in column_used:
                            column_index = random.randint(0, column_number - 1)
                        column_used.append(column_index)
                        values = data_frame_[row_index]
                        literal_value = 0
                        if values[column_index] == 0:
                            literal_value += 1
                        clause.append([column_index, literal_value])
                    formula.append(clause)
                formulas_array.append(formula)
            return formulas_array

        first = create_positive_formula_array(data_frame, literal_number, clause_number, int(formula_number / 2))
        second = create_negative_formula_array(opposite_data_frame, literal_number, clause_number,
                                               int(formula_number / 2))
        return first + second

    def _split_data_frame_to_positives_and_negatives_rows(self, data_frame, goal_column):
        positive = []
        negative = []
        for x in range(len(data_frame)):
            row = data_frame.iloc[x, :].values.tolist()
            value_of_correct = row[goal_column]
            del row[goal_column]
            if value_of_correct == 1:
                positive.append(row)
            else:
                negative.append(row)
        return positive, negative

    def run(self, csv_directory, number_of_training_loops, number_of_literals, number_of_clauses, number_of_formulas,
            goal_column, output_path):
        data_frame = pd.read_csv(csv_directory)
        if any(data_frame.dtypes != "int64") or any(data_frame.nunique() > 2):
            return 0
        train_data_frame, test_data_frame = train_test_split(data_frame, test_size=0.5)
        positive_rows, negative_rows = self._split_data_frame_to_positives_and_negatives_rows(train_data_frame,
                                                                                              goal_column)
        positive_formulas = []
        negative_formulas = []
        best_positive_formulas_end = False
        best_negative_formulas_end = False
        inter = 0
        while (not best_positive_formulas_end or not best_negative_formulas_end) and \
                (inter < number_of_training_loops):
            inter += 1
            try:
                positive_formulas += self._create_formulas(positive_rows, negative_rows, number_of_literals,
                                                           number_of_clauses,
                                                           int(number_of_formulas - len(positive_formulas)))
                negative_formulas += self._create_formulas(negative_rows, positive_rows, number_of_literals,
                                                           number_of_clauses,
                                                           int(number_of_formulas - len(negative_formulas)))
            except IndexError:
                return 0
            positive_correctness, positive_count, positive_formulas_statistic = \
                self._check_formulas_correctness_on_data_frame(train_data_frame, positive_formulas, goal_column, True)
            negative_correctness, negative_count, negative_formulas_statistic = \
                self._check_formulas_correctness_on_data_frame(train_data_frame, negative_formulas, goal_column, False)
            best_positive_formulas = self._get_best_formulas(positive_formulas, positive_formulas_statistic)
            best_negative_formulas = self._get_best_formulas(negative_formulas, negative_formulas_statistic)
            if len(best_positive_formulas) >= number_of_formulas:
                best_positive_formulas_end = True
            if len(best_negative_formulas) >= number_of_formulas:
                best_negative_formulas_end = True
            if inter < number_of_training_loops:
                positive_formulas = best_positive_formulas
                negative_formulas = best_negative_formulas
        positive_correctness, positive_count, positive_formulas_statistic = \
            self._check_formulas_correctness_on_data_frame(test_data_frame, positive_formulas, goal_column, True)
        negative_correctness, negative_count, negative_formulas_statistic = \
            self._check_formulas_correctness_on_data_frame(test_data_frame, negative_formulas, goal_column, False)
        effectiveness = 0
        for index in range(len(test_data_frame)):
            proposal_value = positive_correctness[index] > negative_correctness[index]
            x = test_data_frame.iloc[index, :].values.tolist()
            if bool(x[goal_column]) == proposal_value:
                effectiveness += 1
        precision_value = round(((effectiveness * 100) / len(test_data_frame)), 2)
        self._create_files_with_formulas(number_of_literals, number_of_clauses, number_of_formulas,
                                         test_data_frame.columns.values, positive_formulas, output_path,
                                         f"{Path(csv_directory).stem}-pos.cnf")
        self._create_files_with_formulas(number_of_literals, number_of_clauses, number_of_formulas,
                                         test_data_frame.columns.values, negative_formulas, output_path,
                                         f"{Path(csv_directory).stem}-neg.cnf")
        return precision_value
