# Write your code here
import random
import sys
import sqlite3


MII = 400000
DATABASE_FILE_PATH = "/Users/sshiganov/PycharmProjects/" \
                     "Simple Banking System/Simple Banking System/task/banking/card.s3db"


def do_exit():
    print("\nBye!")
    return sys.exit(1)


def update_info(db_connection, logged_user_data):
    card_number = logged_user_data[0]

    try:
        return send_sql_query(db_connection, f"""SELECT number, balance FROM card WHERE number = {card_number}""")
    except sqlite3.Error as c:
        raise ConnectionError(f'Error {c} occurred')


def connect_database(file_path):
    table_creation_query = "CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT," \
                           " number TEXT UNIQUE, pin TEXT, balance INTEGER DEFAULT 0);"
    try:
        connect = sqlite3.connect('card.s3db')
        cursor = connect.cursor()
        cursor.execute(table_creation_query)
        return connect
    except (IOError, sqlite3.Error):
        raise RuntimeError(f'Error connecting to database path {file_path} or no response to {table_creation_query}')


def send_sql_query(db_connection, query):
    cursor = db_connection.cursor()
    try:
        send_query = cursor.execute(query)
        db_connection.commit()
        return send_query.fetchone()
    except sqlite3.Error as e:
        db_connection.commit()
        raise ConnectionError(f'Error result {e.args[0]}')


def has_valid_checksum(card_number):
    total = []
    check_digit = None

    if len(card_number) == 16:
        check_digit = int(card_number[-1])
        card_number = card_number[:-1]

    # Multiply odd digits by 2 + # Subtract 9 to numbers over 9 #
    for i, number in enumerate(card_number, start=1):

        if i % 2:
            total.append(int(number) * 2)
            continue
        total.append(int(number))

    total = list(map(lambda x: x - 9 if x > 9 else x, total))

    compare_digit = 10 - sum(i for i in total) % 10 if sum(i for i in total) % 10 else 0

    if check_digit:
        return compare_digit == check_digit
    return compare_digit


def create_account(db_connection):
    card_number = f'{MII}{random.randint(100000000, 999999999)}'
    checksum = has_valid_checksum(card_number)
    card_number = f'{card_number}{checksum}'
    card_pin = f'{random.randint(1000, 9999)}'

    try:
        send_sql_query(db_connection, f"INSERT INTO card (number, pin) VALUES ({card_number}, {card_pin})")
        print("\nYour card has been created")
        print(f"Your card number:\n{card_number}")
        print(f"Your card PIN:\n{card_pin}\n")
    except KeyError:
        # In case card_number already exists, generate card_number one more time
        create_account(db_connection)


def balance(db_connection, logged_user_data):
    card_number = logged_user_data[0]

    try:
        response = send_sql_query(db_connection, f"""SELECT balance FROM card WHERE number = {card_number}""")
        return response[0]
    except sqlite3.Error as c:
        raise ConnectionError(f'Error {c} occurred')


def do_transfer(db_connection, logged_user_data):
    user_card = logged_user_data[0]
    user_balance = logged_user_data[1]

    print("Transfer")
    card_to_transfer = input("Enter card number:\n")

    if not has_valid_checksum(card_to_transfer):
        return print("Probably you made a mistake in the card number. Please try again!\n")

    if not send_sql_query(db_connection, f"SELECT number FROM card WHERE number = {card_to_transfer}"):
        return print("Such a card does not exist.\n")

    amount_to_transfer = int(input("Enter how much money you want to transfer:\n"))
    if amount_to_transfer > user_balance:
        return print("Not enough money!\n")

    try:
        transfer_data = (card_to_transfer, 0)
        transfer_balance = update_info(db, transfer_data)
        send_sql_query(db_connection, f"""UPDATE card SET balance = {transfer_balance[1] + amount_to_transfer}\
                                        WHERE number = {card_to_transfer}""")
        send_sql_query(db_connection, f"""UPDATE card SET balance = {user_balance - amount_to_transfer}\
                                                WHERE number = {user_card}""")
        return print("Success!\n")

    except sqlite3.Error as e:
        return print(f"{e} occurred\n")


def close_account(db_connection, logged_user_data):
    card_number = logged_user_data[0]
    try:
        send_sql_query(db_connection, f"""DELETE FROM card WHERE number = {card_number} """)
        return print("The account has been closed!\n")
    except sqlite3.Error:
        return print("Such a card does not exist.\n")


def add_income(db_connection, logged_user_data):
    card_number = int(logged_user_data[0])
    user_balance = int(logged_user_data[1])

    try:
        income = int(input("Enter income:\n"))
        income += user_balance
        send_sql_query(db_connection, f"UPDATE card SET balance = {income} WHERE number = {card_number}")
        print("Income was added!\n")
        return 1
    except (ValueError, NameError) as e:
        raise ValueError(f"Error {e} occurred")


def log_into_account(db_connection):
    card_number = input("\nEnter your card number:")
    card_pin = input("Enter your PIN number:")

    try:
        output = send_sql_query(db_connection, f"""SELECT number, pin, balance FROM card
                                                WHERE number = {card_number} AND pin = {card_pin};""")
        if output:
            if card_number == output[0] and card_pin == output[1]:
                user_balance = output[2]
                print("You have successfully logged in!\n")
                return int(card_number), int(user_balance)
        print("Wrong card number or PIN!\n")

    except KeyError:
        print("Wrong card number or PIN!\n")


def show_menu(interface=None):
    if not interface:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        return input()

    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")
    return input()


while True:
    db = connect_database('card.s3db')
    a = show_menu()
    if a == "1":
        create_account(db)
        continue
    elif a == "2":
        logged = log_into_account(db)
        while True:
            b = show_menu(1)
            if b == "1":
                print(balance(db, logged), "\n")
            elif b == "2":
                add_income(db, logged)
            elif b == "3":
                do_transfer(db, logged)
            elif b == "4":
                close_account(db, logged)
                break
            elif b == "5":
                break
            elif b == "0":
                do_exit()
            logged = update_info(db, logged)
        continue
    do_exit()
