text = "Alec"
num = [str(ord(char) - 96).zfill(2) for char in text.lower()]
print(num)
temp = float("0." + "".join(num)).as_integer_ratio()
print(temp[0]*0.0000629921)
