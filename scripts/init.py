import getpass

from django.contrib.auth.models import User

from accounts.models import Option, PlayerUser


def run():
    Option.objects.create(option_name="uid", option_value="-1")
    print("Creating an administrator account...")
    admin_username = input("Username: ")
    admin_email = input("Email: ")
    while True:
        admin_pass = getpass.getpass("Password: ")
        repeat_pass = getpass.getpass("Repeat password: ")
        if admin_pass != repeat_pass:
            print("Repeat password does not match!")
        else:
            break
    superuser = User.objects.create_superuser(username=admin_username, email=admin_email, password=admin_pass)
    player_user = PlayerUser.objects.create(user=superuser, name=admin_username, player_id="admin")
    print("Initialized！")
