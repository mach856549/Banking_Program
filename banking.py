import sqlite3
import random

cc_connection = sqlite3.connect("card.s3db")
cc_cursor = cc_connection.cursor()
# cc_cursor.execute('DELETE FROM card;')
# cc_connection.commit()
cc_cursor.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
cc_connection.commit()
# Read existing database components into code then re-write code to work with database
cc_cursor.execute('SELECT number, pin FROM card;')
id_database = cc_cursor.fetchall()
id_list = []

for i in id_database:
    id_list.append(i[0])
# id_list is now a list of all credit card numbers


class CreditCard:
    global id_list
    number = None  # Stored as a string
    name = None
    pin = None  # Stored as a string
    balance = 0

    def __init__(self):
        global id_list
        new_num = "failed"
        while new_num == "failed":
            new_num, new_pin = CreditCard.create_new_number()
        self.number = str(new_num)
        self.pin = str(new_pin)
        id_list.append(self.number)
        id1 = len(id_list)
        cc_cursor.execute('INSERT INTO card (id, number, pin, balance)'
                          f"     VALUES ({id1}, '{self.number}', '{self.pin}', {self.balance});")
        cc_connection.commit()

    @staticmethod
    def create_new_number():
        IIN = "400000"
        # card_no = '400000' + '{:10d}'.format(random.randrange(0000000000, 9999999999))
        # self.number = f'400000{random.randint(0, 999999999):09d}{random.randint(0, 9)}'
        account_number = f"{random.randint(0, 999999999):09d}"
        checksum = CreditCard.luhn_check(IIN + account_number, False)
        new_card_number = (IIN + account_number + str(checksum))
        new_pin = f"{random.randint(0, 9999):04d}"
        if new_card_number not in id_list:
            return new_card_number, new_pin
        else:
            return "failed", "failed"

    # if called with a 15 digit number will return the checksum for True
    # if called with a 16 digit number will return True or False
    @staticmethod
    def luhn_check(cc_number, checksum=True):
        # if checksum = True then cc_number includes a checksum figure: Returns True if Pass, False if Fail
        # if checksum = False then cc_number has been passed without a checksum and this code will return checksum
        cc_digits = list(str(cc_number))
        cc_number_length = len(cc_number)
        for j in range(cc_number_length):
            cc_digits[j] = int(cc_digits[j])

        if checksum:
            checksum_number = cc_digits[-1]
            cc_digits = cc_digits[:cc_number_length - 1]

        if len(cc_digits) < 15:
            print("CC numbers passed to luhn is <15 digits")
            return False

        luhn_multiplier = [1] * len(cc_digits)
        for k in range(len(cc_digits) + 1):
            if k % 2 != 0:
                luhn_multiplier[-1 * k] = 2

        luhn_sum = 0
        counter = 0

        for m in cc_digits:
            m *= luhn_multiplier[counter]
            counter += 1
            if m > 9:
                m -= 9
            luhn_sum += m

        if checksum:
            if (luhn_sum + checksum_number) % 10 == 0:
                return True
            else:
                return False
        else:
            if luhn_sum % 10 == 0:
                return 0
            else:
                checksum_new = 10 - (luhn_sum % 10)
                return checksum_new


def check_pin(cc_number, user_pin):
    cc_cursor.execute(f'SELECT pin FROM card WHERE number={cc_number};')
    correct_pin = cc_cursor.fetchone()[0]
    return correct_pin == user_pin


def option_menu1():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    option = int(input())

    if option == 1:
        new_card = CreditCard()
        print("Your card has been created")
        print("Your card number:")
        print(new_card.number)
        print("Your card PIN:")
        print(new_card.pin)
        print()
        option_menu1()
    elif option == 2:
        log_in()
    elif option == 0:
        print("Bye!")
        exit()
    else:
        print(f"{option} is not a valid input, please select 1, 2 or 0.")
        option_menu1()


def log_in():
    user_card_number = input("Enter your card number:")
    if user_card_number in id_list:
        user_pin = input("Enter your PIN:")
        if check_pin(user_card_number, user_pin):
            print("You have successfully logged in!")
            option_logged_in(user_card_number)
        else:
            print("Wrong card number or PIN!")
            option_menu1()
    else:
        print("Wrong card number or PIN!")
        option_menu1()


def option_logged_in(user_card_number):
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")
    option = int(input())

    if option == 1:
        cc_cursor.execute(f'SELECT balance FROM card WHERE number={user_card_number};')
        balance = cc_cursor.fetchone()[0]
        print(f"Balance: {balance}")
        option_logged_in(user_card_number)
    elif option == 2:
        cc_cursor.execute(f'SELECT id, pin, balance FROM card WHERE number={user_card_number};')
        existing_entry = cc_cursor.fetchone()
        balance_add = int(input("How much would you like to add?"))
        balance = int(existing_entry[2]) + balance_add
        print(balance)
        cc_cursor.execute(f'DELETE FROM card WHERE number={user_card_number};')
        cc_cursor.execute('INSERT INTO card (id, number, pin, balance) '
                          f"VALUES ({existing_entry[0]}, '{user_card_number}', '{existing_entry[1]}', {balance});")
        cc_connection.commit()
        option_logged_in(user_card_number)
    elif option == 3:
        cc_cursor.execute(f'SELECT id, pin, balance FROM card WHERE number={user_card_number};')
        account_out = cc_cursor.fetchone()
        user_card_number_in = input("What is the account number that you would like to transfer to")
        if user_card_number == user_card_number_in:
            print("You can't transfer money to the same account!")
            option_logged_in(user_card_number)
        elif not CreditCard.luhn_check(user_card_number_in):
            print("Probably you made a mistake in the card number. Please try again!")
            option_logged_in(user_card_number)
        elif user_card_number_in not in id_list:
            print("Such a card does not exist.")
            option_logged_in(user_card_number)
        else:
            print(f"Current Balance = {account_out[2]}")
            bal_transfer = int(input("How much would you like to transfer?"))
            print(bal_transfer, account_out[2])
            if bal_transfer > int(account_out[2]):
                print("Not enough money!")
                option_logged_in(user_card_number)
            else:
                cc_cursor.execute(f'SELECT id, pin, balance FROM card WHERE number={user_card_number_in};')
                account_in = cc_cursor.fetchone()
                balance_in = int(account_in[2]) + bal_transfer
                balance_out = int(account_out[2]) - bal_transfer
                cc_cursor.execute(f'DELETE FROM card WHERE number={user_card_number_in};')
                cc_cursor.execute('INSERT INTO card (id, number, pin, balance) '
                                  f"VALUES ({account_in[0]}, '{user_card_number_in}', '{account_in[1]}', "
                                  f"{balance_in});")
                cc_connection.commit()
                cc_cursor.execute(f'DELETE FROM card WHERE number={user_card_number};')
                cc_cursor.execute('INSERT INTO card (id, number, pin, balance) '
                                  f"VALUES ({account_out[0]}, '{user_card_number}', '{account_out[1]}', "
                                  f"{balance_out});")
                cc_connection.commit()
                option_logged_in(user_card_number)
    elif option == 4:
        if user_card_number in id_list:
            cc_cursor.execute(f'DELETE FROM card WHERE number={user_card_number}')
            cc_connection.commit()
            print(f"Card {user_card_number} has been deleted.")
            option_menu1()
        else:
            print("Such a card does not exist.")
            option_logged_in(user_card_number)
    elif option == 5:
        print("You have successfully logged out!")
        option_menu1()
    elif option == 0:
        print("Bye!")
        exit()
    else:
        print(f"{option} is not a valid input, please select 1, 2, 3, 4, 5 or 0.")
        option_logged_in(user_card_number)


option_menu1()
