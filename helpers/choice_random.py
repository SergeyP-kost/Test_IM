import random


def select_random_items(source_list, count):
    """Выбрать случайные элементы из списка"""
    if count > len(source_list):
        count = len(source_list)
    return random.sample(source_list, count)