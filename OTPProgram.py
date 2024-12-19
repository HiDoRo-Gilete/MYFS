import OTP

def start():
    print("OTP Program is starting!")
    try:
        user_input_str = input("Enter X (4 digit number): ").strip()
    except EOFError:
        print("No input. Program exited.")
        return False
    if not user_input_str.isdigit() or len(user_input_str) != 4:
        print("Invalid format X!")
    else:
        user_input = int(user_input_str)
        generated_otp = OTP.make_smartOTP(user_input)
        print(f"Your smart OTP is {generated_otp}")

start()