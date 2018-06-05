import os
import datetime
from urllib.parse import urlencode

from django.shortcuts import render, redirect, reverse
#from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from .forms import *
from .models import *

from django.utils.datastructures import MultiValueDictKeyError

#from django.core.files.storage import FileSystemStorage


#def index(request):
#	return render(request, 'index.html')


#def clientes(request):
#	return render(request, 'clientes.html')

def custom_redirect(url_name, *args, **kwargs):
    url = reverse(url_name, args=args)
    params = urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)

def index(request):
	clientes = Clientes.objects.all()
	
	campos = Clientes._meta.get_fields()
	titulos = ["#", "Cliente","Dirección"]
	#titulos = []
	#for campo in campos:
	#	if not("ManyToOneRel" in str(campo.get_internal_type)):
	#		titulos.append(campo.verbose_name.title())
	#		print (campo.verbose_name.title())

	context = {
		"clientes": clientes,
		"titulos": titulos,
	}
	return render(request, 'index.html', context)


def agregar_cliente(request):
	if request.method == 'POST':
		form = ClientesForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('index')
	else:
		form = ClientesForm()
	context = {
		"clientes_form": form,
	}
	return render(request, 'agregar_cliente.html', context)


def activaciones(request):
	try:
		idCliente = request.GET['cliente']
		cliente = Clientes.objects.get(idCliente=idCliente)
		activaciones = Activaciones.objects.filter(Cliente=cliente)
		titulos = ["#","Activación", "Descripción"]
		contactos = cliente.Contactos.all()
		titulos_contactos = ["#", "Nombre", "Teléfono", "Mail"]
	except MultiValueDictKeyError:
		idCliente = ""
		cliente = ""
		activaciones = Activaciones.objects.all()
		titulos = ["#", "Cliente","Activación", "Descripción"]
		contactos = None
		titulos_contactos = None
	
	#campos = Activaciones._meta.get_fields()
	#titulos = []
	#for campo in campos:
	#	if not("ManyToOneRel" in str(campo.get_internal_type)):
	#		if not(campo.verbose_name.title() == "Cliente" and cliente != ""):
	#			titulos.append(campo.verbose_name.title())
	#			print (campo.verbose_name.title())

	pendientes = []
	for activacion in activaciones:
		if activacion.Eventos.filter(fecha__gte=datetime.date.today()).count() > 0:
			pendientes.append(activacion)

	context = {
		"activaciones": activaciones,
		"titulos": titulos,
		"titulos_contactos": titulos_contactos,
		"pendientes": len(pendientes),
		"cliente": cliente,
		"contactos": contactos,
	}
	return render(request, 'activaciones.html', context)


def agregar_activacion(request):
	if request.method == 'POST':
		try:
			int(request.POST['Cliente']) # (probar si viene de SelectForm o no)
			idCliente = request.POST['Cliente']
			cliente = Clientes.objects.get(idCliente=idCliente)
			form = ActivacionesForm(request.POST, request.FILES)
		except:
			cliente = request.POST['Cliente']
			idCliente = cliente.idCliente
			form = ActivacionesSelectForm(request.POST, request.FILES)

		if form.is_valid():
			a = form.save(commit=False)
			a.Cliente = Clientes.objects.get(idCliente=idCliente)
			form.save()
			return custom_redirect('activaciones', cliente=idCliente)
	
	else:
		try:
			idCliente = request.GET['cliente']
			cliente = Clientes.objects.get(idCliente=idCliente)
			form = ActivacionesForm()
		except MultiValueDictKeyError:
			cliente = ""
			form = ActivacionesSelectForm()

	context = {
		"activaciones_form": form,
		"cliente": cliente,
	}
	return render(request, 'agregar_activacion.html', context)


def eventos(request):
	#try:
	#	idCliente = request.GET['cliente']
	#except MultiValueDictKeyError:
	#	idCliente = ""
	#	cliente = ""
	try:
		idActivacion = request.GET['activacion']
		activacion = Activaciones.objects.get(idActivacion=idActivacion)
		eventos = activacion.Eventos.all()
		cliente = activacion.Cliente
		titulos = ["#", "Fecha", "Horas", "Plan(es)", "Comentarios"]
	except MultiValueDictKeyError:
		idActivacion = ""
		activacion = ""
		eventos = Eventos.objects.all()
		cliente = ""
		titulos = ["#", "Cliente","Activación", "Fecha", "Horas", "Plan(es)", "Comentarios"]

	#if idActivacion == "":
	#	if idCliente == "":
	#		eventos = Eventos.objects.all()
	#	else:
	#		# todos los eventos del cliente:
	#		# quizas no sea necesario este caso
	#		cliente = Clientes.objects.get(idCliente=idCliente)
	#		activaciones = Activaciones.objects.filter(Cliente=cliente)
	#		eventos = Eventos.objects.filter(Activacion=activaciones[0])
	#		if activaciones.count() > 1:
	#			for activacion in activaciones[1:]:
	#				eventos = eventos_list | Eventos.objects.filter(idActivacion=activacion.idActivacion)
	#else:
	#	activacion = Activaciones.objects.get(idActivacion=idActivacion)
	#	eventos = Eventos.objects.filter(idActivacion=idActivacion)
	#	if idCliente == "":
	#		cliente = activacion.idCliente
	#	else:
	#		cliente = Clientes.objects.get(idCliente=idCliente)

	context = {
		"cliente": cliente,
		"activacion": activacion,
		"titulos": titulos,
		"pendientes": eventos.filter(fecha__gte=datetime.date.today()),
		"eventos": eventos,
	}
	return render(request, 'eventos.html', context)


def agregar_evento(request):
	if request.method == 'POST':
		nPlanes = int(request.POST['nPlanes'])

		try:
			int(request.POST['activacion']) # (probar si viene de SelectForm o no)
			idActivacion = request.POST['activacion']
			activacion = Activaciones.objects.get(idActivacion=idActivacion)
			form = EventosForm(nPlanes, request.POST, request.FILES)
		except:
			activacion = request.POST['activacion']
			idActivacion = activacion.idActivacion
			form = EventosSelectForm(nPlanes, request.POST, request.FILES)
		
		
		
		if form.is_valid():
			evento = Eventos(Activacion=activacion)
			#datetime.date(1943,3, 13)  #year, month, day
			evento.fecha = datetime.date(int(request.POST['fecha_year']), int(request.POST['fecha_month']), int(request.POST['fecha_day']))  #year, month, day
			evento.horas = request.POST['horas']
			evento.comentarios = request.POST['comentarios']
			evento.save()

			planes = []
			for key, value in request.POST.items():
				#print("key:", key)
				if "plan_" in key:
					planes.append(Planes.objects.get(idPlan=value))
			for plan in planes:
				planEvento = PlanesEvento(Evento=evento, Plan=plan)
				planEvento.save()

			#return redirect('eventos')
			return custom_redirect('eventos', activacion=idActivacion)
	
	else:
		try:
			nPlanes = int(request.GET['nPlanes'])
		except MultiValueDictKeyError:
			nPlanes = 1

		try:
			idActivacion = request.GET['activacion']
			activacion = Activaciones.objects.get(idActivacion=idActivacion)
			form = EventosForm(nPlanes)
		except MultiValueDictKeyError:
			activacion = ""
			form = EventosSelectForm(nPlanes)

	
	context = {
		"eventos_form": form,
		"activacion": activacion,
		"nPlanes": nPlanes,
	}
	return render(request, 'agregar_evento.html', context)


def editar_evento(request):
	if request.method == 'POST':
		nPlanes = int(request.POST['nPlanes'])
		form = EventosForm(nPlanes, request.POST, request.FILES)
		idActivacion = request.POST['activacion']
		#for key, value in request.POST.items():
		#	print(key)
		if form.is_valid():
			activacion = Activaciones.objects.get(idActivacion=idActivacion)
			evento = Eventos(Activacion=activacion)
			#datetime.date(1943,3, 13)  #year, month, day
			evento.fecha = datetime.date(int(request.POST['fecha_year']), int(request.POST['fecha_month']), int(request.POST['fecha_day']))  #year, month, day
			evento.horas = request.POST['horas']
			evento.comentarios = request.POST['comentarios']
			evento.save()

			planes = []
			for key, value in request.POST.items():
				#print("key:", key)
				if "plan_" in key:
					planes.append(Planes.objects.get(idPlan=value))
			for plan in planes:
				planEvento = PlanesEvento(Evento=evento, Plan=plan)
				planEvento.save()

			#return redirect('eventos')
			return custom_redirect('eventos', activacion=idActivacion)
	else:
		try:
			nPlanes = int(request.GET['nPlanes'])
		except MultiValueDictKeyError:
			nPlanes = 1
		form = EventosForm(nPlanes)
		#for field in form:
		#	print(field)
		idActivacion = request.GET['activacion']

	activacion = Activaciones.objects.get(idActivacion=idActivacion)
	context = {
		"eventos_form": form,
		"cliente": activacion.Cliente,
		"activacion": activacion,
		"nPlanes": nPlanes,
	}
	return render(request, 'agregar_evento.html', context)


def eliminar_evento(request):
	if request.method == 'POST':
		nPlanes = int(request.POST['nPlanes'])
		form = EventosForm(nPlanes, request.POST, request.FILES)
		idActivacion = request.POST['activacion']
		#for key, value in request.POST.items():
		#	print(key)
		if form.is_valid():
			activacion = Activaciones.objects.get(idActivacion=idActivacion)
			evento = Eventos(Activacion=activacion)
			#datetime.date(1943,3, 13)  #year, month, day
			evento.fecha = datetime.date(int(request.POST['fecha_year']), int(request.POST['fecha_month']), int(request.POST['fecha_day']))  #year, month, day
			evento.horas = request.POST['horas']
			evento.comentarios = request.POST['comentarios']
			evento.save()

			planes = []
			for key, value in request.POST.items():
				#print("key:", key)
				if "plan_" in key:
					planes.append(Planes.objects.get(idPlan=value))
			for plan in planes:
				planEvento = PlanesEvento(Evento=evento, Plan=plan)
				planEvento.save()

			#return redirect('eventos')
			return custom_redirect('eventos', activacion=idActivacion)
	else:
		try:
			nPlanes = int(request.GET['nPlanes'])
		except MultiValueDictKeyError:
			nPlanes = 1
		form = EventosForm(nPlanes)
		#for field in form:
		#	print(field)
		idActivacion = request.GET['activacion']

	activacion = Activaciones.objects.get(idActivacion=idActivacion)
	context = {
		"eventos_form": form,
		"cliente": activacion.Cliente,
		"activacion": activacion,
		"nPlanes": nPlanes,
	}
	return render(request, 'agregar_evento.html', context)


def planes(request):
	planes = Planes.objects.all()
	
	titulos = ["#", "Plan", "Items"]

	context = {
		"planes": planes,
		"titulos": titulos,
	}
	return render(request, 'planes.html', context)


def agregar_plan(request):
	nombre_unico = True
	if request.method == 'POST':
		nItems = int(request.POST['nItems'])
		form = PlanesForm(nItems, request.POST, request.FILES)
		#form = PlanesForm2(request.POST, request.FILES)
		print (len(request.POST))
		count = 0
		for key, value in request.POST.items():
			if "item_" in key:
				count += 1
		if form.is_valid() and count == int(nItems):
			# verificar uniqueness
			planes = Planes.objects.all()
			for p in planes:
				if p.nombre == request.POST['nombre']:
					nombre_unico = False
			if nombre_unico == True:
				plan = Planes(nombre=request.POST['nombre'])
				#plan.nombre = request.POST['nombre']
				plan.save()

				items = []
				for key, value in request.POST.items():
					if "item_" in key:
						items.append(Items.objects.get(idItem=value))
				for item in items:
					itemsPlan = ItemsPlan(Plan=plan, Item=item)
					itemsPlan.save()

				return redirect('planes')
	else:
		try:
			nItems = int(request.GET['nItems'])
		except MultiValueDictKeyError:
			nItems = 1
		form = PlanesForm(nItems)
		#form = PlanesForm2()
	context = {
		"planes_form": form,
		"nItems": nItems,
		"nombre_unico": nombre_unico,
	}
	return render(request, 'agregar_plan.html', context)


def estaciones(request):
	estaciones = Estaciones.objects.all()
	
	titulos = ["#", "Estación", "Items"]

	context = {
		"estaciones": estaciones,
		"titulos": titulos,
	}
	return render(request, 'estaciones.html', context)


def agregar_estacion(request):
	nombre_unico = True
	if request.method == 'POST':
		nItems = int(request.POST['nItems'])
		form = EstacionesForm(nItems, request.POST, request.FILES)

		if form.is_valid():
			# verificar uniqueness
			estaciones = Estaciones.objects.all()
			for e in estaciones:
				if e.nombre == request.POST['nombre']:
					nombre_unico = False
			if nombre_unico == True:
				estacion = Estaciones(nombre=request.POST['nombre'])
				#estacion.nombre = request.POST['nombre']
				estacion.save()

				items = []
				for key, value in request.POST.items():
					if "item_" in key:
						items.append(Items.objects.get(idItem=value))
				for item in items:
					itemsEstacion = ItemsEstacion(Estacion=estacion, Item=item)
					itemsEstacion.save()

				return redirect('estaciones')
	else:
		try:
			nItems = int(request.GET['nItems'])
		except MultiValueDictKeyError:
			nItems = 1
		form = EstacionesForm(nItems)
	context = {
		"estaciones_form": form,
		"nItems": nItems,
		"nombre_unico": nombre_unico,
	}
	return render(request, 'agregar_estacion.html', context)


def items(request):
	items = Items.objects.all()
	
	titulos = ["#", "Item"]

	context = {
		"items": items,
		"titulos": titulos,
	}
	return render(request, 'items.html', context)


def agregar_item(request):
	if request.method == 'POST':
		form = ItemsForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('items')
	else:
		form = ItemsForm()
	context = {
		"items_form": form,
	}
	return render(request, 'agregar_item.html', context)


def trabajadores(request):
	trabajadores = Trabajadores.objects.all()
	
	titulos = ["#", "Nombre", "RUT", "Teléfono", "Mail"]

	context = {
		"trabajadores": trabajadores,
		"titulos": titulos,
	}
	return render(request, 'trabajadores.html', context)


def agregar_trabajador(request):
	if request.method == 'POST':
		form = TrabajadoresForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('trabajadores')
	else:
		form = TrabajadoresForm()
	context = {
		"trabajadores_form": form,
	}
	return render(request, 'agregar_trabajador.html', context)


def contactos(request):
	contactos = Contactos.objects.all()
	
	titulos = ["#", "Nombre", "Cliente", "RUT", "Teléfono", "Mail"]

	context = {
		"contactos": contactos,
		"titulos": titulos,
	}
	return render(request, 'contactos.html', context)


def agregar_contacto(request):
	if request.method == 'POST':
		form = ContactosForm(request.POST, request.FILES)
		if form.is_valid():
			idCliente = request.POST['cliente']
			e = form.save(commit=False)
			e.Cliente = Clientes.objects.get(idCliente=idCliente)
			form.save()
			return custom_redirect('activaciones', cliente=idCliente)
	else:
		try:
			idCliente = request.GET['cliente']
			cliente = Clientes.objects.get(idCliente=idCliente)
			form = ContactosForm(initial={"Cliente": cliente})
		except MultiValueDictKeyError:
			return redirect('index')
	context = {
		"contactos_form": form,
		"cliente": cliente,
	}
	return render(request, 'agregar_contacto.html', context)

def agregar_contacto_select(request):
	if request.method == 'POST':
		form = ContactosFormSelect(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('contactos')
	else:
		form = ContactosFormSelect()
	context = {
		"contactos_form": form,
		"cliente": None,
	}
	return render(request, 'agregar_contacto.html', context)


def evento(request):
	error = False
	if request.method == 'POST':
		idEvento = request.POST['evento']
		evento = Eventos.objects.get(idEvento=idEvento)
		activacion = evento.Activacion
		cliente = activacion.Cliente

		coordinacion_form = None
		logistica_form = None
		logistica_planes_form = None
		edit = request.POST['edit']
		tab = None
		if edit == "coordinacion":
			coordinacion_form = CoordinacionForm(request.POST, request.FILES)
			if coordinacion_form.is_valid():
				
				contacto = request.POST['Contacto']
				if contacto == "":
					evento.Contacto = None
				else:
					Contacto = cliente.Contactos.get(idContacto=contacto)
					if Contacto != evento.Contacto:
						evento.Contacto = Contacto

				#datetime.date(1943,3, 13)  #year, month, day
				#if (request.POST['fecha_instalacion_year'] != "0" and request.POST['fecha_instalacion_month'] != "0" and request.POST['fecha_instalacion_day'] != "0"):
				evento.fecha_instalacion = datetime.date(int(request.POST['fecha_instalacion_year']), int(request.POST['fecha_instalacion_month']), int(request.POST['fecha_instalacion_day']))  #year, month, day
				#if (request.POST['fecha_desinstalacion_year'] != "0" and request.POST['fecha_desinstalacion_month'] != "0" and request.POST['fecha_desinstalacion_day'] != "0"):
				evento.fecha_desinstalacion = datetime.date(int(request.POST['fecha_desinstalacion_year']), int(request.POST['fecha_desinstalacion_month']), int(request.POST['fecha_desinstalacion_day']))  #year, month, day
				
				hora_instalacion = request.POST['hora_instalacion']
				if hora_instalacion == "":
					hora_instalacion = None
				if hora_instalacion != evento.hora_instalacion:
					evento.hora_instalacion = hora_instalacion

				hora_desinstalacion = request.POST['hora_desinstalacion']
				if hora_desinstalacion == "":
					hora_desinstalacion = None
				if hora_desinstalacion != evento.hora_desinstalacion:
					evento.hora_desinstalacion = hora_desinstalacion

				inicio_servicio = request.POST['inicio_servicio']
				if inicio_servicio == "":
					inicio_servicio = None
				if inicio_servicio != evento.inicio_servicio:
					evento.inicio_servicio = inicio_servicio
				
				fin_servicio = request.POST['fin_servicio']
				if fin_servicio == "":
					fin_servicio = None
				if fin_servicio != evento.fin_servicio:
					evento.fin_servicio = fin_servicio

				evento.direccion = request.POST['direccion']
				evento.save()
				return custom_redirect('evento', evento=idEvento)
			else:
				error = True

		elif edit == "logistica":
			logistica_form = LogisticaTrabajadoresForm(request.POST, request.FILES)
			logistica_planes_form = LogisticaPlanesForm(evento.PlanesEvento.all(), request.POST, request.FILES)
			if logistica_form.is_valid() and logistica_planes_form.is_valid():
			# Trabajadores
				tipos = ["Supervisor", "Montaje", "Desmontaje", "Operador"]
				for tipo in tipos:
					try:
						idTrabajadores = request.POST.getlist(tipo)
						trabajadores = Trabajadores.objects.filter(idTrabajador__in=idTrabajadores)
					except MultiValueDictKeyError:
						continue # trabajadores = []

					trabajadoresEvento_actuales = evento.TrabajadoresEvento.filter(tipo=tipo)
					for trabajadorEvento_actual in trabajadoresEvento_actuales:
						if trabajadorEvento_actual.Trabajador not in trabajadores:
							#print(supervisor_actual.Trabajador.nombre)
							trabajadorEvento_actual.delete()

					for trabajador in trabajadores:
						if trabajador not in [trabajadorEvento_actual.Trabajador for trabajadorEvento_actual in trabajadoresEvento_actuales]:
							TrabajadoresEvento(Evento=evento, Trabajador=trabajador, tipo=tipo).save()
			
			# Planes
				for key, value in request.POST.items():
					if "_" in key:
						split = key.split("_")
						planEvento = PlanesEvento.objects.get(idPlanesEvento=split[1])
						itemPlan = ItemsPlan.objects.get(idItemsPlan=split[3])
						if value == "":
							itemEstacion = None
						else:
							itemEstacion = ItemsEstacion.objects.get(idItemsEstacion=value)

						try:
							itemPlanEvento = ItemsPlanEvento.objects.get(PlanesEvento=planEvento, ItemsPlan=itemPlan)
							itemPlanEvento.ItemsEstacion = itemEstacion
						except ItemsPlanEvento.DoesNotExist:
							itemPlanEvento = ItemsPlanEvento(PlanesEvento=planEvento, ItemsPlan=itemPlan, ItemsEstacion=itemEstacion)
						itemPlanEvento.save()

				#evento.save()
				return custom_redirect('evento', evento=idEvento, tab="logistica")
			else:
				error = True

	# GET				
	else:
		try:
			idEvento = request.GET['evento']
			evento = Eventos.objects.get(idEvento=idEvento)
			activacion = evento.Activacion
			cliente = activacion.Cliente
		except MultiValueDictKeyError:
			return redirect('eventos')
		try:
			coordinacion_form = None
			logistica_form = None
			logistica_planes_form = None
			edit = request.GET['edit']
			if edit == "coordinacion":
				coordinacion_form = CoordinacionForm(initial={
					"Contacto":evento.Contacto, 
					"inicio_servicio":evento.inicio_servicio, 
					"fin_servicio":evento.fin_servicio, 
					"fecha_instalacion":evento.fecha_instalacion, 
					"hora_instalacion":evento.hora_instalacion, 
					"fecha_desinstalacion":evento.fecha_desinstalacion, 
					"hora_desinstalacion":evento.hora_desinstalacion, 
					"direccion":evento.direccion
					})
			elif edit == "logistica":
				logistica_form = LogisticaTrabajadoresForm(initial={
					"Supervisor":[trabajadorEvento.Trabajador.idTrabajador for trabajadorEvento in evento.TrabajadoresEvento.filter(tipo="Supervisor")], 
					"Montaje":[trabajadorEvento.Trabajador.idTrabajador for trabajadorEvento in evento.TrabajadoresEvento.filter(tipo="Montaje")], 
					"Desmontaje":[trabajadorEvento.Trabajador.idTrabajador for trabajadorEvento in evento.TrabajadoresEvento.filter(tipo="Desmontaje")], 
					"Operador":[trabajadorEvento.Trabajador.idTrabajador for trabajadorEvento in evento.TrabajadoresEvento.filter(tipo="Operador")]
					})

				initial = {}
				planesEvento = evento.PlanesEvento.all()
				for planEvento in planesEvento:
					for itemPlan in planEvento.Plan.ItemsPlan.all():
						try:
							init = ItemsPlanEvento.objects.get(PlanesEvento=planEvento, ItemsPlan=itemPlan).ItemsEstacion.idItemsEstacion
						except ItemsPlanEvento.DoesNotExist:
							init = None
						except AttributeError: # (ItemsEstacion no definido en ItemsPlanEvento)
							init = None
						initial['planEvento_%d_itemPlan_%d' % (planEvento.idPlanesEvento, itemPlan.idItemsPlan)] = init
				logistica_planes_form = LogisticaPlanesForm(planesEvento, initial=initial)

		except MultiValueDictKeyError:
			edit = False
		try:
			tab = request.GET['tab']
		except MultiValueDictKeyError:
			tab = "coordinacion"

		#itemsPlanEvento = ItemsPlanEvento.objects.filter(PlanesEvento__in=evento.PlanesEvento.all(), ItemsPlan__in=evento.Planes.)

	context = {
		"cliente": cliente,
		"activacion": activacion,
		"evento": evento,
		"edit": edit,
		"coordinacion_form": coordinacion_form,
		"logistica_form": logistica_form,
		"logistica_planes_form": logistica_planes_form,
		"error": error,
		"tab": tab,
	}
	return render(request, 'evento.html', context)










# Sufee Admin
def charts_chartjs(request):
	return render(request, 'SufeeAdmin/charts_chartjs.html')
def charts_flot(request):
	return render(request, 'SufeeAdmin/charts_flot.html')
def charts_peity(request):
	return render(request, 'SufeeAdmin/charts_peity.html')
def dashboard(request):
	return render(request, 'SufeeAdmin/dashboard.html')
def font_fontawesome(request):
	return render(request, 'SufeeAdmin/font_fontawesome.html')
def font_themify(request):
	return render(request, 'SufeeAdmin/font_themify.html')
def forms_advanced(request):
	return render(request, 'SufeeAdmin/forms_advanced.html')
def forms_basic(request):
	return render(request, 'SufeeAdmin/forms_basic.html')
def maps_gmap(request):
	return render(request, 'SufeeAdmin/maps_gmap.html')
def maps_vector(request):
	return render(request, 'SufeeAdmin/maps_vector.html')
def page_login(request):
	return render(request, 'SufeeAdmin/page_login.html')
def page_register(request):
	return render(request, 'SufeeAdmin/page_register.html')
def pages_forget(request):
	return render(request, 'SufeeAdmin/pages_forget.html')
def tables_basic(request):
	return render(request, 'SufeeAdmin/tables_basic.html')
def tables_data(request):
	return render(request, 'SufeeAdmin/tables_data.html')
def ui_alerts(request):
	return render(request, 'SufeeAdmin/ui_alerts.html')
def ui_badges(request):
	return render(request, 'SufeeAdmin/ui_badges.html')
def ui_buttons(request):
	return render(request, 'SufeeAdmin/ui_buttons.html')
def ui_cards(request):
	return render(request, 'SufeeAdmin/ui_cards.html')
def ui_grids(request):
	return render(request, 'SufeeAdmin/ui_grids.html')
def ui_modals(request):
	return render(request, 'SufeeAdmin/ui_modals.html')
def ui_progressbar(request):
	return render(request, 'SufeeAdmin/ui_progressbar.html')
def ui_social_buttons(request):
	return render(request, 'SufeeAdmin/ui_social_buttons.html')
def ui_switches(request):
	return render(request, 'SufeeAdmin/ui_switches.html')
def ui_tabs(request):
	return render(request, 'SufeeAdmin/ui_tabs.html')
def ui_typgraphy(request):
	return render(request, 'SufeeAdmin/ui_typgraphy.html')
def widgets(request):
	return render(request, 'SufeeAdmin/widgets.html')



#customer_id = request.POST["id"]

# def blog_upload(request):
#     if request.method == 'POST':
#         form = BlogForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('blog')
#     else:
#         form = BlogForm()
#     context = {
#         "blog_form": form
#     }
#     return render(request, 'blog_upload.html', context)

# def delete_blog(request):
#     checks = request.POST["checks_form"]
#     checks = checks.split(',')

#     for i in range(len(checks)):
#         #if pics_check[i] != '':
#         blog = Blog.objects.get(id_int=checks[i])
			
#         path = settings.MEDIA_ROOT + "/" + str(blog.Foto)
#         print (path)
#         if os.path.isfile(path):
#             os.remove(path)
#         blog.delete()
		
#     return redirect('blog')

