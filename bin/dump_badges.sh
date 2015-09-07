./manage.py dumpdata badges.BadgeCategory badges.Badge --indent 4 | grep -v '"image":' > badges/fixtures/badges.json 
