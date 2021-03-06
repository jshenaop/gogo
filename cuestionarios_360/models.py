from __future__ import unicode_literals
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from usuarios.models import Proyectos


class Instrumentos_360( models.Model ):
	id = models.AutoField( primary_key = True )
	estado = models.BooleanField( default = True )
	max_dimensiones = models.PositiveSmallIntegerField( default = 0 )
	max_preguntas = models.PositiveSmallIntegerField( default = 0 )
	nombre =  models.CharField( max_length = 255, db_index = True)
	proyecto = models.ForeignKey( Proyectos, blank = True, null = True )
	zdel = models.DateTimeField( blank = True, null = True )

	def __unicode__(self):
		return self.nombre

	class Meta:
		managed = True
		db_table = 'cuestionarios_360_instrumentos'
		verbose_name_plural = 'Instrumentos 360'


class Dimensiones_360( models.Model ):
	id = models.AutoField( primary_key = True )
	descripcion = models.TextField( blank = True, null = True , max_length = 255 )
	estado = models.BooleanField( default = True )
	instrumento = models.ForeignKey( Instrumentos_360, related_name="dimension", blank = True, null = True )
	max_variables = models.PositiveSmallIntegerField( default = 0 )
	nombre =  models.CharField( max_length = 255 )
	posicion = models.PositiveSmallIntegerField( blank = True, null = True )
	proyecto = models.ForeignKey( Proyectos, blank = True, null = True )
	zdel = models.DateTimeField( blank = True, null = True )

	def __unicode__(self):
		return self.nombre

	class Meta:
		managed = True
		db_table = 'cuestionarios_360_dimensiones'
		verbose_name_plural = 'Dimensiones 360'


class Variables_360( models.Model ):
	id = models.AutoField( primary_key = True )
	descripcion = models.TextField( blank = True, null = True , max_length = 255 )
	dimension = models.ForeignKey( Dimensiones_360, blank = True, null = True )
	estado = models.BooleanField( default = True )
	imagen = models.CharField( default="/static/img/variables/badge.png", max_length = 400 )
	instrumento = models.ForeignKey( Instrumentos_360, blank = True, null = True )
	max_preguntas = models.PositiveSmallIntegerField( default = 0 )
	nombre =  models.CharField( max_length = 255 )
	posicion = models.PositiveSmallIntegerField( blank = True, null = True )
	proyecto = models.ForeignKey( Proyectos, blank = True, null = True )
	zdel = models.DateTimeField( blank = True, null = True )

	def __unicode__(self):
		return self.nombre

	class Meta:
		managed = True
		db_table = 'cuestionarios_360_variables'
		verbose_name_plural = 'Variables 360'


class Preguntas_360( models.Model ):
	id = models.AutoField( primary_key = True )
	abierta = models.BooleanField( default = False )
	cuerpo = models.BooleanField( default = False )
	dimension = models.ForeignKey( Dimensiones_360, blank = True, null = True )
	estado = models.BooleanField( default = True )
	instrumento = models.ForeignKey( Instrumentos_360, blank = True, null = True )
	multiple = models.BooleanField( default = False )
	numerica = models.BooleanField( default = True )
	posicion = models.IntegerField()
	puntaje = models.FloatField( default = 1 )
	texto = models.CharField( max_length = 255 )
	variable = models.ForeignKey( Variables_360,  blank = True, null = True )
	proyecto = models.ForeignKey( Proyectos, blank = True, null = True )
	zdel = models.DateTimeField( blank = True, null = True )

	def __unicode__(self):
		return self.texto

	class Meta:
		managed = True
		db_table = 'cuestionarios_360_preguntas'
		verbose_name_plural = 'Preguntas 360'


class Respuestas_360( models.Model ):
	id = models.AutoField( primary_key = True )
	numerico = models.FloatField( blank = True, null = True )
	pregunta = models.ForeignKey( Preguntas_360 )
	texto = models.CharField( max_length = 255 )

	def __unicode__(self):
		return self.texto

	class Meta:
		managed = True
		db_table = 'cuestionarios_360_respuestas'
		verbose_name_plural = 'Respuestas 360'
