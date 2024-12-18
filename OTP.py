import time
import random
import sys

def getX():
    random.seed(time.time())
    x_value = random.randint(1000, 9999)
    return x_value
def make_smartOTP(x_value):
    pseudo_random = (x_value * 1103515245 + 12345) & 0x7fffffff
    six_digits = pseudo_random % 1000000
    random_two = random.randint(0, 99)
    Y = f"{six_digits:06d}{random_two:02d}"
    return Y
def verify(user_input,generated_otp):
    return user_input[:6]==generated_otp[:6]
def run():
    x_value = getX()
    print(f"The X just sent to you is {x_value}")

    generated_otp = make_smartOTP(x_value)
    print(f"The Y calculated from X on your device is {generated_otp}")
    print("Note: " + ("The OTP will be expired in 20 seconds" if random.randint(0,1) == 0 else "You can try up to 3 times"))
    sys.stdout.flush()

    start_time = time.time()
    attempts = 0
    max_attempts = 3
    timeout = 20

    while attempts < max_attempts:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print("OTP is expired (20 seconds elapsed)")
            return False

        try:
            user_input_str = input("Enter OTP (8 digit number): ").strip()
        except EOFError:
            print("No input. Program exited.")
            return False

        elapsed = time.time() - start_time
        if elapsed > timeout:
            print("OTP expired (20 seconds elapsed)")
            return False

        if not user_input_str.isdigit() or len(user_input_str) != 8:
            attempts += 1
            print("Invalid input. Try again.")
            continue

        user_input = user_input_str
        if verify(user_input, generated_otp):
            print("Successfully authenticated!")
            input()
            return True
        else:
            attempts += 1
            print("Wrong OTP. Try again.")

    print("Failed 3 times. Program exited.")
    return False
