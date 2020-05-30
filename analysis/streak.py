from collections import defaultdict



def get_longest_sequence(seq):
    """
    Get the longest sequence, where each element is increaed by 1

    @args:
      seq(list): e.g.  [ 0,  1,  2,  3,  9, 19, 20]
    return:
        existing_sequence(dict): is a dict which contains the length of all sequences

    """
    '#1.Step: Initials variables'
    existing_sequence = defaultdict(int)
    current_sequence_length = 0
    '#2.Step: Loop for the seq'
    for i in range(0, len(seq)-1):
        '#2.1.Step: Compare if next element is one bigger'
        if (seq[i]+1) == (seq[i+1]):
            current_sequence_length += 1
            '#Check if current element is last element'
            if (i+2)==len(seq):
                current_sequence_length += 1
        else:
            current_sequence_length += 1
            existing_sequence[current_sequence_length]+=1

            current_sequence_length = 0

    '#3.Step: Add current sequence to dict'
    existing_sequence[current_sequence_length] += 1
    return existing_sequence


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)