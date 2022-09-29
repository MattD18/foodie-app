
# delete and reset migrations folder
rm -r foodie/migrations/
mkdir foodie/migrations/
touch foodie/migrations/__init__.py

# add to psql to path
echo $PATH
if [[ ":$PATH:" == *":/Library/PostgreSQL/14/bin:$PATH:"* ]]; then
  echo "Your path is correctly set"
else
  echo "Adding Path"
fi
export PATH="/Library/PostgreSQL/14/bin:$PATH"
echo $PATH
dropdb -U postgres foodiedb