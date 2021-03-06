# -*- encoding: utf-8 -*-
from colaboradores_360.models import *
from cuestionarios_360.models import *
from datetime import datetime as DT
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.views.decorators.cache import cache_control
from mensajeria_360.models import Streaming_360
from usuarios.models import Proyectos, Logs
from redes_360.models import Redes_360
import random
# from .colabora import ver_colaboradores
from colaboradores_360.models import Colaboradores_360, ColaboradoresDatos_360
from usuarios.models import Proyectos
#===============================================================================
# indices
#===============================================================================


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def colaboradores_ind_360(request):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa"] :
        return render_to_response('423.html')
    permisos = request.user.permisos
    if permisos.consultor and permisos.col_see:
        #tabla = ver_colaboradores(str(proyecto.id),permisos.col_edit,permisos.col_del)
        col = Colaboradores_360.objects.filter(proyecto=proyecto.id)
        tabla = ""
        auxiliar = ""
        for i in col.all():
            tabla += "<tr><td>"
            auxiliar = i.nombre
            tabla += auxiliar + "</td><td>"
            auxiliar = i.apellido
            tabla += auxiliar + "</td><td>"
            if i.externo:
                auxiliar = i.descripcion
                tabla += auxiliar + "</td><td>"
            else:
                try:
                    col_datos = ColaboradoresDatos_360.objects.get(id=i.id)
                    auxiliar = col_datos.cargo
                    tabla += auxiliar + "</td><td>"
                except:
                    tabla += "</td><td>"

            id_ = i.id
            auxiliar = i.email
            tabla += auxiliar + "</td><td id='e"+str(id_)+"'>"
            if i.estado:
                tabla += "<span style='color:#1d9d73'>Activo</span></td><td>"
            else:
                tabla += "<span style='color:#cd1e21'>Inactivo</span></td><td>"
            #3if  editar :
            tabla += "<span style='cursor:pointer;color:#1d9d73' onclick=\"actualizar("+str(id_)+")\" ><i class='fa fa-retweet m-r' title='Activar/Desactivar'></i></span><a href='/360/participante/editar/"+str(id_)+"/'><i class='fa fa-edit m-r' title='editar'></i></a>"
            #if  eliminar :
            tabla += "<a href='/360/participante/eliminar/"+str(id_)+"/'><i class='fa fa-trash m-r' title='eliminar'></i></a></td></tr>"
            #else:
                #output += "<td></tr>"
        # print '################################################'
        # print tabla
        return render_to_response('colaboradores_ind_360.html',{
        'Activar':'Contenido','activar':'Individual',
        'Proyecto':proyecto,'Permisos':permisos,'Tabla':tabla
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')

#===============================================================================
# nuevo
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def colaboradornuevo_360(request):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa"] :
        return render_to_response('423.html')
    permisos = request.user.permisos
    if permisos.consultor and permisos.col_add:
        emails = Colaboradores_360.objects.only('email').filter(proyecto_id=proyecto.id)
        if request.method == 'POST':
            chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            key = ''.join(random.sample(chars, 64))
            if not Colaboradores_360.objects.filter(proyecto=proyecto,email=request.POST['email'].strip()).exists():
                with transaction.atomic():
                    participante = Colaboradores_360(
                                    nombre = request.POST['nombre'].strip(),
                                    apellido = request.POST['apellido'].strip(),
                                    key = key,
                                    key_old = 'HACK',
                                    email = request.POST['email'].lower().strip(),
                                    genero = request.POST['genero'],
                                    proyecto_id = proyecto.id)

                    try:
                        if(request.POST['estado']):
                            participante.estado = True
                    except:
                        participante.estado = False

                    try:
                        if(request.POST['externo']):
                            participante.externo = True
                    except:
                        participante.externo = False

                    try: participante.descripcion = request.POST['descripcion'].strip()
                    except: pass

                    participante.save()
                    print '######################################'
                    datos = ColaboradoresDatos_360(id = participante)
                    try:datos.area = request.POST['area'].strip()
                    except:pass
                    try:datos.cargo = request.POST['cargo'].strip()
                    except:pass
                    try:datos.ciudad = request.POST['ciudad'].strip()
                    except:pass
                    try:datos.regional = request.POST['regional'].strip()
                    except:pass
                    try:datos.niv_academico = request.POST['niv_academico'].strip()
                    except:pass
                    try:datos.profesion = request.POST['profesion'].strip()
                    except:pass
                    try: datos.fec_ingreso = DT.strptime(str(request.POST['fec_ingreso']),'%d/%m/%Y')
                    except: datos.fec_ingreso = None
                    try: datos.fec_nacimiento = DT.strptime(str(request.POST['fec_nacimiento']),'%d/%m/%Y')
                    except: datos.fec_nacimiento = None

                    proyecto_datos = proyecto.proyectosdatos
                    if proyecto_datos.opcional1:
                        try:datos.opcional1 = request.POST['opcional1'].strip()
                        except:pass
                    if proyecto_datos.opcional2:
                        try:datos.opcional2 = request.POST['opcional2'].strip()
                        except:pass
                    if proyecto_datos.opcional3:
                        try:datos.opcional3 = request.POST['opcional3'].strip()
                        except:pass
                    if proyecto_datos.opcional4:
                        try:datos.opcional4 = request.POST['opcional4'].strip()
                        except:pass
                    if proyecto_datos.opcional5:
                        try:datos.opcional5 = request.POST['opcional5'].strip()
                        except:pass
                    Proyectos.objects.filter(id=proyecto.id).update(tot_participantes=F("tot_participantes")+1)
                    datos.save()
                    ColaboradoresMetricas_360.objects.create(id=participante)

                    #  dependiendo del tipo se ejecuta auto o no
                    if (proyecto.tipo =="360 unico"):
                        instrumento = Instrumentos_360.objects.only('id').filter( proyecto_id = proyecto.id )[0]
                        preguntas = Preguntas_360.objects.filter( proyecto_id = proyecto.id, instrumento_id=instrumento.id)
                        red = Redes_360.objects.only('id','evaluado_id').filter(proyecto_id = proyecto.id)[0]
                        streaming_crear = []
                        adicionales = 0
                        for j in preguntas:
                            try:
                                streaming_crear.append(Streaming_360(
                                                        proyecto_id=proyecto.id,
                                                        instrumento_id=instrumento.id,
                                                        colaborador_id=participante.id,
                                                        evaluado = red.evaluado_id,
                                                        red_id = red.id,
                                                        pregunta_id=j.id))
                                adicionales += 1
                            except:
                                pass
                        if(proyecto.tot_aresponder):
                            total = 100.0*proyecto.tot_respuestas/proyecto.tot_aresponder
                            Proyectos.objects.filter(id=proyecto.id).update(total=total )

                        if(streaming_crear):
                            Streaming_360.objects.bulk_create(streaming_crear)
                            Proyectos.objects.filter(id=proyecto.id).update(tot_aresponder=F("tot_aresponder")+adicionales)
                    proyecto = Proyectos.objects.get(id=proyecto.id)
                    cache.set(request.user.username,proyecto,86400)
                    nom_log = request.user.first_name+' '+request.user.last_name
                    Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,
                    accion="Creó al participante",descripcion=participante.nombre+' '+participante.apellido)
                return HttpResponseRedirect('/360/participantes/individual')

        return render_to_response('colaborador.html',{
        'Activar':'Contenido','activar':'Individual','accion':'registrar',
        'Proyecto':proyecto,'Permisos':permisos,'Emails':emails
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')


#===============================================================================
# editar
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def colaboradoreditar_360(request,id_colaborador):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa"] :
        return render_to_response('423.html')
    permisos = request.user.permisos
    if permisos.consultor and permisos.col_edit:
        try:participante = Colaboradores_360.objects.filter(proyecto=proyecto
                            ).select_related('colaboradoresdatos_360').get(id=id_colaborador)
        except:return render_to_response('403.html')
        emails = Colaboradores_360.objects.only('email').filter(proyecto=proyecto).exclude(id=id_colaborador)
        if request.method == 'POST':
            if not Colaboradores_360.objects.exclude(id=id_colaborador).filter(proyecto_id=proyecto.id,email=request.POST['email'].strip()).exists():
                participante.nombre = request.POST['nombre'].strip()
                participante.apellido = request.POST['apellido'].strip()
                participante.email = request.POST['email'].strip()
                participante.genero = request.POST['genero']
                try:
                    if(request.POST['estado']):
                        participante.estado = True
                except:
                    participante.estado = False
                try:
                    if(request.POST['externo']):
                        participante.externo = True
                except:
                    participante.externo = False

                try: participante.descripcion = request.POST['descripcion'].strip()
                except: participante.descripcion = None

                datos = participante.colaboradoresdatos_360
                datos.area = request.POST['area'].strip()
                datos.cargo = request.POST['cargo'].strip()
                datos.ciudad = request.POST['ciudad'].strip()
                try:
                    if(request.POST['fec_ingreso']):
                        datos.fec_ingreso = DT.strptime(str(request.POST['fec_ingreso']),'%d/%m/%Y')
                except:
                    datos.fec_nacimiento = None
                try:
                    if(request.POST['fec_nacimiento']):
                        datos.fec_nacimiento = DT.strptime(str(request.POST['fec_nacimiento']),'%d/%m/%Y')
                except:
                    datos.fec_nacimiento = None
                datos.niv_academico = request.POST['niv_academico'].strip()
                datos.profesion = request.POST['profesion'].strip()
                datos.regional = request.POST['regional'].strip()
                proyecto_datos = proyecto.proyectosdatos
                if proyecto_datos.opcional1:
                    datos.opcional1 = request.POST['opcional1'].strip()
                if proyecto_datos.opcional2:
                    datos.opcional2 = request.POST['opcional2'].strip()
                if proyecto_datos.opcional3:
                    datos.opcional3 = request.POST['opcional3'].strip()
                if proyecto_datos.opcional4:
                    datos.opcional4 = request.POST['opcional4'].strip()
                if proyecto_datos.opcional5:
                    datos.opcional5 = request.POST['opcional5'].strip()
                with transaction.atomic():
                    participante.save()
                    datos.save()
                    nom_log = request.user.first_name+' '+request.user.last_name
                    Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,
                    accion="Editó al participante",descripcion=participante.nombre+' '+participante.apellido)
                return HttpResponseRedirect('/360/participantes/individual')
        return render_to_response('colaborador.html',{
        'Activar':'Contenido','activar':'Individual','accion':'editar',
        'Proyecto':proyecto,'Permisos':permisos,'Participante':participante,'Emails':emails,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')

#===============================================================================
# activar/desactivar
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def colaboradoractivar_360(request,id_colaborador):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa"] :
        return render_to_response('423.html')
    permisos = request.user.permisos
    if permisos.consultor and permisos.col_edit:
        try:participante = Colaboradores_360.objects.only('estado').filter(proyecto=proyecto).get(id=id_colaborador)
        except:return render_to_response('403.html')
        if(participante.estado):
             Colaboradores_360.objects.filter(id=id_colaborador).update(estado=False)
        else:
            Colaboradores_360.objects.filter(id=id_colaborador).update(estado=True)
        return JsonResponse({'id': id_colaborador,'estado':1-int(participante.estado)})
    else:
        return render_to_response('403.html')

#===============================================================================
# nuevo archivo
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def archivo_360(request):
    import xlwt
    date_format = xlwt.XFStyle()
    date_format.num_format_str = '@'
    tit_format = xlwt.easyxf('font:bold on ;align:wrap on, vert centre, horz center;')
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa"] :
        return render_to_response('423.html')
    permisos = request.user.permisos
    if permisos.consultor and permisos.col_add:
        response = HttpResponse(content_type='application/ms-excel')
        import string
        a ='Participantes'
        response['Content-Disposition'] = 'attachment; filename=%s.xls'%(a)
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet(a)
        datos = proyecto.proyectosdatos
        ws.write(0,0,u"Nombre",tit_format)
        ws.write(0,1,u"Apellido",tit_format)
        ws.write(0,2,u"Email",tit_format)
        ws.write(0,3,u"Género",tit_format)
        ws.write(0,4,u"Descripción (solo externos)",tit_format)
        ws.write(0,5,u"Área",tit_format)
        ws.write(0,6,u"Cargo",tit_format)
        ws.write(0,7,u"Regional",tit_format)
        ws.write(0,8,u"Ciudad",tit_format)
        ws.write(0,9,u"Nivel académico",tit_format)
        ws.write(0,10,u"Profesión",tit_format)
        ws.write(0,11,u"Fecha de nacimiento mm/dd/yyyy",tit_format)
        ws.write(0,12,u"Fecha de ingreso mm/dd/yyyy",tit_format)
        for i in xrange(1,10000):
            ws.write(i,11,"",date_format)
            ws.write(i,12,"",date_format)
        if(datos.opcional1):
            ws.write(0,13,datos.opcional1,tit_format)
        if(datos.opcional2):
            ws.write(0,14,datos.opcional2,tit_format)
        if(datos.opcional3):
            ws.write(0,15,datos.opcional3,tit_format)
        if(datos.opcional4):
            ws.write(0,16,datos.opcional4,tit_format)
        if(datos.opcional5):
            ws.write(0,17,datos.opcional5,tit_format)
        wb.save(response)
        return response

#===============================================================================
# subir participantes archivo
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def colaboradores_xls_360(request):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa"] :
        return render_to_response('423.html')
    proyecto = Proyectos.objects.get(id=proyecto.id)
    permisos = request.user.permisos
    if permisos.consultor and permisos.col_add:
        error = None
        if request.method == 'POST':
            import xlrd,xlwt
            date_format = xlwt.XFStyle()
            input_excel = request.FILES['docfile']
            doc = xlrd.open_workbook(file_contents=input_excel.read())
            sheet = doc.sheet_by_index(0)
            filas = sheet.nrows
            var_error = None
            try:
                proyecto_datos = proyecto.proyectosdatos
                vector_personas = []
                vector_ignorar = []
                vector_email = []
                chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                for i in xrange(1,filas):
                    if sheet.cell_value(i,2).lower().strip() in vector_email or Colaboradores_360.objects.filter(
                            proyecto=proyecto,
                            email=sheet.cell_value(i,2).lower().strip() ).exists():
                        vector_ignorar.append(i)
                        vector_personas.append('dummy')
                    else:
                        vector_email.append(sheet.cell_value(i,2).lower().strip())
                        var_error = sheet.cell_value(i,0)+' '+sheet.cell_value(i,1)
                        key = ''.join(random.sample(chars, 64))
                        persona = Colaboradores_360(
                            nombre=sheet.cell_value(i,0).strip(),
                            apellido = sheet.cell_value(i,1).strip(),
                            key = key,
                            email=sheet.cell_value(i,2).lower().strip(),
                            genero=sheet.cell_value(i,3).capitalize().strip(),
                            estado=True,proyecto=proyecto)
                        if not sheet.cell_value(i,6):
                            persona.externo = True
                        vector_personas.append(persona)

                vector_datos = []
                vector_metricas = []
                with transaction.atomic():
                    participantes_conteo = 0
                    for i in xrange(1, filas):
                        if i not in vector_ignorar:
                            participantes_conteo += 1
                            vector_personas[i-1].save()
                            vector_metricas.append(ColaboradoresMetricas_360(id=vector_personas[i-1]))
                            datos = ColaboradoresDatos_360(id=vector_personas[i-1])
                            if sheet.cell_value(i, 5):
                                datos.area = sheet.cell_value(i, 5).strip()
                                # datos.save()
                            if sheet.cell_value(i, 6):
                                datos.cargo = sheet.cell_value(i, 6).strip()
                                # datos.save()
                            if sheet.cell_value(i, 7):
                                datos.regional = sheet.cell_value(i, 7).strip()
                                # datos.save()
                            if sheet.cell_value(i, 8):
                                datos.ciudad = sheet.cell_value(i, 8).strip()
                                # datos.save()
                            if sheet.cell_value(i, 9):
                                datos.niv_academico = sheet.cell_value(i, 9).strip()
                                # datos.save()
                            if sheet.cell_value(i, 10):
                                datos.profesion = sheet.cell_value(i, 10).strip()
                                # datos.save()
                            if sheet.cell_value(i, 11):
                                a1 = sheet.cell_value(i, 11)
                                # print doc.datemode
                                a1_tuple = xlrd.xldate_as_tuple(a1, doc.datemode)
                                # print a1_tuple
                                datos.fec_nacimiento = DT(*a1_tuple).strftime("%Y-%m-%d")
                                # print '##################################################'
                                # datos.save()
                                # print datos.fec_nacimiento
                                # datos.fec_nacimiento =  DT.strptime(sheet.cell_value(i, 11), '%d/%m/%Y')
                            if sheet.cell_value(i, 12):
                                a1 = sheet.cell_value(i, 12)
                                a1_tuple = xlrd.xldate_as_tuple(a1, doc.datemode)
                                datos.fec_ingreso = DT(*a1_tuple).strftime("%Y-%m-%d")
                                # datos.save()
                                # datos.fec_ingreso =  DT.strptime(sheet.cell_value(i,12), '%d/%m/%Y')
                            if proyecto_datos.opcional1:
                                datos.opcional1 = sheet.cell_value(i, 13).strip()
                                # datos.save()
                            if proyecto_datos.opcional2:
                                datos.opcional2 = sheet.cell_value(i, 14).strip()
                                # datos.save()
                            if proyecto_datos.opcional3:
                                datos.opcional3 = sheet.cell_value(i, 15).strip()
                                # datos.save()
                            if proyecto_datos.opcional4:
                                datos.opcional4 = sheet.cell_value(i, 16).strip()
                                # datos.save()
                            if proyecto_datos.opcional5:
                                datos.opcional5 = sheet.cell_value(i, 17).strip()
                                # datos.save()
                            # vector_datos.append(datos)
                            datos.save()
                            #  dependiendo del tipo se ejecuta auto o no
                            if (proyecto.tipo == "360 unico"):

                                instrumento = Instrumentos_360.objects.only('id').filter(proyecto_id=proyecto.id)[0]
                                preguntas = Preguntas_360.objects.filter(proyecto_id=proyecto.id,
                                                                         instrumento_id=instrumento.id)
                                streaming_crear = []
                                # streaming = Streaming_360(proyecto_id=proyecto.id)
                                adicionales = 0
                                for j in preguntas:
                                    try:
                                        # print '##################################################'
                                        # print proyecto.id, instrumento.id, vector_personas[i-1].id, j.id
                                        streaming_crear.append(Streaming_360(
                                                                proyecto_id=proyecto.id,
                                                                instrumento_id=instrumento.id,
                                                                colaborador_id=vector_personas[i-1].id,
                                                                pregunta_id=j.id))
                                        # streaming.instrumento_id = instrumento.id
                                        # streaming.colaborador_id = vector_personas[i-1].id
                                        # streaming.pregunta_id = j.id
                                        # # streaming.save()
                                        adicionales += 1
                                    except:
                                        pass
                                if(proyecto.tot_aresponder):
                                    val = 100.0*proyecto.tot_respuestas/proyecto.tot_aresponder
                                    Proyectos.objects.filter(id=proyecto.id).update(total=val)
                                if(streaming_crear):
                                    # Streaming_360.objects.bulk_create(streaming_crear)
                                    # print '##################################################'
                                #     print streaming_crear
                                    # streaming.save()
                                    Proyectos.objects.filter(id=proyecto.id).update(tot_aresponder=F("tot_aresponder")+adicionales)
                    # if(streaming_crear):
                    #     print '###########################'
                    #     print streaming_crear
                    #     Streaming_360.objects.bulk_create(streaming_crear)
                    #ColaboradoresDatos_360.objects.bulk_create(vector_datos)
                    ColaboradoresMetricas_360.objects.bulk_create(vector_metricas)
                    Proyectos.objects.filter(id=proyecto.id).update(tot_participantes=F("tot_participantes")+participantes_conteo)
                proyecto = Proyectos.objects.get(id=proyecto.id)
                cache.set(request.user.username,proyecto,86400)
                if(permisos.col_see):
                    return HttpResponseRedirect('/360/participantes/individual/')
                else:
                    error = "Todos los colaboradores se han subido con éxito"
            except:
                error= "Ocurrio un error cuando se procesaba al participante "+var_error

        return render_to_response('colaboradores_xls_360.html',{
        'Activar':'Contenido','activar':'AcrhivoPlano',
        'Proyecto':proyecto,'Permisos':permisos,'Error':error
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')

#===============================================================================
# eliminar
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def colaboradoreliminar_360(request,id_colaborador):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa"] :
        return render_to_response('423.html')
    proyecto = Proyectos.objects.get(id=proyecto.id)
    permisos = request.user.permisos
    if permisos.consultor and permisos.col_del:
        try:
            participante = Colaboradores_360.objects.filter(proyecto_id=proyecto.id).get(id=id_colaborador)
        except:
            return render_to_response('403.html')
        if request.method == 'POST':
            # maestro = Proyectos.objects.get(id=1)

            with transaction.atomic():
                Colaboradores_360.objects.filter(id=id_colaborador).delete()
                proyecto.tot_participantes = Colaboradores_360.objects.filter(proyecto=proyecto.id).count()
                proyecto.tot_aresponder = Streaming_360.objects.filter(proyecto=proyecto).count()
                proyecto.tot_respuestas = Streaming_360.objects.filter(proyecto=proyecto,respuesta__isnull=False).count()
                if(proyecto.tot_aresponder):
                    proyecto.total = 100.0*proyecto.tot_respuestas/proyecto.tot_aresponder
                nom_log = request.user.first_name+' '+request.user.last_name
                Logs.objects.create(usuario=nom_log,usuario_username=request.user.username,
                accion="Eliminó al participante",descripcion=participante.nombre+' '+participante.apellido)
                proyecto.save()
                cache.set(request.user.username,proyecto,86400)
            return HttpResponseRedirect('/360/participantes/individual/')
    return render_to_response('col_eliminar_360.html',{
    'Activar':'Contenido','activar':'Individual',
    'objeto':'Participante','Participante':participante,
    'Proyecto':proyecto,'Permisos':permisos,
    }, context_instance=RequestContext(request))

#===============================================================================
# roles
#===============================================================================

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def roles_360(request):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa","360 unico"] :
        return render_to_response('423.html')
    permisos = request.user.permisos
    if permisos.consultor and permisos.var_see:
        roles = Roles_360.objects.filter(proyecto=proyecto)
        return render_to_response('roles.html',{
        'Activar':'Contenido','activar':'Roles',
        'Roles':roles,'Proyecto':proyecto,'Permisos':permisos,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('403.html')

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def rolnuevo_360(request):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa","360 unico"] :
        return render_to_response('423.html')
    permisos = request.user.permisos
    if permisos.consultor and permisos.var_add:
        if request.method == "POST":
            if not Roles_360.objects.filter(nombre=request.POST['nombre'].strip(),proyecto_id=proyecto.id).exists():
                rol = Roles_360.objects.create(nombre=request.POST['nombre'].strip(),proyecto_id=proyecto.id)
                return JsonResponse({'id':rol.id,'nombre':request.POST['nombre'].strip()})
            else:
                return HttpResponse(0)
        return render_to_response('404.html')
    else:
        return render_to_response('403.html')

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def roleditar_360(request,id_rol):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa","360 unico"] :
        return render_to_response('423.html')
    permisos = request.user.permisos
    if permisos.consultor and permisos.var_edit:
        if request.method == 'POST':
            if not Roles_360.objects.exclude(id=id_rol).filter(nombre=request.POST['nombre'].strip(),proyecto_id=proyecto.id).exists():
                with transaction.atomic():
                    Roles_360.objects.filter(proyecto_id=proyecto.id,id=id_rol).update(nombre=request.POST['nombre'].strip())
                    Redes_360.objects.filter(proyecto_id=proyecto.id,rol_idn=id_rol).update(rol=request.POST['nombre'].strip())
                    return JsonResponse({'id':id_rol,'nombre':request.POST['nombre'].strip()})
        return HttpResponse(0)
    else:
        return render_to_response('403.html')

@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def roleliminar_360(request,id_rol):
    proyecto = cache.get(request.user.username)
    if not proyecto or proyecto.tipo in ["Completa","Fragmenta","Externa","360 unico"] :
        return render_to_response('423.html')
    permisos = request.user.permisos
    if permisos.consultor and permisos.var_del:
        Roles_360.objects.filter(proyecto_id=proyecto.id,id=id_rol).delete()
        return JsonResponse({'id':id_rol})
    else:
        return render_to_response('403.html')
