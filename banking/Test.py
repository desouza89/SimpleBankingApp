def has_valid_checksum(card_number):
    total = []
    check_digit = None

    if len(card_number) == 16:
        check_digit = int(card_number[-1])
        card_number = card_number[:-1]


    # Multiply odd digits by 2 + # Subtract 9 to numbers over 9 #
    for i, number in enumerate(card_number, start=1):

        if i % 2:
            total.append(int(number) * 2)
            continue
        total.append(int(number))

    total = list(map(lambda x: x - 9 if x > 9 else x, total))

    compare_digit = 10 - sum(i for i in total) % 10 if sum(i for i in total) % 10 else 0

    if check_digit:
        return compare_digit == check_digit
    return compare_digit


print(has_valid_checksum('3000003972196503'))
