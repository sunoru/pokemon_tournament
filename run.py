import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    from scripts import init
    from django.core.management import execute_from_command_line

    if len(sys.argv) > 1:
        execute_from_command_line(sys.argv)
        sys.exit(0)
    
    if not os.path.exists("./db.sqlite3"):
        execute_from_command_line(["django-admin", "migrate"])
        init.run()
    
    print("开启比赛服务器…")
    execute_from_command_line(["django-admin", "runserver", "--nothreading", "--noreload"])
