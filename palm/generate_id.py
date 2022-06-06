import random

def generate_hex_id(length=32):
    rand_int = random.randrange(10**80)
    hex_id = hex(rand_int)[:length]
    return hex_id
