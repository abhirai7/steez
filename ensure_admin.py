import json
import os

from colorama import Fore, Style, init

from src.server import app, db
from src.server.models import Users

init(autoreset=True)

CONFIG_FILE = ".config.env.json"


def log_info(message):
    print(Fore.GREEN + "[INFO] " + Style.RESET_ALL + message)


def log_error(message):
    print(Fore.RED + "[ERROR] " + Style.RESET_ALL + message)


def log_input(message):
    while True:
        try:
            is_input = input(Fore.YELLOW + "[INPUT] " + Style.RESET_ALL + message)
            if not is_input:
                log_error("Input cannot be empty. Please try again.")
                continue
            return is_input
        except KeyboardInterrupt:
            log_error("KeyboardInterrupt detected. Exiting...")
            exit(1)


def create_admin():
    name = log_input("Enter admin name: ")
    email = log_input("Enter admin email: ")
    password_raw = log_input("Enter admin password: ")
    phone = log_input("Enter admin phone: ")
    address = log_input("Enter admin address: ")

    password_hashed = Password(password_raw).hex

    with app.app_context():
        admin_user = Users(
            NAME=name,
            EMAIL=email,
            PASSWORD=password_hashed,
            PHONE=phone,
            ADDRESS=address,
            ROLE="ADMIN",
        )

        db.session.add(admin_user)
        db.session.commit()

    log_info(f"Admin `{name}` created successfully.")

    return {
        "name": name,
        "email": email,
        "password": password_hashed,
        "phone": phone,
        "address": address,
        "role": "ADMIN",
    }


def save_to_config(admin_data):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
    else:
        config_data = {"admins": []}

    config_data["admins"].append(admin_data)

    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

    log_info(f"Admin details saved to `{CONFIG_FILE}`.")


def setup_admins():
    log_info("Starting admin setup...")

    while True:
        admin_data = create_admin()
        save_to_config(admin_data)

        another = log_input("Do you want to add another admin? (y/n): ").lower()
        if another != "y":
            break

    log_info("Admin setup completed.")


if __name__ == "__main__":
    setup_admins()
