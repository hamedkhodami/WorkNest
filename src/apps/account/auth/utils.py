

def is_melli_code(melli_code):
    if melli_code.isdigit() and len(melli_code) == 10:
        first_number = int(melli_code[0])
        counter = 0
        total_sum = 0
        for i in range(1, 10):
            num = int(melli_code[i - 1])
            if num == first_number:
                counter += 1
            total_sum += num * (11 - i)
        r = total_sum % 11
        if r > 1:
            r = 11 - r
        if r == int(melli_code[-1]) and counter < 9:
            return True
    return False