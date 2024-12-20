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
    random_two = [str(random.randint(0, 9)),str(random.randint(0,9))]
    Y = f"{six_digits:06d}"
    index0 = (int(Y[0]) + int(Y[1]) * int(Y[2]))%8
    index1 = (int(Y[3]) + int(Y[4]) * int(Y[5]))%8
    if index0 == index1: index0 =index0 -1 if index0 !=0 else index0+1
    if index0<index1:
        Y = Y[:index0] +random_two[0]+Y[index0:]
        Y = Y[:index1] +random_two[1]+Y[index1:]
    else:
        Y = Y[:index1] +random_two[1]+Y[index1:]
        Y = Y[:index0] +random_two[0]+Y[index0:]
    return Y
def verify(user_input,x_value):
    pseudo_random = (x_value * 1103515245 + 12345) & 0x7fffffff
    six_digits = pseudo_random % 1000000
    Y = f"{six_digits:06d}"
    index0 = (int(Y[0]) + int(Y[1]) * int(Y[2]))%8
    index1 = (int(Y[3]) + int(Y[4]) * int(Y[5]))%8
    if index0 == index1: index0 =index0 -1 if index0 !=0 else index0+1
    if index0<index1:
        user_input = user_input[:index1] +user_input[index1+1:]
        user_input = user_input[:index0] +user_input[index0+1:]
    else:
        user_input = user_input[:index0] +user_input[index0+1:]
        user_input = user_input[:index1] +user_input[index1+1:]
    return user_input==Y
def otp():
    x_value = getX()
    print(f"The X just sent to you is {x_value}")

    #generated_otp = make_smartOTP(x_value)
    #print(f"The Y calculated from X on your device is {generated_otp}")
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
        if verify(user_input, x_value):
            print("Successfully authenticated!")
            input()
            return True
        else:
            attempts += 1
            print("Wrong OTP. Try again.")

    print("Failed 3 times. Program exited.")
    return False
