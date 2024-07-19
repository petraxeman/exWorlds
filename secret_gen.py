import random as rnd



alph = list("qazwsxedcrfvtgbyhnujmikolp1234567890-")
secret = ""

for i in range(175):
    secret += rnd.choice(alph)

print(secret)