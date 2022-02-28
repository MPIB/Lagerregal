def format_bytes(size, power=2**10):
    # 2**10 = 1024
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return "{0:.2f}{1}".format(size, power_labels[n] + "B")
