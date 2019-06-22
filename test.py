import re

name = "nande koko ni sensei ga less censored 11"

names = ["Nande Koko ni Sensei ga! 11 [Less censored 720p Eng-sub].mkv", "Nande Koko ni Sensei ga! 10 [Less censored 720p Eng-sub].mkv", "Nande Koko ni Sensei ga! 09 [Less censored 720p Eng-sub].mkv"]

for n in names:
    n = re.sub(r'[^\w]', ' ', n).lower()
    n1 = name.split(' ')
    nb = True
    for nm in n1:
        if nm not in n:
            nb = False
    if nb == True:
        print(n)