from __future__ import unicode_literals
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey


class Empresas( models.Model ):
	id = models.AutoField( primary_key = True )
	departamento =  models.CharField(  max_length = 100 , blank = True, null = True )
	nit = models.CharField(  max_length = 20 , blank = True, null = True )
	nombre = models.CharField( max_length = 100 )
	num_empleados =  models.IntegerField( blank= True, null = True )
	pagina = models.CharField( max_length=1000, blank= True, null = True )
	pais =  models.CharField(  max_length = 100 , blank = True, null = True )
	sector = models.CharField(  max_length = 100, blank = True, null = True )
	usuario = models.ForeignKey( User )

	def __unicode__(self):
		return self.nombre

	class Meta:
		managed = True
		db_table = 'usuarios_empresas'
		verbose_name_plural = 'Empresas'


class Proyectos( models.Model ):
	id = models.AutoField( primary_key=True )
	activo = models.BooleanField( default = False )
	can_envio = models.IntegerField( default = 5 )
	descripcion = models.TextField( blank = True, null = True )
	empresa = models.ForeignKey( Empresas )
	fec_registro =  models.DateTimeField( auto_now_add = True )
	iniciable = models.BooleanField( default = False )
	nombre =  models.CharField( max_length = 255 )
	prudenciamax = models.IntegerField( default = 2 )
	prudenciamin = models.IntegerField( default = 1 )
	max_variables = models.PositiveSmallIntegerField( default = 0 )
	usuarios = models.ManyToManyField( User )

	def __unicode__(self):
		return self.nombre

	class Meta:
		managed = True
		db_table = 'cuestionarios_proyectos'
		verbose_name_plural = 'Proyectos'


class ProyectosDatos( models.Model ):
	id = models.OneToOneField( Proyectos, primary_key = True )
	cue_correo = models.TextField( blank = True, null = True )
	fregistro = models.DateField( auto_now_add = True )
	int_encuesta = models.TextField( blank = True, null = True )
	logo = models.ImageField( upload_to = 'logos' )
	logoenc = models.ImageField( upload_to = 'logos', blank = True, null = True )
	senso = models.BooleanField( default = False )
	tipo = models.IntegerField( blank = True, null = True )
	tit_encuesta = models.CharField( max_length = 255, blank = True, null = True )

	def __unicode__(self):
		return self.nombre

	class Meta:
		managed = True
		db_table = 'cuestionarios_proyectosdatos'
		verbose_name_plural = "Proyectos datos"


class Permisos( models.Model ):
	id = models.OneToOneField( User, primary_key = True )
	consultor = models.BooleanField( default = True )
	cre_usuarios = models.BooleanField( default = False )
	act_surveys = models.BooleanField( default = False )
	act_variables = models.BooleanField( default = True )
	col_add = models.BooleanField( default = True )#colaboradores
	col_del = models.BooleanField( default = True )
	col_edit = models.BooleanField( default = True )
	col_see = models.BooleanField( default = True )
	det_see = models.BooleanField( default = True )#respuestas detalladas
	pre_add = models.BooleanField( default = True )#preguntas
	pre_del = models.BooleanField( default = True )
	pre_edit = models.BooleanField( default = True )
	pre_see = models.BooleanField( default = True )
	pro_add = models.BooleanField( default = True )#proyectos
	pro_del = models.BooleanField( default = True )
	pro_edit = models.BooleanField( default = True )
	pro_see = models.BooleanField( default = True )
	res_exp = models.BooleanField( default = True )#exportar resultados
	res_see = models.BooleanField( default = True )#graficas
	var_add = models.BooleanField( default = True )#variables
	var_del = models.BooleanField( default = True )
	var_edit = models.BooleanField( default = True )
	var_see = models.BooleanField( default = True )

	def __unicode__(self):
		return '%s'%(self.id)

	class Meta:
		managed = True
		db_table = 'usuarios_permisos'
		verbose_name_plural = 'Permisos'


class IndiceUsuarios( MPTTModel ):
	id = models.AutoField( primary_key = True )
	usuario =  models.OneToOneField( User )
	name = models.CharField( max_length = 100, db_index=True )
	parent = TreeForeignKey('self', null=True, blank = True )

	def __unicode__( self ):
		return '%s' %(self.name)

	class MPTTMeta:
		order_insertion_by = ['name']

	class Meta:
		managed = True
		db_table = "usuarios_indice"
		verbose_name_plural = "Indice de usuarios"


class Recuperar( models.Model ):
	id_envio = models.AutoField( primary_key=True )
	usuario = models.ForeignKey( User )
	link = models.CharField( max_length = 96 )
	fregistro = models.DateTimeField( auto_now_add = True )

	def __unicode__(self):
		return '%s'%self.usuario

	class Meta:
		managed = True
		db_table = 'usuarios_recuperar'
		verbose_name_plural = 'Recuperar'
