
rm -rf dist/

pyinstaller --onefile --windowed main.py
mv dist/main.app dist/LegoCatalog.app
mv dist/main dist/LegoCatalog
cp -r data/ dist/data/

# Restore with mysql lego_catalog < db_create.sql
mysqldump -u root lego_catalog > dist/db_create.sql

rm -rf build/


