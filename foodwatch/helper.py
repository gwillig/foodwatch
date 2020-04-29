import numpy as np


def try_str_float(element):
    """
    Function try to convert a string to a float
    :param
        element (string): e.g. "NaN", 84.2, 16000
    :return:
    @Doctest
    >>> try_str_float(84.1)
    True
    >>> try_str_float('84.1')
    True
    >>> try_str_float('84,1')
    True
    >>> try_str_float('16000')
    True
    >>> try_str_float("NaN")
    False
    """
    try:
        '#1.0.Step: Convert element into string'
        element_str = str(element)
        '#1.1.Step: Replace the comma with a dot'
        element_dot = element_str.replace(",", ".")
        '#1.2.Step: Try to convert it to a float'
        element_float = float(element_dot)
        '#1.3.Step: Test if element_float is nan'
        if np.isnan(element_float) == True:
            return False
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
