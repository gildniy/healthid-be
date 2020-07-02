import random


def generate_password():
    e_id = ''.join(random.choice('23456789ABCDEFGabcde') for _ in range(12))
    return e_id
