#function for cecking passwords

#remember to add more functionality

def password_checker(password):
    
    special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '?', '/', ';', ':', '{', '}', '_', '-']
    if len(password) < 10:
        return "Password must be atleast 10 characters in length"
    if len(password) > 20:
        return "Password length cannot exceed 20 characters"
    
    special_char_count = 0
    for char in password:
        if char in special_chars:
            special_char_count += 1
    if special_char_count == 0:
        return "Password must contain at least 1 special character"
    return "Good password!"