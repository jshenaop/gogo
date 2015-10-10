#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os,django
import sys
sys.path.append('/home/ubuntu/gogo/')
sys.path.append('/home/ubuntu/gogo/gogo/')
sys.path.append('/home/suidi/codigo/gogo/')
sys.path.append('/home/suidi/codigo/gogo/gogo/')
os.environ["DJANGO_SETTINGS_MODULE"] ="gogo.settings"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '+xtgn6s8(15e#nv)1v5ta7n)*fpt=xq7+gt5o_28$8lzg3=ccm'
django.setup()
DEBUG = False
INSTALLED_APPS = ('analisis','colaboradores','cuestionarios','mensajeria','usuarios','mptt',)
DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql','NAME': 'gogo','USER': 'suidi','PASSWORD':'Su1357*-','HOST':'nwl.co3mxnuop6eu.us-east-1.rds.amazonaws.com','PORT':'3306'}}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
LANGUAGE_CODE = 'es-CO'
TIME_ZONE = 'America/Bogota'

from colaboradores.models import *
from mensajeria.corrector import salvar_html
from mensajeria.models import *
from usuarios.strings import *
from django.db import transaction
from datetime import datetime,timedelta
from django.utils import timezone
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
import smtplib,cgi,unicodedata

from django.db import models
server=smtplib.SMTP('smtp.mandrillapp.com',587)
server.ehlo()
server.starttls()
server.login('Team@goanalytics.com','pR6yG1ztNHT7xW6Y8yigfw')

def sendmail(stream_i):
	# try
	colaborador = stream_i.colaborador
	desde="Team@goanalytics.com"
	destinatario = colaborador.email
	msg=MIMEMultipart()
	urlimg = 'http://www.lavozdemisclientes.com'+stream_i.proyecto.proyectosdatos.logo.url
	if colaborador.colaboradoresdatos.genero.lower() == "femenino" :
		genero = "a"
	else:
		genero = "o"
	nombre = cgi.escape(colaborador.nombre).encode("ascii", "xmlcharrefreplace")
	titulo = cgi.escape(stream_i.proyecto.proyectosdatos.tit_encuesta).encode("ascii", "xmlcharrefreplace")
	url = 'http://www.lavozdemisclientes.com/encuesta/'+str(stream_i.proyecto.id)+'/'+colaborador.key
	texto_correo = salvar_html(cgi.escape(stream_i.proyecto.proyectosdatos.cue_correo).encode("ascii", "xmlcharrefreplace"))
	msg["subject"]=  unicodedata.normalize('NFKD', stream_i.proyecto.proyectosdatos.tit_encuesta).encode('ascii','ignore')
	msg['From'] = email.utils.formataddr(('GoAnalitycs', 'Team@goanalytics.com'))
	html = correo_standar(urlimg,genero,nombre,titulo,texto_correo,url)
	parte2=MIMEText(html,"html")
	msg.attach(parte2)
	server.sendmail('Team@goanalytics.com',destinatario,msg.as_string())
	with transaction.atomic():
		colaborador.enviados =+1
		colaborador.save()
	print 'Enviado.'
	# except:
	# 	pass

def actualizar(i,stream,tiempo):
	for j in stream:
		if j.colaborador_id == i.colaborador_id:
			j.fec_controlenvio = tiempo
	Streaming.objects.filter(colaborador=i.colaborador,proyecto=i.proyecto).update(fec_controlenvio=tiempo)
	return stream

def enviar():
	stream = Streaming.objects.select_related('colaborador__colaboradoresdatos',
			'proyecto__proyectosdatos').filter(
			fecharespuesta__isnull=True,proyecto__activo =True,
			colaborador__estado=True,pregunta__estado=True)
	lens = len(stream)
	tiempo = timezone.now()
	for i in xrange(lens):
		if not stream[i].fec_controlenvio:#no se ha enviado?
			sendmail(stream[i])
			stream = actualizar(stream[i],stream,tiempo)
			# print 'A:',stream[i].colaborador.email,' se le ha enviado por primera vez'
		else:
			delta = tiempo - stream[i].fec_controlenvio
			if stream[i].colaborador.propension:
				propension = stream[i].colaborador.propension - 0.83 #calibrador para que no se mueva a derecha
				if ( delta.days >= stream[i].proyecto.prudenciamin and delta.days >= propension ):  # x > p > m
					sendmail(stream[i])
					stream = actualizar(stream[i],stream,tiempo)
					# print stream[i].colaborador.email,' respondio se le ha enviado nuevamente en bajo lapsus'
				elif ( delta.days <= stream[i].proyecto.prudenciamax and delta.days >= propension ): # M > x > p
					sendmail(stream[i])
					stream = actualizar(stream[i],stream,tiempo)
					# print stream[i].colaborador.email,' respondio se le ha enviado nuevamente en medio lapsus'
				elif delta.days >= stream[i].proyecto.prudenciamax: # x > M con propension
					sendmail(stream[i])
					stream = actualizar(stream[i],stream,tiempo)
					# print stream[i].colaborador.email,' respondio se le ha enviado nuevamente en alto lapsus'
			elif delta.days >= stream[i].proyecto.prudenciamax: # x > M sin propension
					sendmail(stream[i])
					stream = actualizar(stream[i],stream,tiempo)
					# print stream[i].colaborador.email,' respondio se le ha enviado nuevamente en alto lapsus'
enviar()
server.quit()
print 'Finalizado'