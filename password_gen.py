import random
import string

def generate_password(length, use_upper, use_lower, use_numbers, use_symbols):
    characters = ""
    if use_upper:
        characters += string.ascii_uppercase
    if use_lower:
        characters += string.ascii_lowercase
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation
    if not characters:
        raise ValueError("At least one character type must be selected for the password.")
    password = ''.join(random.choice(characters) for _ in range(length))
    return password
