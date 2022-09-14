#a^3+b^3=c^3+d^3을 만족하는 1000이하의 자연수
for a in range(1,1000):
    for b in range(1,1000):
        for c in range(1,1000):
            for d in range(1,1000):
                if a==c and b==d or a==d and b==c:
                    continue
                if a**3+b**3==c**3+d**3:
                    print(a,b,c,d)
