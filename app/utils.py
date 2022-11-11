import random
import string


def generate_pin_code(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for x in range(size))
