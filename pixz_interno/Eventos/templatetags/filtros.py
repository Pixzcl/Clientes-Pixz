from django import template
register = template.Library()

from Eventos.models import *

@register.filter()
def tipo(TrabajadoresEvento, tipo):
	return TrabajadoresEvento.filter(tipo=tipo)

@register.filter()
def itemsEstacion(planEvento, itemPlan):
	try:
### itemsEstacion = []
### itemsPlanEvento = ItemsPlanEvento.objects.filter(PlanesEvento=planEvento, ItemsPlan=itemPlan)
### if not(itemPlan.Item.multiple):
	### for it in itemsPlanEvento:
		### if itemPlan.cantidad > 1:
			### for i in range(1, itemPlan.cantidad + 1):
				### itemsEstacion.append([it.ItemsPlan.Item.nombre + " " + str(i), it.ItemsEstacion.Estacion.nombre])
		### else:
			### ### itemsEstacion.append([it.ItemsPlan.Item.nombre, it.ItemsEstacion.Estacion.nombre])
### else:
	### itemsEstacion.append([itemsPlanEvento[0].ItemsPlan.Item.nombre, itemsPlanEvento[0].ItemsEstacion.Estacion.nombre])
		return ItemsPlanEvento.objects.get(PlanesEvento=planEvento, ItemsPlan=itemPlan).ItemsEstacion.Estacion.nombre
	except (ItemsPlanEvento.DoesNotExist, AttributeError): # (ItemsEstacion no existe o no esta definido en ItemsPlanEvento)
		return None
### no va a pasar mas

@register.filter(name='zip_evento')
def zip_evento(planEvento, logisticaPlanesForm):
	itemsPlan = planEvento.Plan.ItemsPlan.all()
	#itemsPlan = []
	#anterior = ""
	#for itemPlan in planEvento.Plan.ItemsPlan.all():
	#	if itemPlan.Item.multiple and itemPlan.Item.nombre == anterior:
	#		continue
	#	else:
	#		itemsPlan.append(itemPlan)
	#		anterior = itemPlan.Item.nombre
	
	if logisticaPlanesForm == None:
		return zip(itemsPlan, [None]*len(itemsPlan))
	else:
		formSplit = []
		for field in logisticaPlanesForm:
			if ("planEvento_%d" % planEvento.idPlanesEvento) in field.label:
				formSplit.append(field)
		return zip(itemsPlan, formSplit)

@register.filter(name='zip')
def zip_listas(a,b):
	return zip(a,b)