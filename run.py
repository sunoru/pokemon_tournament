#!/bin/env python
import os
import pathlib
import sys

VERSION = "1.2.0"

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    from django.core.management import execute_from_command_line, call_command

    if len(sys.argv) > 1:
        execute_from_command_line(sys.argv)
        sys.exit(0)

    db_path = pathlib.Path(__file__).parent.resolve().joinpath("db.sqlite3")
    if not db_path.exists():
        print("开始初始化…")
        try:
            execute_from_command_line(["django-admin", "makemigrations", "accounts", "pmtour"])
            execute_from_command_line(["django-admin", "migrate"])
            from mysite import init
            init.run()
        except BaseException as e:
            print("初始化中断")
            if db_path.exists():
                db_path.unlink()
            raise e

    import django
    django.setup()

    print("开启比赛服务器…")
    call_command("runserver", "--nothreading", "--noreload")
