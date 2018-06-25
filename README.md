Admin Pixz

git add -A
git commit -m "descripcion"
git push -u origin master
git subtree push --prefix pixz_interno heroku master     (subir solo subcarpeta del repositorio que contiene el proyecto)


heroku run python manage.py shell