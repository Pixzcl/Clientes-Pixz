from django import template
register = template.Library()

from Eventos.models import ItemsPlanEvento

@register.filter()
def tipo(TrabajadoresEvento, tipo):
	return TrabajadoresEvento.filter(tipo=tipo)

@register.filter()
def itemsEstacion(planEvento, itemPlan):
	try:
		return ItemsPlanEvento.objects.get(PlanesEvento=planEvento, ItemsPlan=itemPlan).ItemsEstacion.Estacion.nombre
	except ItemsPlanEvento.DoesNotExist:
		return None
	except AttributeError: # (ItemsEstacion no definido en ItemsPlanEvento)
		return None

@register.filter(name='zip_evento')
def zip_evento(planEvento, logisticaPlanesForm):
	itemsPlan = planEvento.Plan.ItemsPlan.all()
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