import os

def convert_to_fraction(decimal):
    try:
        float_value = float(decimal)
        whole = int(float_value)
        frac = round((float_value - whole) * 16)
        if frac == 0:
            return str(whole)
        elif frac == 16:
            return str(whole + 1)
        mapping = {
            1: "1/16", 2: "1/8", 3: "3/16", 4: "1/4", 5: "5/16", 6: "3/8",
            7: "7/16", 8: "1/2", 9: "9/16", 10: "5/8", 11: "11/16", 12: "3/4",
            13: "13/16", 14: "7/8", 15: "15/16"
        }
        return f"{whole} {mapping[frac]}"
    except:
        return decimal

def process_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    data = [line.strip().split(';') for line in lines]
    empty_spaces = []
    carts_and_slots = []

    sorted_cart = sorted(data, key=lambda x: float(x[19]))
    alt_car = sorted_cart[0][19]
    for row in sorted_cart:
        if "/" not in row[18]:
            row[18] = convert_to_fraction(row[18])

    for row in sorted_cart:
        barcode, cart, slot = row[23], row[19], row[20]
        row[4] = 0
        for temp in sorted_cart:
            if temp[23] == barcode and temp[4] == '1' and temp[20] != slot:
                carts_and_slots = [temp[19], temp[20]]
                empty_spaces.append(carts_and_slots)
                temp[19], temp[20], temp[7], temp[6], temp[4] = cart, slot, cart, slot, 0

    if empty_spaces:
        numb = 0
        index = empty_spaces[numb]
        for temp1 in sorted_cart:
            if temp1[19] != alt_car:
                barcode = temp1[23]
                for temp2 in sorted_cart:
                    if temp2[23] == barcode and temp2[4] == 0 and temp2[19] != alt_car:
                        temp2[19], temp2[20], temp2[7], temp2[6] = index[0], index[1], index[0], index[1]
                        numb += 2
                        if numb < len(empty_spaces):
                            index = empty_spaces[numb]
                        else:
                            break

    data = sorted(sorted_cart, key=lambda x: float(x[0]))
    job_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = os.path.join(os.path.dirname(os.path.dirname(file_path)), job_name + "-SH.txt")
    with open(output_file, 'w') as f:
        for row in data:
            row[4] = '1'
            f.write(';'.join(map(str, row)) + '\n')
    return data, output_file
