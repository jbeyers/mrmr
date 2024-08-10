import random

def get_randoms():
    return [random.randint(0, 65000) for i in range(10)]

def bytewise_xors(*args):
    if len(args) <2:
        raise ValueError('Need at least 2 lists of integers')
    result = args[0].copy()
    for arg in args[1:]:
        for i in range(len(result)):
            result[i] = result[i] ^ arg[i]
    return result

def shift_register(input, how_much):
    result = []
    lenny = len(input)
    for i in range(lenny):
        index = (i - how_much)%lenny
        result.append(input[index])
    return result

def get_parity(drives, shift):
    parity = [0 for i in range(len(drives[0]))]
    for i, drive in enumerate(drives):
        parity = bytewise_xors(parity, shift_register(drive, -i*shift))
        
    return parity

def reconstruct(seq, starting_byte):
    # TODO: Start again here
    pass


d1 = [2, 4, 8, 60001, 8279, 63471, 38186, 35323, 29830, 24039]
d0 = [1, 2, 4, 28989, 46965, 12350, 23716, 21612, 12108, 49903]

p0 = get_parity([d0,d1], 0)
p1 = get_parity([d0, d1], 1)
p2 = get_parity([d0, d1], 2)
print(p0)
print(p1)
print(p2)

r0 = bytewise_xors(p0, d1)
assert r0 == d0

i0 = bytewise_xors(p0, p1)
print(i0)
assert i0 == bytewise_xors(d1, shift_register(d1, -1))

print(bytewise_xors(i0, shift_register(i0, 1)))

print(d1)
f0 = bytewise_xors(d1, shift_register(d1,1))
print(f0)
answer = bytewise_xors(f0, shift_register(f0,1))
print(answer)