def new_password():

    password = input("Please enter a new password: ")
    count = 0
    if len(password) >= 8 and len(password) <= 11:
        count += 1
    if len(password) > 11:
        count += 2
    not_common = password.lower() not in ["password", "123456", "1234", "password123", "abc123", "admin"]
    if not_common == False:
        count -= 2
    has_upper = any(c.isupper() for c in password)
    if has_upper:
        count += 1
    if has_lower := any(c.islower() for c in password):
        count += 1
    if has_number := any(c.isdigit() for c in password):
        count += 1
    if has_special := any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in password):
        count += 1
    
    if count <= 0:
        print("Password is too weak, you are recommanded to try again.")
        return
    if count >=1 and count <= 3:
        print("Password is medium strength.")
        return
    if count >= 4:
        print("Password is strong and created successfully!")
        return

new_password()