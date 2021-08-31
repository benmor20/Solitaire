from typing import Tuple, Union


def add_tuples(t1: Tuple, t2: Union[Tuple, int]) -> Tuple:
    if isinstance(t2, int):
        t2 = tuple([t2] * len(t1))
    if len(t1) != len(t2):
        raise ValueError(f't1 and t2 must have same length (received {len(t1)}, {len(t2)})')
    ret = []
    for index in range(len(t1)):
        ret.append(t1[index] + t2[index])
    return tuple(ret)


def subtract_tuples(t1: Tuple, t2: Union[Tuple, int]) -> Tuple:
    if isinstance(t2, int):
        t2 = tuple([t2] * len(t1))
    if len(t1) != len(t2):
        raise ValueError(f't1 and t2 must have same length (received {len(t1)}, {len(t2)})')
    ret = []
    for index in range(len(t1)):
        ret.append(t1[index] - t2[index])
    return tuple(ret)
