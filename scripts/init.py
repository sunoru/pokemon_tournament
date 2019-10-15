import getpass

from django.contrib.auth.models import User

from accounts.models import Option, PlayerUser


def run():
    Option.objects.create(option_name="uid", option_value="-1")
    print("新建管理员账号…")
    admin_username = input("用户名：")
    admin_email = input("Email：")
    while True:
        admin_pass = getpass.getpass("密码：")
        repeat_pass = getpass.getpass("重复密码：")
        if admin_pass != repeat_pass:
            print("密码不一致！")
        else:
            break
    superuser = User.objects.create_superuser(username=admin_username, email=admin_email, password=admin_pass)
    player_user = PlayerUser.objects.create(user=superuser, name=admin_username, player_id="admin")
    print("初始化成功！")
