def new_password():

    password = input("Please enter a new password: ")
    long_enough = len(password) >= 8
    has_upper = any(c.isupper() for c in password)
    not_common = password.lower() not in ["password", "123456", "password123", "abc123", "admin"]

    if not_common == False:
        print("Password is too common. Please choose a different one.")
        return
    if (long_enough == True and has_upper==False) or (has_upper==True and long_enough==False):
        print("Password is medium strength.")
    if long_enough and has_upper and not_common:
        print("Password is strong and created successfully!")

new_password()