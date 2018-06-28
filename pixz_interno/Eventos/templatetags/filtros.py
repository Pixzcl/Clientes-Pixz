from django import template
register = template.Library()

from Eventos.models import *

@register.filter(name='zip')
def zip_listas(a,b):
	return zip(a,b)

@register.filter()
def cargo(TrabajadoresEvento, cargo):
	return TrabajadoresEvento.filter(Cargo=cargo)

@register.filter()
def tipo(TrabajadoresEvento, tipo):
	return TrabajadoresEvento.filter(tipo=tipo)


