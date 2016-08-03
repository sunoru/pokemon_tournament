cd ..
cp .\mysite\settings_default.py .\mysite\settings.py
pip install -r requirement.txt
python .\manage.py migrate
python .\manage.py shell
