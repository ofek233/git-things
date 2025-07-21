def decToBin(numD):
    numD = int(numD)
    if numD < 0:
        print("Input must be a non-negative number")
        return
    
    if numD == 0:
        return "0"
    
    binary = ""
    while numD > 0:
        binary = str(numD % 2) + binary
        numD //= 2

    return(binary)

def bin_to_negative(numB):
    numB = str(numB)
    if numB[0] == '0':
        return numB
    else:
        inverted = ''.join('1' if bit == '0' else '0' for bit in numB)
        inverted_decimal = int(inverted, 2) + 1
        return decToBin(inverted_decimal)
    

dec = int(input("Enter a decimal number: "))

binary = decToBin(dec)
negative_binary = bin_to_negative(binary)
print("Negative binary representation (two's complement):", negative_binary)
