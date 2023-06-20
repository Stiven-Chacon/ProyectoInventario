from django.shortcuts import render, redirect
from django.db import Error, transaction
from django.contrib.auth.models import Group
import random
import string
#Enviar Correo 
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading#hilos envio de correo
from smtplib import SMTPException
################################################################
from AppGestionInventario.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from django.conf import settings
import urllib
from AppGestionInventario.models import Devolutivo
from AppGestionInventario.models import *
from django.http import HttpResponse
from django.http import JsonResponse
import json

#---------------------------------------------------------------------------------------------
#BLOQUE DE CODIGO DE REGISTRAR USUARIO
# Create your views here.
def registrarUsuario(request):
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        tipo = request.POST["cbTipo"]
        foto = request.FILES.get("fileFoto",False)
        idRol = int(request.POST["cbRol"])
        with transaction.atomic():
            #crear un objeto de tipo User
            user = User(username=correo, first_name=nombres,
                        last_name=apellidos,email = correo,
                        userTipo=tipo, userFoto=foto)
            user.save()
            #obtener el Rol de acuerdo a id del rol
            rol = Group.objects.get(pk=idRol)
            #agregar el usuario a ese Rol
            user.groups.add(rol)
            #si el rol es Administrador se habilita para que tenga acceso
            #al sitio web del administrador
            if(rol.name=="Administrador"):user.is_staff=(True)
            #guardamos el usuario con lo que tenemos
            user.save()
            #llamamos a la funcion generarPassword
            passwordGenerado = generarPassword()
            print(f"password {passwordGenerado}")
            #con el usuario creado llamamos a la funcion set_password que
            #encripta el password y lo agrega al campo password del user.
            user.set_password(passwordGenerado)
            #se actualiza el user
            user.save()
            mensaje="Usuario Agregado Correctamente"
            retorno = {"mensaje":mensaje}
            #enviar correo al usuario
            asunto='Registro Sistema Inventario CIES-NEIVA'
            mensaje=f'Cordial saludo, <b>{user.first_name} {user.last_name}</b> Nos Permitimos \
                informarle que usted ha sido registrado en el sistema de gestion de inventario \
                del centro de la industria, la empresa y los servicios CIES de la ciudad de Neiva \
                Nos permitimos enviarle las credenciales de ingreso a nuestro sistema. <br>\
                <br><b>Username:</b> {user.username}\
                <br><b>Password:</b> {passwordGenerado}\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                https://sena.territorio.la/index.php?login=true'
            thread = threading.Thread(target=enviarCorreo,
                                args=(asunto, mensaje,user.email))
            thread.start()
         #Modifique el vistaGestionarUsuario por vistaRegistrarUsuario
            return redirect("/vistaRegistrarUsuario/",retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje":mensaje, "user":user}
    return render(request, "administrador/RegistrarUsuario.html", retorno)

def generarPassword():
    longitud = 10
    caracteres = string.ascii_lowercase + string.ascii_uppercase \
                + string.digits + string.punctuation
    password = ''
    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password

def vistaRegistrarUsuario(request):
    roles = Group.objects.all()
    retorno = {"roles":roles, "user":None}
    return render(request, "administrador/RegistrarUsuario.html", retorno)

#Listamos los Usuarios
def ListarUsuarios(request):
    try:
        user = User.objects.all()
        mensaje=""
        print(user)
    except:
        mensaje="Problemas al obtener los Usuarios"
    retorno = {"mensaje":mensaje, "ListaUsuarios":user}
    return render(request, "administrador/ListarUsuarios.html", retorno)

def vistaLogin(request):
     return render(request, "Login.html")

def login(request):
     #validar el recaptcha
     '''Begin reCAPTCHA validation'''
     recaptcha_response = request.POST.get('g-recaptcha-response')
     url = 'https://www.google.com/recaptcha/api/siteverify'
     values = {
         'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
         'response': recaptcha_response
     }
     data = urllib.parse.urlencode(values).encode()
     req = urllib.request.Request(url, data=data)
     response = urllib.request.urlopen(req)
     result = json.loads(response.read().decode())
     print(result)
     ''' End reCAPTCHA validation'''
    
     if result['succes']:
         username = request.POST["txtUsername"]
         password = request.POST["txtPassword"]
         user = authenticate(username=username, passsword=password)
         if user is not None:
             #registrar la variable de sesión
             auth.login(request, user)
             if user.groups.filter(name='Administrador').exist():
                 return redirect('RegistrarUsuario.html')
             elif user.groups.filter(name='Asistente').exist():
                 return redirect('RegistrarUsuario.html')
             else: 
                 return redirect('RegistrarUsuario.html')
         else:
             mensaje = "Usuario o Contraseña Incorrectas"
             return render(request, "Login.html",{"mensaje":mensaje})
     else:
         mensaje="Debe validar primero el recaptcha"
         return render(request, "Login.html",{"mensaje":mensaje})
    
def inicioAdministrador(request):
     if request.user.is_authenticated:
         return render(request, "administrador/inicio.html")
     else:
         retorno={"mensaje":"Debe ingresar con sus credenciales"}
         return render(request, "Login.html",retorno)

def enviarCorreo(asunto=None,mensaje=None,destinatario=None):
     remitente = settings.EMAIL_HOST_USER
     template = get_template('enviarCorreo.html')
     contenido = template.render({
         'destinatario': 'cocoarroz06@gmail.com',
         'mensaje': '{mensaje}',
         'asunto': 'Programador Del Año',
         'remitente': 'cocoarroz06@gmail.com',
     })
     try:
         correo = EmailMultiAlternatives(asunto, mensaje, remitente, [destinatario])
         correo.attach_alternative(contenido, 'text/html')
         correo.send(fail_silently=True)
     except SMTPException as error:
      print(error)
#---------------------------------------------------------------------------------------------
#BLOQUE DE CODIGO DE GESTIONAR ELEMENTOS DEVOLUTIVOS
#Listamos los Elementos
def vistaGestionarDevolutivos(request):
    if request.user.is_authenticated:
        elementosDevolutivos = Devolutivo.objects.all()
        retorno = {"listaElementosDevolutivos":elementosDevolutivos}
        print(elementosDevolutivos)
        return render(request, "administrador/ListarElementosDevolutivos.html",retorno)
    else:
        mensaje = f"Debe iniciar sesión"
        return render(request, "login.html",{"mensaje":mensaje})
    
def vistaRegistrarDevolutivo(request):
    retorno = {"tipoElementos":tipoElemento,"estados":estadosElementos}
    print(retorno)
    return render(request, "administrador/RegistrarElementoDevolutivo.html", retorno)
                  
    
def registrarDevolutivo(request):
    estado=False
    try:
        tipoElemento = request.POST["cbTipoElemento"]
        fechaInventarioSena = request.POST["txtFechaSena"]
        placaSena = request.POST["txtPlacaSena"]
        serial = request.POST.get("txtSerial",False)
        marca = request.POST.get("txtMarca",False)
        valorUnitario = int(request.POST["txtValorUnitario"])
        estado = request.POST["cbEstado"]
        nombre = request.POST["txtNombre"]
        descripcion = request.POST["txtDescripcion"]
        deposito = request.POST["cbDeposito"]
        estante = request.POST.get("txtEstante",False)
        entrepano = request.POST.get("txtEntrepano",False)
        locker = request.POST.get("txtLocker",False)
        archivo = request.FILES.get("fileFoto",False)

        #iniciamos una transacción, (hasta que todos estan bien se puede enviar a la base de datos
        # en lo contrario no se envia a la base de datos)
        with transaction.atomic():
        #Obtener Cuantos Elementos Se Han Registrado
            cantidad = Elemento.objects.all().count()
            # Crear Un Codigo a Partir de la cantidad, ajustando 0 al inicio
            codigoElemento = tipoElemento.upper() + str(cantidad+1).rjust(6, '0')
            # Crear Un Elemento
            elemento = Elemento(eleCodigo=codigoElemento, eleNombre= nombre,
                                eleTipo = tipoElemento,eleEstado = estado)
            # Salvar el elemento en la base de datos
            elemento.save()
            #Crear objeto ubicacion fisica del elemento
            ubicacion = UbicacionFisica(ubiDeposito = deposito, ubiEstante = estante,
                                        ubiEntrepano =entrepano, ubiLocker = locker,
                                        ubiElemento = elemento)
            #Registrada la ubicacion fisica del elemento
            ubicacion.save()
            #crear el devolutivo 
            elementoDevolutivo =Devolutivo(devPlacaSena = placaSena,devSerial = serial,
                                        devDescripcion = descripcion, devMarca = marca,
                                        devFechaIngresoSENA = fechaInventarioSena,
                                        devValor = valorUnitario, devFoto = archivo,
                                        devElemento = elemento)
            #Registrar el elemento a la base de datos
            elementoDevolutivo.save()
            estado=True
            mensaje = f"Elemento Devolutivo Registrado Satisfactoriamente con el codigo {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje = f"Error"
    retorno = {"mensaje":mensaje, "devolutivo":elementoDevolutivo, "estado":estado}
    return render(request,"administrador/RegistrarElementoDevolutivo.html",retorno)

#---------------------------------------------------------------------------------------------
#BLOQUE DE CODIGO DE ENTRADA MATERIAL DE CONSUMO
def vistaRegistrarMaterial(request):
    unidadesMedidad = UnidadMedida.objects.all()
    retorno = {"unidadesMedida":unidadesMedidad,"estados":estadosElementos}
    return render(request,"administrador/RegistrarMaterialConsumo.html", retorno)

def registrarMaterial(request):
    estado = False
    mensaje = ""
    try:
        nombre = request.POST["txtNombre"]
        # unidadMedida = int(request.POST["cbUnidadMedida"])
        marca = request.POST.get("txtMarca",None)
        descripcion = request.POST.get("txtDescripcion",None)
        estado = request.POST["cbEstado"]
        deposito = request.POST["cbDeposito"]
        estante = request.POST.get("txtEstante",False)
        entrepano = request.POST.get("txtEntrepano",False)
        locker = request.POST.get("txtLocker",False)
        with transaction.atomic():
            # unidadM = UnidadMedida.objects.get(pk=unidadMedida)
            cantidad = Elemento.objects.all().filter(eleTipo='MAT').count()
            codigoElemento = "MAT" + str(cantidad+1).rjust(6, '0')
            #crear elemento
            elemento = Elemento(eleCodigo = codigoElemento, eleNombre = nombre,
                                eleTipo = "MAT", eleEstado = estado)
            #slavar elemento en la base de datos
            elemento.save()
            #crear el maerial
            materiales = Material(matReferencia = descripcion, matMarca = marca, matElemento = elemento)
            materiales.save()
            #crear objeto ubicación física del elemento
            ubicacion = UbicacionFisica(ubiDeposito = deposito, ubiEstante = estante,
                                        ubiEntrepano = entrepano, ubiLocker = locker, ubiElemento = elemento)
            #registrar en la base de datos la ubicación física del elemento
            ubicacion.save()
            estado = True
            mensaje = f"Material registrado satisfactoriamente con el código: {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje = f"Error {error}"
    retorno = {"mensaje":mensaje,"material":materiales,"estado":estado}
    return render(request, "administrador/RegistrarMaterialConsumo.html", retorno)

#---------------------------------------------------------------------------------------------
#BLOQUE DE CODIGO DE ENTRADA MATERIAL 
def vistaEntradaMaterial(request):
    proveedores = Proveedor.objects.all()
    usuarios = User.objects.all()
    materiales = Material.objects.all()
    unidadesMedida = UnidadMedida.objects.all()
    
    retorno = {"proveedores":proveedores, "usuarios":usuarios,
               "materiales":materiales, "unidadesMedida": unidadesMedida}
    return render(request,"administrador/RegistrarEntradaDeMateriales.html", retorno)


def registrarEntradaMaterial(request):
    if request.method == "POST":
        estado = False
        try:
            with transaction.atomic():
                
                codigoFactura = request.POST.get('codigoFactura')
                entregadoPor = request.POST.get('entregadoPor')
                idProveedor = int(request.POST.get('proveedor'))
                recibidoPor = int(request.POST.get('recibidoPor'))
                fechaHora = request.POST.get('fechaHora',None)
                observaciones = request.POST.get('observaciones')
                userRecibe = User.objects.get(pk=recibidoPor)
                proveedor = Proveedor.objects.get(pk=idProveedor)
                entradaMaterial = EntradaMaterial(entNumeroFactura = codigoFactura, entFechaHora = fechaHora,
                                                  entUsuarioRecibe= userRecibe, entEntregadoPor = entregadoPor,
                                                  entProveedor = proveedor, entObservaciones=observaciones)
                entradaMaterial.save()
                detalleMateriales = json.loads(request.POST.get('detalle'))
                for detalle in detalleMateriales:
                    material = Material.objects.get(pk=int(detalle['idMaterial'])) 
                    cantidad = int(detalle['cantidad'])
                    precio = int(detalle['precio'])
                    estado = detalle['estado']
                    unidadMedida = UnidadMedida.objects.get(pk=int(detalle['idUnidadMedida']))
                    detalleEntradaMaterial = DetalleEntradaMaterial(detEntradaMaterial = entradaMaterial,
                    detMaterial = material, detUnidadMedida = unidadMedida,
                    detCantidad=cantidad, detPrecioUnitario = precio, devEstado=estado)
                    detalleEntradaMaterial.save()
                estado = True
                mensaje = "Se ha registrado la entrada de Materiales correctamente" 
        except Error as error:
            transaction.rollback()
            mensaje = f"{error}"
        retorno={"estado":estado, "mensaje":mensaje}
        return JsonResponse(retorno)
        