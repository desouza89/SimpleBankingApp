lm = [int(i) for i in range(21)]

total = []
for index, number in enumerate(lm):
    if index % 2:
        total.append(number)

print(*total)
total = map(lambda x: x - 9 if x > 9 else x, total)
print(*total)