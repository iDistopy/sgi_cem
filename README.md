Instalar:
- pip install django
- pip install django-extensions
- py -m pip install Pillow

Activar base de datos:
- py manage.py makemigrations
- py manage.py migrate
- py manage.py makemigrations sgi_web
- py manage.py migrate sgi_web

Correr servidor:
- py manage.py runserver

Ajustar configuración:
- py manage.py createsuperuser
- Colocar los datos
- Acceder a http://127.0.0.1:8000/admin y iniciar sesión

Añadir "Groups":
- Alumno
- Familiar
- Administrador
- Personal CEM
- Personal CEL
