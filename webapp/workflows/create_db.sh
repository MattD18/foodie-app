# createdb
echo $PATH
if [[ ":$PATH:" == *":/Library/PostgreSQL/14/bin:$PATH:"* ]]; then
  echo "Your path is correctly set"
else
  echo "Adding Path"
fi
export PATH="/Library/PostgreSQL/14/bin:$PATH"
echo $PATH
createdb -U postgres foodiedb


# create and run migrations
rm -r foodie/migrations/
mkdir foodie/migrations/
touch foodie/migrations/__init__.py
python manage.py makemigrations foodie
python manage.py migrate

# add restaurant data
cp workflows/scripts/load_restaurants_to_db.py load_restaurants_to_db.py
python load_restaurants_to_db.py
rm load_restaurants_to_db.py