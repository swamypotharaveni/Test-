num=1
reversed_num=0

while num >0:
    reversed_num =reversed_num*10 +num%10
    num= num //10
print(reversed_num)
