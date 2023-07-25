import math


def transform_index_to_coordinate(index, board_size):
    return ((index - 1) % board_size) + 1, math.ceil(index / board_size)


def transform_coordinate_to_index(x, y, board_size):
    return (board_size * y) - (board_size - x)
