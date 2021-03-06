# -*- encoding: utf-8 -*-
# from django.db import connection
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.utils import timezone
from django.views.decorators.cache import cache_control
from usuarios.models import *
import random
import sendgrid
from sendgrid.helpers.mail import *
from colaboradores_360.models import Colaboradores_360
from redes_360.models import Redes_360
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
import smtplib,os
#===============================================================================
# Front end
#===============================================================================

@cache_control(no_store=True)
def index(request):

    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    captcha = ''.join(random.sample(chars, 5))

    if not request.user.is_anonymous():
        return HttpResponseRedirect('/home/')

    if request.method == 'POST':
        try:
            if( request.POST['variable'] == request.POST['captcha']):
                # server=smtplib.SMTP('smtp.mandrillapp.com',587)
                # server=smtplib.SMTP('email-smtp.us-east-1.amazonaws.com',587)
                # server.ehlo()
                # server.starttls()
                # # server.login('Team@goanalytics.com','pR6yG1ztNHT7xW6Y8yigfw')
                # server.login('AKIAIIG3SGXTWBK23VEQ','AtDj4P2QhDWTSIpkVv9ySRsz50KUFnusZ1cjFt+ZsdHC')
                sg = sendgrid.SendGridAPIClient(apikey='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')

                destinatario = ['ilgaleanos@gmail.com','ricardo.montoya@networkslab.co']
                msg=MIMEMultipart()
                msg["subject"]=  'Persona interesada GoAnalytics xD.'
                msg['To'] = email.utils.formataddr(('Respetado', destinatario))
                # msg['From'] = email.utils.formataddr(('GoAnalytics', 'Team@goanalytics.com'))
                msg['From'] = email.utils.formataddr(('GoAnalytics', 'team@bigtalenter.com'))
                n = (request.POST['nombre']).encode("ascii", "xmlcharrefreplace")
                e = (request.POST['email']).encode("ascii", "xmlcharrefreplace")
                t = (request.POST['telefono']).encode("ascii", "xmlcharrefreplace")
                m = (request.POST['mensaje']).encode("ascii", "xmlcharrefreplace")
                html = '<b>NOMBRE:</b> '+ n +'<br>'
                html = html+'  <b>EMAIL:</b> '+str(e)+'<br>'
                html = html+'  <b>TELEFONO: </b>'+str(t)+'<br>'
                html = html+'  <b>MENSAJE: </b><br> '+ m

                parte2=MIMEText(html,"html")
                msg.attach(parte2)

                # server.sendmail('Team@goanalytics.com',destinatario,msg.as_string())
                # server.sendmail('team@bigtalenter.com',destinatario,msg.as_string())
                # server.quit()
                content = Content("text/html", html)
                print '####################################################################'
                mail = Mail(Email('team@bigtalenter.com'), msg["subject"], Email(destinatario), content)
                mail.set_template_id('09dd518c-04a1-45e1-8fea-b635274a02e2')
                response = sg.client.mail.send.post(request_body=mail.get())
                print response
                return HttpResponseRedirect('/index/')
        except:
            return HttpResponseRedirect('/index/#contact/')

    return render_to_response('index.html',{
    'captcha':captcha
    }, context_instance=RequestContext(request))

#===============================================================================
# login - logout
#===============================================================================

# @cache_control(no_store=True)
# def index(request):
#     """Home page JsConf"""
#     data = {}
#     desafios = Desafio.objects.all().order_by('id')
#     # # speakers = Speaker.objects.all().order_by('order')
#     # # countries = Set([])
#     # # for speaker in speakers:
#     # #     if speaker.country:
#     # #         countries.add(speaker.country.country)
    
#     # # data['sponsors_scholarship'] = sponsors_scholarship
#     # data['sponsors_hardware'] = sponsors_hardware
#     data['desafios'] = desafios
#     return render(request, 'index_2.html', data)


@cache_control(no_store=True)
def acceder(request):
    if not request.user.is_anonymous():
        return HttpResponseRedirect('/home/')
    error = None
    if request.method == 'POST':
        acceso = False
        try:
            acceso = authenticate(
            username = User.objects.only('username').get(email = request.POST['email']),
            password = request.POST['clave'])
            if acceso is None:
                error = 'Los datos proporcionados son incorrectos.'
            else:
                if acceso.is_active:
                    login(request,acceso)
                    return HttpResponseRedirect('/home/')
                else:
                    error = 'Su usuario se encuentra desactivado'
        except:
            error = 'Los datos proporcionados son incorrectos.'
    return render_to_response('login.html',{
    'Error':error,
    }, context_instance=RequestContext(request))


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def home(request):
    permisos = request.user.permisos
    cache.delete(request.user)
    if request.user.is_superuser:
        proyectos = Proyectos.objects.only('nombre','empresa__nombre','interna',
                                            'tot_respuestas','tot_aresponder',
                                            'total','activo').all().select_related('empresa__nombre')
    else:
        if permisos.pro_see or permisos.res_see:
            proyectos = Proyectos.objects.only('nombre','empresa__nombre','interna',
                                                'tot_respuestas','tot_aresponder',
                                                'total','activo').select_related('empresa__nombre').filter( usuarios = request.user)
        else:
            proyectos = []
    return render_to_response('home.html',{
    'Activar':'MisProyectos','Proyectos':proyectos,'Permisos':permisos
    }, context_instance=RequestContext(request))


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def menu(request,id_proyecto):
    try:
        permisos = request.user.permisos
        if request.user.is_superuser:
            proyecto = Proyectos.objects.select_related('empresa__nombre'
                        ).get(id=int(id_proyecto))
        elif permisos.pro_see or permisos.res_see:
            proyecto = Proyectos.objects.filter(
            usuarios = request.user).select_related('empresa__nombre'
            ).get(id=int(id_proyecto))
        else:
            return render_to_response('403.html')
        cache.set(request.user.username,proyecto,86400)
        if( permisos.consultor and proyecto.tipo != "360 unico" and proyecto.tipo != "360 redes" ):
            return HttpResponseRedirect('/respuestas/metricas')
        elif( permisos.consultor and ( proyecto.tipo == "360 unico" or proyecto.tipo == "360 redes" ) ):
            return HttpResponseRedirect('/360/respuestas/metricas')
        elif( proyecto.tipo == "Lineal 360" or proyecto.tipo == "Redes 360" ):
            return HttpResponseRedirect('/360/focalizado/')
        else:
            return HttpResponseRedirect('/analisis/focalizado/')

    except:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def home2(request):
  permisos = request.user.permisos
  if permisos.consultor or permisos.pro_see:
    proyecto = cache.get(request.user.username)
    if(proyecto):
      return render_to_response('home2.html',{
      'Activar':'Configuracion','Permisos':permisos,'Proyecto':proyecto
      }, context_instance=RequestContext(request))
    else:
      return render_to_response('423.html')
  else:
    return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def salir(request):
    cache.delete(request.user)
    logout(request)
    return HttpResponseRedirect('/acceder/')


#===============================================================================
#    Páginas de recuperar usuario
#===============================================================================


@cache_control(no_store=True)
def recuperar(request):
    aviso = None
    if request.method == 'POST':
        ema = request.POST['email']
        try:
            usuario = User.objects.get(email = ema)
            envio,_ = Recuperar.objects.get_or_create(usuario=usuario)
            hora_local = timezone.now()
            hora_envio = envio.fregistro
            delta = hora_local - hora_envio

            if(delta.days >= 1 or (delta.seconds>=3600 or 2 >= delta.seconds)):
                from strings import recuperar_cuenta
                from mensajeria.corrector import salvar_html
                # server=smtplib.SMTP('smtp.mandrillapp.com',587)
                server=smtplib.SMTP('email-smtp.us-east-1.amazonaws.com',587)
                server.ehlo()
                server.starttls()
                # server.login('Team@goanalytics.com','pR6yG1ztNHT7xW6Y8yigfw')
                server.login('AKIAIIG3SGXTWBK23VEQ','AtDj4P2QhDWTSIpkVv9ySRsz50KUFnusZ1cjFt+ZsdHC')
                chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                key = ''.join(random.sample(chars, 96))
                Recuperar.objects.filter(usuario=usuario).delete()
                Recuperar.objects.create(usuario=usuario,link=key)
                nom_log = usuario.first_name+' '+usuario.last_name
                Logs.objects.create(usuario=nom_log,usuario_username=usuario.username,accion="Olvido de contraseña",descripcion=usuario.first_name+" "+usuario.last_name)
                destinatario = [usuario.email]
                msg=MIMEMultipart()
                nombre = (usuario.first_name).encode("ascii", "xmlcharrefreplace")
                msg["subject"]=  'Cambio de clave.'
                # msg['From'] = email.utils.formataddr(('GoAnalytics', 'Team@goanalytics.com'))
                msg['From'] = email.utils.formataddr(('GoAnalytics', 'team@bigtalenter.com'))
                url = 'http://159.203.190.248/recuperar/'+key
                html = recuperar_cuenta(nombre,url)
                mensaje = MIMEText(html,"html")
                msg.attach(mensaje)
                # server.sendmail('Team@goanalytics.com',destinatario,msg.as_string())
                server.sendmail('team@bigtalenter.com',destinatario,msg.as_string())
                server.quit()
                return HttpResponseRedirect('/acceder/')
            else:
                aviso = 'Ya se ha enviado el correo, verifique su correo.'

        except:
            aviso = 'Error en el requerimiento'

    return render_to_response('recuperar.html',{
    'Aviso':aviso
    }, context_instance=RequestContext(request))


@cache_control(no_store=True)
def usuariorecuperar(request,key):
    try:
        error = ''
        registro = Recuperar.objects.select_related('usuario').get(link=key)
        usuario = registro.usuario
        if not registro.usuario.is_active:
            return HttpResponseRedirect('/acceder/')
        else:
            if request.method == 'POST':
                if(request.POST['password'] == request.POST['password2']):
                    usuario.set_password(request.POST['password'])
                    with transaction.atomic():
                        usuario.save()
                        Recuperar.objects.filter(usuario=usuario).delete()
                    return HttpResponseRedirect('/acceder/')
                else:
                    error = 'Ocurrió un error al procesar la solicitud, las contraseñas no coinciden.'
        return render_to_response('usuariorecuperar.html',{
        'Error':error
        }, context_instance=RequestContext(request))
    except:
        return render_to_response('404.html')


#===============================================================================
#   Empresas
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def empresas(request):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor:
        empresas = Empresas.objects.filter(usuario=request.user)
        return render_to_response('empresas.html',{
        'Activar':'Configuracion','activar':'Empresas','Empresas':empresas,
        'Permisos':permisos,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def empresaeditar(request,id_empresa):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor:
        try:
            empresas = Empresas.objects.filter(usuario=request.user).exclude(id=int(id_empresa))
            empresa = Empresas.objects.filter(usuario=request.user).get(id=int(id_empresa))
        except:return render_to_response('404.html')
        if request.method == 'POST':
            empresa.nombre = request.POST['nombre']
            empresa.nit  = request.POST['nit']
            empresa.pagina = request.POST['pagina']
            empresa.num_empleados  = int(request.POST['num_empleados'])
            empresa.sector  = request.POST['sector']
            empresa.pais  = request.POST['pais']
            empresa.departamento  = request.POST['departamento']
            with transaction.atomic():
                empresa.save()
                nom_log =request.user.first_name+' '+request.user.last_name
                Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Editó la empresa",descripcion=empresa.nombre)
            return HttpResponseRedirect('/empresas/')
        return render_to_response('empresaeditar.html',{
        'Activar':'Configuracion','activar':'Empresas','Empresa':empresa,
        'Empresas':empresas,'Permisos':permisos,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def empresaeliminar(request,id_empresa):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor:
        try:
            empresa = Empresas.objects.filter(usuario=request.user
            ).prefetch_related('proyectos_set').get(id=int(id_empresa))
        except:return render_to_response('403.html')
        if request.method == 'POST':
            empresa.usuario_id =  1
            with transaction.atomic():
                empresa.save()
                for i in empresa.proyectos_set.all():
                    i.usuarios.clear()
                nom_log =request.user.first_name+' '+request.user.last_name
                Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Eliminó la empresa",descripcion=empresa.nombre)
            return HttpResponseRedirect('/empresas/')
        return render_to_response('eliminar.html',{
        'Activar':'Configuracion','activar':'Empresas','Empresa':empresa,
        'objeto':'Empresa','Permisos':permisos,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def empresanueva(request):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor:
        empresas = Empresas.objects.only('nombre','nit').filter(usuario=request.user)
        if request.method == 'POST':
            with transaction.atomic():
                Empresas.objects.create(
                    nombre = request.POST['nombre'],
                    nit  = request.POST['nit'],
                    pagina = request.POST['pagina'],
                    num_empleados  = int(request.POST['num_empleados']),
                    sector  = request.POST['sector'],
                    pais  = request.POST['pais'],
                    departamento  = request.POST['departamento'],
                    usuario = request.user)
                nom_log =request.user.first_name+' '+request.user.last_name
                Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Creó la empresa",descripcion=request.POST['nombre'])
            return HttpResponseRedirect('/empresas/')
        return render_to_response('empresanueva.html',{
        'Activar':'Configuracion','activar':'Empresas','Empresas':empresas,
        'Permisos':permisos,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')

#===============================================================================
#   Proyecto
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def proyectonuevo(request):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor and permisos.pro_add:
        empresas = Empresas.objects.only('nombre').filter(usuario=request.user)
        proyectos = Proyectos.objects.only('nombre').filter(usuarios=request.user)
        usuarios = IndiceUsuarios.objects.get(usuario=request.user
                    ).get_descendants(include_self=False).select_related(
                    'usuario__first_name','usuario__last_name','parent')
        if request.method == 'POST':
            chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            key = ''.join(random.sample(chars, 64))
            key2 = ''.join(random.sample(chars, 64))
            with transaction.atomic():
                proyecto = Proyectos(
                            empresa_id = request.POST['empresa'],
                            nombre = request.POST['nombre'],
                            tipo = request.POST['tipo'],
                            key=key)
                try:
                    if(request.POST['pordenadas']):proyecto.pordenadas = True
                except:
                    proyecto.pordenadas = False

                try:
                    if(request.POST['circular']):proyecto.circular = True
                except:
                    proyecto.circular= False

                if int(request.POST['interna']):
                    proyecto.interna = True
                proyecto.save()

                if proyecto.tipo == "360 unico":
                    colaborador = Colaboradores_360.objects.create(
                    apellido = "Empresa",
                    email = "ninguno@que.registrar",
                    estado = False,
                    key = key2,
                    nombre = "Empresa",
                    proyecto_id = proyecto.id)

                    Redes_360.objects.create(
                        colaborador_id = colaborador.id,
                        evaluado_id = colaborador.id,
                        proyecto_id = proyecto.id)

                proyecto.usuarios.add(request.user)
                for i in request.POST.getlist('usuarios'):
                    proyecto.usuarios.add(i)
                datos =ProyectosDatos(
                        id = proyecto,
                        tit_encuesta = request.POST['tit_encuesta'],
                        int_encuesta = request.POST['int_encuesta'],
                        cue_correo = request.POST['cue_correo'],
                        logo = request.FILES['logo'],
                        )
                try:datos.asunto = request.POST['asunto']
                except:pass
                try:datos.logoenc = request.FILES['logoenc']
                except:pass
                try:datos.opcional1 = request.POST['opcional1']
                except:pass
                try:datos.opcional2 = request.POST['opcional2']
                except:pass
                try:datos.opcional3 = request.POST['opcional3']
                except:pass
                try:datos.opcional4 = request.POST['opcional4']
                except:pass
                try:datos.opcional5 = request.POST['opcional5']
                except:pass
                try:
                    if(request.POST['censo']):datos.censo = False
                except:
                    datos.censo = True
                datos.save()
                nom_log =request.user.first_name+' '+request.user.last_name
                Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Creó el proyecto",descripcion=proyecto.nombre)
            cache.set(request.user.username,proyecto,86400)

            if( proyecto.tipo == "360 unico" or proyecto.tipo == "360 redes" ):
                return HttpResponseRedirect('/360/instrumento/nuevo')
            else:
                return HttpResponseRedirect('/variable/nueva/')

        return render_to_response('proyectonuevo.html',{
        'Activar':'MisProyectos','Empresas':empresas,'Proyectos':proyectos,
        'Usuarios':usuarios,'Permisos':permisos,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def proyectoeditar(request,id_proyecto):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor and permisos.pro_edit:
        try:
            proyecto = Proyectos.objects.filter(usuarios=request.user
                        ).prefetch_related('usuarios'
                        ).select_related('proyectosdatos'
                        ).get(id=int(id_proyecto))
        except:
            if request.user.is_staff:
                proyecto = Proyectos.objects.select_related('empresa__nombre').get(id=int(id_proyecto))
            else:
                return render_to_response('403.html')
        empresas = Empresas.objects.only('nombre').filter(usuario=request.user)
        proyectos = Proyectos.objects.only('nombre').filter(usuarios=request.user)
        usuarios = IndiceUsuarios.objects.get(usuario=request.user
                    ).get_descendants(include_self=False).select_related(
                    'usuario__first_name','usuario__last_name','parent')
        if request.method == 'POST':
            with transaction.atomic():
                proyecto.empresa_id = request.POST['empresa']
                proyecto.nombre = request.POST['nombre']
                try:
                    if(request.POST['pordenadas']):proyecto.pordenadas = True
                except:
                    proyecto.pordenadas = False
                proyecto.save()
                proyecto.usuarios.clear()
                usuarios_add = [i for i in request.POST.getlist('usuarios')]
                usuarios.add = usuarios_add.append(str(request.user.id))
                proyecto.usuarios.add(*usuarios_add)
                datos = proyecto.proyectosdatos
                datos.tit_encuesta = request.POST['tit_encuesta']
                datos.int_encuesta = request.POST['int_encuesta']
                datos.cue_correo = request.POST['cue_correo']
                try:
                    if request.FILES['logo']:
                        try:
                            command = "rm "+os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+proyecto.proyectosdatos.logo.url
                            os.system(command)
                        except:
                            pass
                    datos.logo = request.FILES['logo']
                except:
                    pass
                try:
                    if request.FILES['logoenc']:
                        try:
                            command = "rm "+os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+proyecto.proyectosdatos.logoenc.url
                            os.system(command)
                        except:
                            pass
                    datos.logoenc = request.FILES['logoenc']
                except:
                    pass
                try:datos.asunto = request.POST['asunto']
                except:pass
                try:datos.opcional1 = request.POST['opcional1']
                except:pass
                try:datos.opcional2 = request.POST['opcional2']
                except:pass
                try:datos.opcional3 = request.POST['opcional3']
                except:pass
                try:datos.opcional4 = request.POST['opcional4']
                except:pass
                try:datos.opcional5 = request.POST['opcional5']
                except:pass
                try:
                    if(request.POST['censo']):datos.censo = False
                except:
                    datos.censo = True
                datos.save()
                nom_log =request.user.first_name+' '+request.user.last_name
                Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Editó el proyecto",descripcion=proyecto.nombre)
            return HttpResponseRedirect('/home/')
        return render_to_response('proyectoeditar.html',{
        'Activar':'MisProyectos','Empresas':empresas,'Proyectos':proyectos,
        'Usuarios':usuarios,'Permisos':permisos,'Proyecto':proyecto
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def proyectoeliminar(request,id_proyecto):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor and permisos.pro_del:
        try:
            proyecto = Proyectos.objects.filter(usuarios=request.user
                ).select_related('empresa__nombre').get(id=int(id_proyecto))
        except:
            if request.user.is_staff:
                proyecto = Proyectos.objects.select_related('empresa__nombre').get(id=int(id_proyecto))
            else:
                return render_to_response('403.html')
        if request.method == 'POST':
            proyecto.zdel = timezone.now()
            with transaction.atomic():
                proyecto.usuarios.clear()
                proyecto.save()
                nom_log =request.user.first_name+' '+request.user.last_name
                Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Eliminó el proyecto",descripcion=proyecto.nombre)
            try:
                command = "rm "+os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+proyecto.proyectosdatos.logo.url
                os.system(command)
            except:pass
            try:
                command = "rm "+os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+proyecto.proyectosdatos.logoenc.url
                os.system(command)
            except:pass
            return HttpResponseRedirect('/home/')
        return render_to_response('eliminar.html',{
        'Activar':'MisProyectos','objeto':'Proyecto','Permisos':permisos,
        'Proyecto':proyecto
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')



#===============================================================================
#   Usuarios
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def usuarios(request):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor and permisos.cre_usuarios:
        usuarios = IndiceUsuarios.objects.select_related('usuario','parent'
                    ).get(usuario=request.user).get_descendants(include_self=False
                    ).prefetch_related('usuario__empresas_set')
        return render_to_response('usuarios.html',{
        'Activar':'Configuracion','activar':'Usuarios','Usuarios':usuarios,
        'Permisos':permisos,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def usuarioeditar(request,id_usuario):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor and permisos.cre_usuarios:
        try:
            usuarios = IndiceUsuarios.objects.select_related('usuario','parent'
                    ).get(usuario=request.user).get_descendants(include_self=False)
            usuario = User.objects.select_related('permisos').get(id=int(id_usuario))
            if usuario.indiceusuarios in usuarios:
                if request.method == 'POST':
                    if  User.objects.filter(email=request.POST['email'].lower()).exists():
                        return render_to_response('usuarioeditar.html',{
                        'Activar':'Configuracion','activar':'Usuarios','Permisos':permisos,'Usuario':usuario,
                        'Error':'Ocurrió un error al procesar la solicitud, este correo ya existe'
                        }, context_instance=RequestContext(request))
                    usuario.first_name = request.POST['nombre']
                    usuario.last_name = request.POST['apellido']
                    usuario.email = request.POST['email'].lower()
                    usuario.username = request.POST['email'].lower()
                    with transaction.atomic():
                        try:
                            if(request.POST['activo']):usuario.is_active = True
                        except:
                            usuario.is_active = False
                        usuario.save()
                        usu_perm = usuario.permisos

                        try:
                            if(request.POST['consultor']):usu_perm.consultor=True
                        except:
                            usu_perm.consultor = False
                        if permisos.cre_usuarios:
                            try:
                                if(request.POST['cre_usuarios']):usu_perm.cre_usuarios = True
                            except:
                                usu_perm.cre_usuarios = False
                        if permisos.act_variables:
                            try:
                                if(request.POST['act_variables']):usu_perm.act_variables = True
                            except:
                                usu_perm.act_variables = False
                        if permisos.det_see:
                            try:
                                if(request.POST['det_see']):usu_perm.det_see = True
                            except:
                                usu_perm.det_see = False
                        if permisos.res_exp:
                            try:
                                if(request.POST['res_exp']):usu_perm.res_exp = True
                            except:
                                usu_perm.res_exp = False
                        if permisos.res_see:
                            try:
                                if(request.POST['res_see']):usu_perm.res_see = True
                            except:
                                usu_perm.res_see = False
                        if permisos.pro_see:
                            try:
                                if(request.POST['pro_see']):usu_perm.pro_see = True
                            except:
                                usu_perm.pro_see = False
                        if permisos.pro_add:
                            try:
                                if(request.POST['pro_add']):usu_perm.pro_add = True
                            except:
                                usu_perm.pro_add = False
                        if permisos.pro_edit:
                            try:
                                if(request.POST['pro_edit']):usu_perm.pro_edit = True
                            except:
                                usu_perm.pro_edit = False
                        if permisos.pro_del:
                            try:
                                if(request.POST['pro_del']):usu_perm.pro_del = True
                            except:
                                usu_perm.pro_del = False
                        if permisos.col_see:
                            try:
                                if(request.POST['col_see']):usu_perm.col_see = True
                            except:
                                usu_perm.col_see = False
                        if permisos.col_add:
                            try:
                                if(request.POST['col_add']):usu_perm.col_add = True
                            except:
                                usu_perm.col_add = False
                        if permisos.col_edit:
                            try:
                                if(request.POST['col_edit']):usu_perm.col_edit = True
                            except:
                                usu_perm.col_edit = False
                        if permisos.col_del:
                            try:
                                if(request.POST['col_del']):usu_perm.col_del = True
                            except:
                                usu_perm.col_del = False
                        if permisos.var_see:
                            try:
                                if(request.POST['var_see']):usu_perm.var_see = True
                            except:
                                usu_perm.var_see = False
                        if permisos.var_add:
                            try:
                                if(request.POST['var_add']):usu_perm.var_add = True
                            except:
                                usu_perm.var_add = False
                        if permisos.var_edit:
                            try:
                                if(request.POST['var_edit']):usu_perm.var_edit = True
                            except:
                                usu_perm.var_edit = False
                        if permisos.var_del:
                            try:
                                if(request.POST['var_del']):usu_perm.var_del = True
                            except:
                                usu_perm.var_del = False
                        if permisos.red_see:
                            try:
                                if(request.POST['red_see']):usu_perm.red_see = True
                            except:
                                usu_perm.red_see = False
                        if permisos.red_add:
                            try:
                                if(request.POST['red_add']):usu_perm.red_add = True
                            except:
                                usu_perm.red_add = False
                        if permisos.red_edit:
                            try:
                                if(request.POST['red_edit']):usu_perm.red_edit = True
                            except:
                                usu_perm.red_edit = False
                        if permisos.red_del:
                            try:
                                if(request.POST['red_del']):usu_perm.red_del = True
                            except:
                                usu_perm.red_del = False
                        usu_perm.save()
                        nom_log =request.user.first_name+' '+request.user.last_name
                        Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Editó al usuario",descripcion=usuario.first_name+" "+usuario.last_name)
                    return HttpResponseRedirect('/usuarios/')
                return render_to_response('usuarioeditar.html',{
                'Activar':'Configuracion','activar':'Usuarios','Permisos':permisos,
                'Usuario':usuario
                }, context_instance=RequestContext(request))
            else:
                return render_to_response('/usuarios/')
        except:
            return render_to_response('404.html')
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def usuarioeliminar(request,id_usuario):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor and request.user.is_staff:
        try:
            usuarios = IndiceUsuarios.objects.select_related('usuario','parent'
                    ).get(usuario=request.user).get_descendants(include_self=False)
            usuario = User.objects.get(id=int(id_usuario))
            if usuario.indiceusuarios in usuarios:
                if request.method == 'POST':
                    usuarios = IndiceUsuarios.objects.select_related('usuario','parent'
                            ).get(usuario=int(id_usuario)).get_descendants(include_self=True)
                    with transaction.atomic():
                        for  i in usuarios:
                            try:i.usuario.delete()
                            except:pass
                        nom_log =request.user.first_name+' '+request.user.last_name
                        Logs.objects.create(usuario=nom_log,
                                            usuario_username=request.user.username,
                                            accion="Eliminó al usuario",
                                            descripcion=usuario.first_name+" "+usuario.last_name)
                    return HttpResponseRedirect('/usuarios/')
                return render_to_response('eliminar.html',{
                'Activar':'Configuracion','activar':'Usuarios','Usuario':usuario,
                'objeto':'Usuario','Permisos':permisos,
                }, context_instance=RequestContext(request))
            else:
                return render_to_response('403.html')
        except:
            return render_to_response('403.html')
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def usuarioreenviar(request,id_usuario):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor and permisos.cre_usuarios:
        usuarios = IndiceUsuarios.objects.select_related('usuario','parent'
                ).get(usuario=request.user).get_descendants(include_self=False)
        try:
            usuario = User.objects.get(id=int(id_usuario))
            if usuario.indiceusuarios in usuarios and not usuario.is_active:
                alerta = None
                if request.method == 'POST':
                    from strings import crear_cuenta
                    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                    key = ''.join(random.sample(chars, 96))
                    # server=smtplib.SMTP('smtp.mandrillapp.com',587)
                    server=smtplib.SMTP('email-smtp.us-east-1.amazonaws.com',587)
                    server.ehlo()
                    server.starttls()
                    # server.login('Team@goanalytics.com','pR6yG1ztNHT7xW6Y8yigfw')
                    server.login('AKIAIIG3SGXTWBK23VEQ','AtDj4P2QhDWTSIpkVv9ySRsz50KUFnusZ1cjFt+ZsdHC')
                    Recuperar.objects.filter(usuario=usuario).delete()
                    Recuperar.objects.create(usuario=usuario,link=key)
                    nom_log =request.user.first_name+' '+request.user.last_name
                    Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Reenvió activación a",descripcion=usuario.first_name+" "+usuario.last_name)
                    destinatario = [usuario.email]
                    msg=MIMEMultipart()
                    msg["subject"]=  'Registro de cuenta.'
                    # msg['From'] = email.utils.formataddr(('GoAnalytics', 'Team@goanalytics.com'))
                    msg['From'] = email.utils.formataddr(('GoAnalytics', 'team@bigtalenter.com'))
                    url = 'http://159.203.190.248/activar/'+key
                    nombre = (usuario.first_name).encode("ascii", "xmlcharrefreplace")
                    html = crear_cuenta(nombre,url)
                    mensaje = MIMEText(html,"html")
                    msg.attach(mensaje)
                    # server.sendmail('Team@goanalytics.com',destinatario,msg.as_string())
                    server.sendmail('team@bigtalenter.com',destinatario,msg.as_string())
                    server.quit()
                    alerta = 'Correo enviado exitosamente.'
                return render_to_response('usuarioreenviar.html',{
                'Activar':'Configuracion','activar':'Usuarios','Usuario':usuario,
                'Permisos':permisos,'Alerta':alerta
                }, context_instance=RequestContext(request))
            else:
                return render_to_response('403.html')
        except:
            return render_to_response('404.html')
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
def usuarioactivar(request,key):
    try:
        error = ''
        cache.delete(request.user)
        registro = Recuperar.objects.select_related('usuario').get(link=key)
        usuario = registro.usuario
        if registro.usuario.is_active:
            return HttpResponseRedirect('/home/')
        else:
            if request.method == 'POST':
                if(request.POST['password'] == request.POST['password2']):
                    usuario.first_name = request.POST['nombre']
                    usuario.last_name =  request.POST['apellido']
                    usuario.is_active = True
                    usuario.set_password(request.POST['password'])
                    with transaction.atomic():
                        usuario.save()
                        registro.delete()
                    return HttpResponseRedirect('/acceder/')
                else:
                    error = 'Ocurrió un error al procesar la solicitud, las contraseñas no coinciden.'
        return render_to_response('usuarioactivar.html',{
        'Usuario':usuario,'Error':error
        }, context_instance=RequestContext(request))
    except:
        return render_to_response('404.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def usuarionuevo(request):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor and permisos.cre_usuarios:
        if request.method == 'POST':
            if  User.objects.filter(email=request.POST['email'].lower()).exists():
                return render_to_response('usuarionuevo.html',{
                'Activar':'Configuracion','activar':'Usuarios','Permisos':permisos,
                'Error':'Ocurrió un error al procesar la solicitud, este correo ya existe'
                }, context_instance=RequestContext(request))
            else:
                from strings import crear_cuenta
                # server=smtplib.SMTP('smtp.mandrillapp.com',587)
                server=smtplib.SMTP('email-smtp.us-east-1.amazonaws.com',587)
                server.ehlo()
                server.starttls()
                # server.login('Team@goanalytics.com','pR6yG1ztNHT7xW6Y8yigfw')
                server.login('AKIAIIG3SGXTWBK23VEQ','AtDj4P2QhDWTSIpkVv9ySRsz50KUFnusZ1cjFt+ZsdHC')
                chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                clave = ''.join(random.sample(chars, 16))
                key = ''.join(random.sample(chars, 96))
                usuario = User(
                first_name = request.POST['nombre'],
                last_name = request.POST['apellido'],
                email = request.POST['email'].lower(),
                username = request.POST['email'].lower(),
                is_active = False,
                last_login = timezone.now())
                usuario.set_password(clave)
                with transaction.atomic():
                    usuario.save()
                    usu_perm = Permisos(id=usuario)
                    try:
                        if(request.POST['consultor']):usu_perm.consultor=True
                    except:pass
                    try:
                        if(request.POST['cre_usuarios']):usu_perm.cre_usuarios = True
                    except:pass
                    try:
                        if(request.POST['act_variables']):usu_perm.act_variables = True
                    except:pass
                    try:
                        if(request.POST['det_see']):usu_perm.det_see = True
                    except:pass
                    try:
                        if(request.POST['res_exp']):usu_perm.res_exp = True
                    except:pass
                    try:
                        if(request.POST['res_see']):usu_perm.res_see = True
                    except:pass
                    try:
                        if(request.POST['pro_see']):usu_perm.pro_see = True
                    except:pass
                    try:
                        if(request.POST['pro_add']):usu_perm.pro_add = True
                    except:pass
                    try:
                        if(request.POST['pro_edit']):usu_perm.pro_edit = True
                    except:pass
                    try:
                        if(request.POST['pro_del']):usu_perm.pro_del = True
                    except:pass
                    try:
                        if(request.POST['col_see']):usu_perm.col_see = True
                    except:pass
                    try:
                        if(request.POST['col_add']):usu_perm.col_add = True
                    except:pass
                    try:
                        if(request.POST['col_edit']):usu_perm.col_edit = True
                    except:pass
                    try:
                        if(request.POST['col_del']):usu_perm.col_del = True
                    except:pass
                    try:
                        if(request.POST['var_see']):usu_perm.var_see = True
                    except:pass
                    try:
                        if(request.POST['var_add']):usu_perm.var_add = True
                    except:pass
                    try:
                        if(request.POST['var_edit']):usu_perm.var_edit = True
                    except:pass
                    try:
                        if(request.POST['var_del']):usu_perm.var_del = True
                    except:pass
                    try:
                        if(request.POST['red_see']):usu_perm.red_see = True
                    except:pass
                    try:
                        if(request.POST['red_add']):usu_perm.red_add = True
                    except:pass
                    try:
                        if(request.POST['red_edit']):usu_perm.red_edit = True
                    except:pass
                    try:
                        if(request.POST['red_del']):usu_perm.red_del = True
                    except:pass
                    usu_perm.save()
                    IndiceUsuarios.objects.create(
                    usuario=usuario,
                    name=usuario.username,
                    parent=request.user.indiceusuarios)
                    Recuperar.objects.create(usuario=usuario,link=key)
                    nom_log =request.user.first_name+' '+request.user.last_name
                    Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Creó al usuario",descripcion=usuario.first_name+" "+usuario.last_name)

                destinatario = [usuario.email]
                msg=MIMEMultipart()
                msg["subject"]=  'Registro de cuenta.'
                # msg['From'] = email.utils.formataddr(('GoAnalytics', 'Team@goanalytics.com'))
                msg['From'] = email.utils.formataddr(('GoAnalytics', 'team@bigtalenter.com'))
                url = 'http://159.203.190.248/activar/'+key
                nombre = (usuario.first_name).encode("ascii", "xmlcharrefreplace")
                html = crear_cuenta(nombre,url)
                mensaje = MIMEText(html,"html")
                msg.attach(mensaje)
                # server.sendmail('Team@goanalytics.com',destinatario,msg.as_string())
                server.sendmail('team@bigtalenter.com',destinatario,msg.as_string())
                server.quit()
                return HttpResponseRedirect('/usuarios/')
        return render_to_response('usuarionuevo.html',{
        'Activar':'Configuracion','activar':'Usuarios','Permisos':permisos,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')

#===============================================================================
#   Licencia y cuenta
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def licencia(request):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor:
        empresas = Empresas.objects.filter(usuario=request.user)
        return render_to_response('licencia.html',{
        'Activar':'Configuracion','activar':'GestionarCuenta','activarp':'Licencia',
        'Permisos':permisos
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def cuenta(request):
    acceso = None
    cambio = ''
    cache.delete(request.user)
    permisos = request.user.permisos
    if request.method == 'POST':
        usuario = request.user
        P = request.POST['cpassword']
        clave = request.POST['password']
        clave2 = request.POST['password2']
        acceso = authenticate(username=usuario, password=P)
        if ((acceso is not None) and (clave == clave2)):
            usuario.set_password(clave)
            usuario.save()
            cambio= "Se ha cambiado la contraseña exitosamente."
        else:
            cambio= "Credenciales incorrectas, intente nuevamente."

    return render_to_response('cuenta.html',{
    'Activar':'Configuracion','activar':'GestionarCuenta','activarp':'Cuenta',
    'Cambio':cambio,'Permisos':permisos
    }, context_instance=RequestContext(request))

#===============================================================================
#   Logs
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def logs(request):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor:
        usuarios_creados = IndiceUsuarios.objects.filter(usuario=request.user
                            ).get_descendants(include_self=True).select_related('usuario')
        aux = []
        for  i in usuarios_creados:
            aux.append(i.usuario.username)

        logs = Logs.objects.filter(usuario_username__in=aux)
        return render_to_response('logs.html',{
        'Activar':'Configuracion','activar':'Logs','Logs':logs,'Permisos':permisos
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')


#===============================================================================
#    Páginas de errores
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def reportarerror(request):
    cache.delete(request.user)
    permisos = request.user.permisos
    if permisos.consultor:
        aviso = None
        if request.method == 'POST':
            nom_log =request.user.first_name+' '+request.user.last_name
            try:
                error = Errores(usuario=nom_log,reporte=request.POST['reporte'],
                        imagen=request.FILES['imagen'])
            except:
                error = Errores(usuario=nom_log,reporte=request.POST['reporte'])

            with transaction.atomic():
                Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,accion="Reportó un error",descripcion='Esperando respuesta')
                error.save()
                aviso = "ok"
            # server=smtplib.SMTP('smtp.mandrillapp.com',587)
            server=smtplib.SMTP('email-smtp.us-east-1.amazonaws.com',587)
            server.ehlo()
            server.starttls()
            server.login('no-reply@gochangeanalytics.com','anVgUmTPhGyqT8J9D5yM1A')

            destinatario = ['ilgaleanos@gmail.com','lamedinaa@gmail.com','jshenaop@gmail.com']
            msg=MIMEMultipart()
            msg["subject"]=  'Reporte de error.'
            msg['To'] = email.utils.formataddr(('Respetado', destinatario))
            msg['From'] = email.utils.formataddr(('GoAnalytics', 'no-reply@gochangeanalytics.com'))

            nombre = (nom_log).encode("ascii", "xmlcharrefreplace")
            usuario = (request.user.username).encode("ascii", "xmlcharrefreplace")
            html = 'El usuario '+nombre+' con usuario '+usuario+' ha reportado un error en Goanalytics: <br>'+(request.POST['reporte']).encode("ascii", "xmlcharrefreplace")
            parte2=MIMEText(html,"html")
            msg.attach(parte2)
            server.sendmail('no-reply@gochangeanalytics.com',destinatario,msg.as_string())
            server.quit()
        return render_to_response('reportarerror.html',{
        'Activar':'CentroDeAyuda','activar':'Reportar','Permisos':permisos,
        'Aviso':aviso
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')

#===============================================================================
#    Páginas de legal
#===============================================================================

@cache_control(no_store=True)
def terminos(request):
    return render_to_response('terminos.html')

@cache_control(no_store=True)
def privacidad(request):
    return render_to_response('privacidad.html')


#===============================================================================
#    Páginas de errores
#===============================================================================

@cache_control(no_store=True)
def e400(request):
    return render_to_response('400.html')

@cache_control(no_store=True)
def e403(request):
    return render_to_response('403.html')

@cache_control(no_store=True)
def e404(request):
    return render_to_response('404.html')

@cache_control(no_store=True)
def e500(request):
    return render_to_response('500.html')
