from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import Programa, Postulacion, Alumno, Documento


def inicio(request):
    context = {
        'es_personal_cem': es_personal_cem(request.user)
    }
    return render(request, 'index.html', context)

def es_personal_cem(user):
    return user.groups.filter(name__in=['Personal-CEM', 'Administrador']).exists()

@login_required
def programa_admin(request):
    # Verificar si el usuario es parte del grupo "Personal-CEM"
    if not es_personal_cem(request.user):
        return redirect('programa/alumno')  # Redirigir si no es Personal-CEM
    
    if request.method == 'POST':
        # Capturar los datos del formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        carrera = request.POST.get('carrera')
        pais = request.POST.get('pais')
        ciudad = request.POST.get('ciudad')

        # Crear el nuevo programa
        Programa.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            carrera=carrera,
            pais=pais,
            ciudad=ciudad
        )

        # Redirigir después de guardar el programa
        return redirect('programas/admin')
    
    # Obtener todos los programas para mostrarlos en la vista
    programas = Programa.objects.all()

    return render(request, 'programas/admin.html', {
        'programas': programas,
    })

def programa_alumno(request):
    # Obtener todos los programas desde la base de datos
    programas = Programa.objects.all()

    # Pasamos los programas al template
    return render(request, 'programas/alumno.html', {
        'programas': programas
    })

def gestionar_programas(request):
    if request.method == 'POST':
        # Capturar los datos del formulario manualmente
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        carrera = request.POST.get('carrera')
        pais = request.POST.get('pais')
        ciudad = request.POST.get('ciudad')

        print(nombre, descripcion, carrera, pais, ciudad)

        # Crear un nuevo programa en la base de datos
        Programa.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            carrera=carrera,
            pais=pais,
            ciudad=ciudad
        )

        # Redirigir después de guardar
        return redirect('gestionar_programas')

    # Obtener todos los programas
    programas = Programa.objects.all()

    # Renderizar la plantilla con los programas
    return render(request, 'programas/admin.html', {
        'programas': programas,
    })

def detalle_programa(request, id):
    # Obtener el programa correspondiente por su ID
    programa = get_object_or_404(Programa, id=id)

    if request.method == 'POST':
        # Obtener los datos del formulario directamente del request.POST
        nombre = request.POST.get('nombre')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')

        # Crear una nueva instancia de Postulacion y asociarla con el programa
        Postulacion.objects.create(
            programa=programa,
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            fecha_nacimiento=fecha_nacimiento,
            correo=correo,
            telefono=telefono
        )
        
        # Redirigir a la página del programa después de postular
        return redirect('programa/alumno')

    return render(request, 'programas/detalle_programa.html', {
        'programa': programa
    })

def listar_postulaciones(request):
    # Verifica si el usuario es parte de Personal-CEM o Administrador
    if not request.user.groups.filter(name__in=['Personal-CEM', 'Administrador']).exists():
        return redirect('index')  # Redirigir si no tiene permisos
    
    # Filtrar por postulaciones en estado 'en_espera' o 'pendiente' (me dio flojera xd)
    postulaciones = Postulacion.objects.filter(Q(estado='en_espera') | Q(estado='pendiente'))

    return render(request, 'admin/postulaciones.html', {
        'postulaciones': postulaciones
    })

@login_required
def gestionar_postulacion(request, id, accion):
    # Obtener la postulación por ID
    postulacion = get_object_or_404(Postulacion, id=id)
    
    # Verificar si el usuario pertenece a los grupos permitidos
    if not request.user.groups.filter(name__in=['Personal-CEM', 'Administrador']).exists():
        return redirect('index')  # Redirigir si no tiene permisos

    # Actualizar el estado de la postulación
    if accion == 'aceptar':
        postulacion.estado = 'aceptada'
        mensaje = "------------------------------------\n¡Felicidades! Tu postulación ha sido aceptada.\n------------------------------------"
    elif accion == 'rechazar':
        postulacion.estado = 'rechazada'
        mensaje = "------------------------------------\nLo sentimos, tu postulación ha sido rechazada.\n-----------------------------------"
    
    postulacion.save()

    # Enviar el correo electrónico de notificación
    send_mail(
        'Resultado de tu postulación',
        mensaje,
        'no_reply@sgi_cem.com',
        [postulacion.correo],
        fail_silently=False,
    )
    
    # Redirigir de vuelta a la lista de postulaciones
    return redirect('listar_postulaciones')

@login_required
def perfil_alumno(request):
    # Busca el objeto Alumno asociado al usuario actual
    try:
        alumno = Alumno.objects.get(user=request.user)
    except Alumno.DoesNotExist:
        # Si no existe, redirige o muestra un mensaje de error
        return redirect('index')  # O puedes mostrar un mensaje de error

    if request.method == 'POST':
        # Manejo de la foto de perfil
        foto_perfil = request.FILES.get('foto_perfil')
        if foto_perfil:
            alumno.foto_perfil = foto_perfil
            alumno.save()

        # Manejo de los documentos (máximo 5)
        documentos_actuales = Documento.objects.filter(alumno=alumno).count()
        if documentos_actuales < 5:
            nuevos_documentos = request.FILES.getlist('documentos')
            for archivo in nuevos_documentos:
                if documentos_actuales < 5:
                    Documento.objects.create(alumno=alumno, archivo=archivo)
                    documentos_actuales += 1

        return redirect('perfil_alumno')

    documentos = Documento.objects.filter(alumno=alumno)
    return render(request, 'perfil/perfil_alumno.html', {
        'alumno': alumno,
        'documentos': documentos
    })

def login(request):
    if request.user.is_authenticated:
        return redirect('index')  # Redirige al index si ya está autenticado
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Has iniciado sesión correctamente.')
            return redirect('index')
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')
    
    return render(request, 'unirse/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']

        # Verificar que las contraseñas coincidan
        if password != password2:
            return render(request, 'unirse/register.html', {'error': 'Las contraseñas no coinciden'})

        # Verificar que no exista un usuario con el mismo nombre de usuario
        if User.objects.filter(username=username).exists():
            return render(request, 'unirse/register.html', {'error': 'El nombre de usuario ya existe'})

        # Crear el nuevo usuario
        user = User.objects.create(
            username=username,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        # Asignar al grupo "Alumno" automáticamente
        grupo_alumno = Group.objects.get(name='Alumno')
        user.groups.add(grupo_alumno)

        # Crear un registro en Alumno asociado a este nuevo usuario
        Alumno.objects.create(user=user, programa_intercambio="", fecha_postulacion=None)

        # Redirigir a la página de inicio con un mensaje de éxito
        messages.success(request, 'Te has registrado exitosamente. Inicia sesión.')
        return redirect('index')

    return render(request, 'unirse/register.html')

@login_required
def protected_view(request):
    return render(request, 'protected_page.html')

@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('index')