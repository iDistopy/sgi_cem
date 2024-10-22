from django.db import models
from django.contrib.auth.models import User

class Alumno(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    programa_intercambio = models.CharField(max_length=255)
    fecha_postulacion = models.DateField(null=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    archivos = models.FileField(upload_to='archivos/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Familiar(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    alumno_adoptado = models.ForeignKey(Alumno, on_delete=models.SET_NULL, null=True)

class PersonalCEM(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    permisos_limite = models.CharField(max_length=100)

class PersonalCEL(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    permisos_limite = models.CharField(max_length=100)

class Administrador(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    acceso_total = models.BooleanField(default=True)

class Programa(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    carrera = models.TextField()
    pais = models.TextField()
    ciudad = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
class Postulacion(models.Model):
    ESTADOS_POSTULACION = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]

    programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    estado = models.CharField(max_length=10, choices=ESTADOS_POSTULACION, default='pendiente')

    def __str__(self):
        return f'{self.nombre} {self.apellido_paterno} {self.apellido_materno} - {self.programa.nombre}'
    
class Documento(models.Model):
    alumno = models.ForeignKey(Alumno, related_name='documentos', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='documentos/')

    def __str__(self):
        return f'Documento {self.id} de {self.alumno.user.username}'

class Calificacion(models.Model):
    alumno = models.ForeignKey(User, on_delete=models.CASCADE)
    asignatura = models.CharField(max_length=255)
    calificacion = models.DecimalField(max_digits=4, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.alumno.username} - {self.asignatura}'