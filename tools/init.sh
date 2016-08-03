cd ..
cp ./mysite/settings_default.py ./mysite/settings.py
sudo pip install -r requirement.txt
python manage.py migrate
