# -*- encoding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.views.decorators.cache import cache_control
from colaboradores.models import Colaboradores, ColaboradoresDatos
from cuestionarios.models import  Preguntas, Variables, Respuestas
from mensajeria.models import Streaming
from usuarios.models import Proyectos, Logs
import grafos as gr
import string



@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def participacion(request):
	proyecto = cache.get(request.user.username)
	pdatos = proyecto.proyectosdatos
	if not proyecto:
		return render_to_response('423.html')
	permisos = request.user.permisos
	if permisos.res_see:
		datos = Streaming.objects.only(
				'respuesta','fecharespuesta',
				'proyecto__proyectosdatos__opcional1',
				'proyecto__proyectosdatos__opcional2',
				'proyecto__proyectosdatos__opcional3',
				'proyecto__proyectosdatos__opcional4',
				'proyecto__proyectosdatos__opcional5',
				'colaborador__colaboradoresdatos__regional',
				'colaborador__colaboradoresdatos__ciudad',
				'colaborador__colaboradoresdatos__area',
				'colaborador__colaboradoresdatos__cargo',
				'colaborador__colaboradoresdatos__genero',
				'colaborador__colaboradoresdatos__niv_academico',
				'colaborador__colaboradoresdatos__profesion',
				'colaborador__colaboradoresdatos__opcional1',
			    'colaborador__colaboradoresdatos__opcional2',
			    'colaborador__colaboradoresdatos__opcional3',
			    'colaborador__colaboradoresdatos__opcional4',
			    'colaborador__colaboradoresdatos__opcional5'
				).filter(
					proyecto_id=proyecto.id
				).select_related(
					'proyecto','proyecto__proyectosdatos',
					'colaborador','colaborador__colaboradoresdatos'
				)

		if( proyecto.tot_preguntas and proyecto.tot_respuestas ):
			finalizados = proyecto.tot_respuestas/proyecto.tot_preguntas
		else:
			finalizados = 0
		return render_to_response('participacion.html',{
			'Activar':'AnalisisResultados','activar':'Participacion','Datos':datos,
			'Proyecto':proyecto,'Permisos':permisos,'Finalizados':finalizados,'PDatos':pdatos,
		}, context_instance=RequestContext(request))
	else:
		return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def focalizado(request):
	proyecto = cache.get(request.user.username)
	pdatos = proyecto.proyectosdatos
	if not proyecto:
		return render_to_response('423.html')
	permisos = request.user.permisos
	if permisos.res_see:
		variables = Variables.objects.filter(proyecto_id=proyecto.id)
		preguntas = Preguntas.objects.prefetch_related('respuestas_set').filter(variable__in=variables,abierta=False)
		datos = Streaming.objects.only(
				'respuesta','fecharespuesta',
				'pregunta__texto',
				'pregunta__numerica',
				'pregunta__multiple',
				'pregunta__abierta',
				'pregunta__variable__nombre',
				'proyecto__proyectosdatos__opcional1',
				'proyecto__proyectosdatos__opcional2',
				'proyecto__proyectosdatos__opcional3',
				'proyecto__proyectosdatos__opcional4',
				'proyecto__proyectosdatos__opcional5',
				'colaborador__colaboradoresdatos__regional',
				'colaborador__colaboradoresdatos__ciudad',
				'colaborador__colaboradoresdatos__area',
				'colaborador__colaboradoresdatos__cargo',
				'colaborador__colaboradoresdatos__niv_academico',
				'colaborador__colaboradoresdatos__profesion',
				'colaborador__colaboradoresdatos__opcional1',
			    'colaborador__colaboradoresdatos__opcional2',
			    'colaborador__colaboradoresdatos__opcional3',
			    'colaborador__colaboradoresdatos__opcional4',
			    'colaborador__colaboradoresdatos__opcional5'
				).filter(
					proyecto_id=proyecto.id,
					pregunta__abierta=False,
					respuesta__isnull=False
				).select_related(
					'proyecto__proyectosdatos',
					'pregunta','pregunta__variable',
					'colaborador','colaborador__colaboradoresdatos'
				).order_by('fecharespuesta')
		return render_to_response('focalizado.html',{
			'Activar':'AnalisisResultados','activar':'Focalizados','PDatos':pdatos,
			'Proyecto':proyecto,'Permisos':permisos,'Datos':datos,'Preguntas':preguntas
		}, context_instance=RequestContext(request))
	else:
		return render_to_response('403.html')


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def general(request):
	proyecto = cache.get(request.user.username)
	pdatos = proyecto.proyectosdatos
	if not proyecto:
		return render_to_response('423.html')
	permisos = request.user.permisos
	if permisos.res_see:
		variables = Variables.objects.filter(proyecto_id=proyecto.id)
		preguntas = Preguntas.objects.prefetch_related('respuestas_set').filter(variable__in=variables,abierta=False)
		datos = Streaming.objects.only(
					'respuesta','fecharespuesta',
					'pregunta__texto',
					'pregunta__numerica',
					'pregunta__multiple',
					'pregunta__abierta',
					'pregunta__variable__nombre',
					'proyecto__proyectosdatos__opcional1',
					'proyecto__proyectosdatos__opcional2',
					'proyecto__proyectosdatos__opcional3',
					'proyecto__proyectosdatos__opcional4',
					'proyecto__proyectosdatos__opcional5',
					'colaborador__nombre',
					'colaborador__apellido',
					'colaborador__colaboradoresdatos__regional',
					'colaborador__colaboradoresdatos__ciudad',
					'colaborador__colaboradoresdatos__area',
					'colaborador__colaboradoresdatos__cargo',
					'colaborador__colaboradoresdatos__niv_academico',
					'colaborador__colaboradoresdatos__profesion',
					'colaborador__colaboradoresdatos__opcional1',
					'colaborador__colaboradoresdatos__opcional2',
					'colaborador__colaboradoresdatos__opcional3',
					'colaborador__colaboradoresdatos__opcional4',
					'colaborador__colaboradoresdatos__opcional5'
				).filter(
					proyecto_id=proyecto.id,
					pregunta__abierta=False,
					respuesta__isnull=False
				).select_related(
					'proyecto__proyectosdatos',
					'pregunta','pregunta__variable',
					'colaborador','colaborador__colaboradoresdatos'
				).order_by('fecharespuesta')
		return render_to_response('general.html',{
			'Activar':'AnalisisResultados','activar':'General','PDatos':pdatos,
			'Proyecto':proyecto,'Permisos':permisos,'Datos':datos,'Preguntas':preguntas
		}, context_instance=RequestContext(request))
	else:
		return render_to_response('403.html')


def solucion(a):
	a = str(a).lower()
	a = string.replace(a,',','')
	a = string.replace(a,'(','')
	a = string.replace(a,')','')
	a = string.replace(a,'[','')
	a = string.replace(a,']','')
	a = string.replace(a,'{','')
	a = string.replace(a,'}','')
	a = string.replace(a,"'",'')
	a = string.replace(a,'.','')
	a = string.replace(a,':','')
	a = string.replace(a,';','')
	a = string.replace(a,'=','')
	a = string.replace(a,'?','')
	a = string.replace(a,'¿','')
	a = string.replace(a,'&','')
	a = string.replace(a,'#','')
	a = string.replace(a,'%','porciento')
	a = string.replace(a,'|','')
	a = string.replace(a,'!','')
	a = string.replace(a,'¡','')
	a = string.replace(a,'á','a')
	a = string.replace(a,'é','e')
	a = string.replace(a,'í','i')
	a = string.replace(a,'ó','o')
	a = string.replace(a,'ú','u')
	return a


@cache_control(no_store=True)
@login_required(login_url='/acceder/')
def wordanalytics(request):
	proyecto = cache.get(request.user.username)
	if not proyecto:
		return render_to_response('423.html')
	permisos = request.user.permisos
	if permisos.res_see:
			objetosStreaming = Streaming.objects.filter(proyecto_id=proyecto.id,pregunta__abierta = True,respuesta__isnull = False)
			listaPreguntas = []
			datasetgrafo = []
			for i in objetosStreaming:
				if i.pregunta in listaPreguntas:
					indi = listaPreguntas.index(i.pregunta)
					datasetgrafo[indi].append(i.respuesta)
				elif i.pregunta not in listaPreguntas:
					listaPreguntas.append(i.pregunta)
					datasetgrafo.append([i.pregunta,i.respuesta])
			grafoPorPregunta,diccionariosPorPregunta,cantidades = gr.Grafos(datasetgrafo)
			listaPreguntas = gr.preguntas(datasetgrafo)
			return render_to_response('wordanalytics.html',{
				'Activar':'AnalisisResultados',
				'activar':'WordAnalytics',
				'Proyecto':proyecto,
				'Permisos':permisos,
				'activarG':3,
				'activar':'grafos',
				'grafos':grafoPorPregunta,'diccionarios':diccionariosPorPregunta,'cantidades':cantidades,'listaPreguntas':listaPreguntas,
			}, context_instance=RequestContext(request))

	else:
			return render_to_response('403.html')
