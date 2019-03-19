import numpy as np
from .distance_matrix import partition_matrix, MatrixIterBlock


# show matrix iteration order
def show_matrix(y, x, blocks):
    mat = np.full((x, y), fill_value=-1, dtype=np.int)
    for i, block in enumerate(blocks):
        x, y, x2, y2 = block
        mat[y:y2+1, x:x2+1] = i
    return str(mat)


def test_partition_matrix_area_full():
    assert(
        show_matrix(2, 3, partition_matrix(2, 3, 6, 999))
    ) == '[[0 0]\n' \
         ' [0 0]\n' \
         ' [0 0]]'

    assert(
        show_matrix(3, 2, partition_matrix(3, 2, 6, 999))
    ) == '[[0 0 0]\n' \
         ' [0 0 0]]'


def test_partition_matrix_area_full_row():
    assert(
        show_matrix(3, 3, partition_matrix(3, 3, 6, 999))
    ) == '[[0 0 0]\n' \
         ' [0 0 0]\n' \
         ' [1 1 1]]'


def test_partition_matrix_area_incomplete_row():
    assert(
        show_matrix(3, 3, partition_matrix(3, 3, 5, 999))
    ) == '[[0 0 0]\n' \
         ' [1 1 1]\n' \
         ' [2 2 2]]'


def test_partition_matrix_area_col():
    assert(
        show_matrix(8, 8, partition_matrix(8, 8, 6, 999))
    ) == '[[ 0  0  0  0  0  0  1  1]\n' \
         ' [ 4  4  4  4  4  4  1  1]\n' \
         ' [ 5  5  5  5  5  5  1  1]\n' \
         ' [ 6  6  6  6  6  6  2  2]\n' \
         ' [ 7  7  7  7  7  7  2  2]\n' \
         ' [ 8  8  8  8  8  8  2  2]\n' \
         ' [ 9  9  9  9  9  9  3  3]\n' \
         ' [10 10 10 10 10 10  3  3]]'
