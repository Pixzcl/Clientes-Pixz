from django import template
register = template.Library()

from Eventos.models import *
from datetime import date

@register.filter(name='zip')
def zip_listas(a,b):
	return zip(a,b)

@register.filter()
def cargo(TrabajadoresEvento, cargo):
	return TrabajadoresEvento.filter(Cargo=Cargos.objects.get(nombre=cargo))

@register.filter()
def tipo(TrabajadoresEvento, tipo):
	return TrabajadoresEvento.filter(tipo=tipo)

@register.filter()
def facturado(activacion):
	suma = 0
	for factura in activacion.Facturas.all():
		suma += factura.monto
	if suma == activacion.monto:
		return "Si"
	elif suma < activacion.monto:
		return "No"
	elif suma > activacion.monto:
		return "Error"

@register.filter()
def pagado(activacion):
	suma = 0
	for ingreso in activacion.Ingresos.all():
		suma += ingreso.monto
	if suma == activacion.montoIVA:
		return "Si"
	elif suma < activacion.montoIVA:
		return "No"
	elif suma > activacion.montoIVA:
		return "Error"

@register.filter()
def atrasado(activacion):
	atrasado = "No"
	hoy = date.today()
	for factura in activacion.Facturas.all():
		if factura.fecha_pago < hoy:
			atrasado = "Si"
			break
	return atrasado


