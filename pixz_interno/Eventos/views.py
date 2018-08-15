import os, ast
from datetime import date, timedelta, datetime
import ast
from urllib.parse import urlencode

from django.shortcuts import render, redirect, reverse
#from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from django.views.generic.list import ListView

from .models import *
import sys
if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
	from .forms import *
#try:
#	for cliente in Clientes.objects.all():
#		print (cliente.nombre)
#	print ("Ok")
#	from .forms import *
#except:
#	print ("No tables")



from django.utils.datastructures import MultiValueDictKeyError

#from django.core.files.storage import FileSystemStorage





def custom_redirect(url_name, *args, **kwargs):
	url = reverse(url_name, args=args)
	params = urlencode(kwargs)
	return HttpResponseRedirect(url + "?%s" % params)


def index(request):
	eventos = Eventos.objects.all()
	errores = Errores.objects.all()
	satisfaccion = [eventos.filter(satisfaccion=5), eventos.filter(satisfaccion=4), eventos.filter(satisfaccion=3), eventos.filter(satisfaccion=2), eventos.filter(satisfaccion=1)]
	evaluados = 0.0
	for s in satisfaccion:
		evaluados += s.count()

	semanas1 = eventos.filter(fecha__gte=date.today(), fecha__lte=date.today()+timedelta(weeks=1)).order_by("fecha")
	semanas2 = eventos.filter(fecha__gte=date.today(), fecha__lte=date.today()+timedelta(weeks=2))
	mes = eventos.filter(fecha__gte=date.today(), fecha__lte=date.today()+timedelta(days=30))
	todos = eventos.filter(fecha__gte=date.today())

	resumen7 = []
	for ev in semanas1:
		nombre = ev.Activacion.Cliente.nombre + " - " + ev.Activacion.nombre + " - " + ev.nombre

		falta = []
		falta_str = ""
		empty = ["", None]
		# Coordinación
		if ev.fecha_instalacion in empty or ev.fecha_desinstalacion in empty or ev.hora_instalacion in empty or ev.hora_desinstalacion in empty or ev.inicio_servicio in empty or ev.fin_servicio in empty or ev.direccion in empty or ev.Contacto in empty:
			falta.append("Coordinación")
		# Logística
		if ev.Trabajadores.all().count() == 0 or None in [it.ItemsEstacion for it in ItemsPlanEvento.objects.filter(PlanesEvento__in=ev.PlanesEvento.all())]:
			falta.append("Logística")
		# Check-list
		if False in [tarea.check for tarea in ev.RecurrentesEvento.all()] or False in [it.check for it in ItemsPlanEvento.objects.filter(PlanesEvento__in=ev.PlanesEvento.all())]:
			falta.append("Checklist")
		for i in range(len(falta)):
			falta_str += falta[i]
			if i+1 == len(falta):
				falta_str += "."
			elif i+2 == len(falta):
				falta_str += " y "
			else:
				falta_str += ", "
		if falta_str == "":
			falta_str = "Listo!"
		else:
			falta_str = "Falta completar " + falta_str

		resumen7.append([ev.fecha, nombre, int(round((3 - len(falta))/3.0*100, 0)), falta_str])


	context = {
		"errores": errores,
		"resumen7": resumen7,
		"semanas2": semanas2.count(),
		"mes": mes.count(),
		"todos": todos.count(),
		"s5": satisfaccion[0].count(),
		"s4": satisfaccion[1].count(),
		"s3": satisfaccion[2].count(),
		"s2": satisfaccion[3].count(),
		"s1": satisfaccion[4].count(),
	}
	if evaluados == 0:
		context["sp5"] = 0
		context["sp4"] = 0
		context["sp3"] = 0
		context["sp2"] = 0
		context["sp1"] = 0
	else:
		context["sp5"] = "%.1f" % (float(satisfaccion[0].count())/evaluados * 100)
		context["sp4"] = "%.1f" % (float(satisfaccion[1].count())/evaluados * 100)
		context["sp3"] = "%.1f" % (float(satisfaccion[2].count())/evaluados * 100)
		context["sp2"] = "%.1f" % (float(satisfaccion[3].count())/evaluados * 100)
		context["sp1"] = "%.1f" % (float(satisfaccion[4].count())/evaluados * 100)

	return render(request, 'index.html', context)


def calendario(request):
	eventos = Eventos.objects.filter(fecha__gte=date.today(), fecha__lte=date.today()+timedelta(weeks=1)).order_by("fecha")
	hoy = date.today()
	calendario = []
	cantidad = 0
	for i in range(8):
		dia = hoy+timedelta(days=i)

		evs = eventos.filter(fecha=dia)
		if evs.count() > cantidad:
			cantidad = evs.count()
		clientes = [ev.Activacion.Cliente.nombre for ev in evs]
		activaciones = [ev.Activacion.nombre for ev in evs]

		calendario.append([dia, evs, clientes, activaciones])
	
	dias = []
	for i in range(8):
		dias.append(hoy+timedelta(days=i))
	calendario2 = []
	for i in range(cantidad):
		calendario2.append([])
		for j in range(8):
			calendario2[-1].append([])
			try:
				calendario2[-1][-1] = [calendario[j][1][i], calendario[j][2][i], calendario[j][3][i]]
			except:
				calendario2[-1][-1] = ["", "", ""]

	context = {
		"dias": dias,
		"calendario": calendario2,
	}
	return render(request, 'calendario.html', context)


def clientes(request):
	clientes = Clientes.objects.all()
	
	titulos = ["#", "Cliente","Dirección"]
	#titulos = []
	#campos = Clientes._meta.get_fields()
	#for campo in campos:
	#	if not("ManyToOneRel" in str(campo.get_internal_type)):
	#		titulos.append(campo.verbose_name.title())
	#		print (campo.verbose_name.title())

	context = {
		"clientes": clientes,
		"titulos": titulos,
	}
	return render(request, 'clientes.html', context)


def agregar_cliente(request):
	if request.method == 'POST':
		form = ClientesForm(request.POST, request.FILES)
		if form.is_valid():
			cliente = form.save()
			#return custom_redirect('activaciones', cliente=cliente.idCliente)
			return custom_redirect('agregar_activacion', cliente=cliente.idCliente)
	else:
		form = ClientesForm()
	context = {
		"clientes_form": form,
	}
	return render(request, 'agregar_cliente.html', context)


def activaciones(request):
	activacion = ""
	idIngreso = ""
	nFactura = ""
	mensaje_error = ""
	if request.method == 'POST':
		activacion = request.POST["activacion"]
		nFactura = request.POST["radios_factura"]

		asociar = request.POST["asociar"]
		if asociar == "False":
			return custom_redirect('agregar_ingreso', activacion=activacion, factura=nFactura)
		elif nFactura != "-":
			idIngreso = request.POST["ingreso"]
			ingreso = Ingresos.objects.get(idIngreso=idIngreso)


			factura = Facturas.objects.get(nFactura=nFactura)
			monto_restante = factura.monto
			for i in factura.Ingresos.all():
				monto_restante -= i.monto

			if monto_restante >= ingreso.monto:
				ingreso.Factura = factura
				ingreso.save()
				return redirect("activaciones")
			else:
				mensaje_error = "El monto del ingreso " + str(ingreso.idIngreso) + " sobrepasa el de la factura " + str(factura.nFactura) + "."
		else:
			idIngreso = request.POST["ingreso"]
			mensaje_error = "Para asociar debes elegir una factura."

	try:
		idCliente = request.GET['cliente']
		cliente = Clientes.objects.get(idCliente=idCliente)
		activaciones = Activaciones.objects.filter(Cliente=cliente)
		titulos = ["#","Activación", "Tipo", "Monto", "Descripción"]
		contactos = cliente.Contactos.all()
		titulos_contactos = ["#", "Nombre", "Teléfono", "Mail"]
	except MultiValueDictKeyError:
		idCliente = ""
		cliente = ""
		activaciones = Activaciones.objects.all()
		titulos = ["#", "Cliente","Activación", "Tipo", "Monto", "Descripción"]
		contactos = None
		titulos_contactos = None

	pendientes = []
	venta = 0
	for act in activaciones:
		if act.Eventos.filter(fecha__gte=date.today()).count() > 0:
			pendientes.append(act)
		for factura in act.Facturas.all():
			venta += factura.monto

	context = {
		"activaciones": activaciones,
		"titulos": titulos,
		"titulos_contactos": titulos_contactos,
		"pendientes": len(pendientes),
		"cliente": cliente,
		"contactos": contactos,
		"venta": venta,
		"activacion": activacion,
		"idIngreso": idIngreso,
		"nFactura": nFactura,
		"mensaje_error": mensaje_error,
	}
	return render(request, 'activaciones.html', context)


def agregar_activacion(request):
	if request.method == 'POST':
		# try:
		# 	int(request.POST['Cliente']) # (probar si viene de SelectForm o no)
		# 	idCliente = request.POST['Cliente']
		# 	cliente = Clientes.objects.get(idCliente=idCliente)
		# 	form = ActivacionesForm(request.POST, request.FILES)
		# except:
		# 	cliente = request.POST['Cliente']
		# 	idCliente = cliente.idCliente
		# 	form = ActivacionesSelectForm(request.POST, request.FILES)
		idCliente = request.POST['Cliente']
		cliente = Clientes.objects.get(idCliente=idCliente)
		form = ActivacionesSelectForm(request.POST, request.FILES)

		nombre_unico = True

		if form.is_valid():
			activaciones = cliente.Activaciones.all()
			nombre = request.POST['nombre']
			for a in activaciones:
				if a.nombre == nombre:
					nombre_unico = False
					break

			if nombre_unico:
				activacion = form.save(commit=False)
				activacion.Cliente = Clientes.objects.get(idCliente=idCliente)
				activacion.save()
				#return custom_redirect('eventos', activacion=activacion.idActivacion)
				return custom_redirect('agregar_evento', activacion=activacion.idActivacion)
	
	else:
		try:
			idCliente = request.GET['cliente']
			cliente = Clientes.objects.get(idCliente=idCliente)
			#form = ActivacionesForm()
			form = ActivacionesSelectForm(initial={"Cliente":cliente})
		except MultiValueDictKeyError:
			cliente = ""
			form = ActivacionesSelectForm()
		nombre_unico = True

	context = {
		"activaciones_form": form,
		"cliente": cliente,
		"nombre_unico": nombre_unico,
	}
	return render(request, 'agregar_activacion.html', context)


class eventos(ListView):

	model = Eventos
	context_object_name = "eventos"
	template_name = "eventos.html"
	#paginate_by = 100  # if pagination is desired

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		eventos = Eventos.objects.all()

		hoy = date.today()
		
		orden = self.request.GET.get("orden", "fecha")
		pendientes = self.request.GET.get("pendientes", "Pendientes")
		cliente = self.request.GET.get("cliente", "")
		activacion = self.request.GET.get("activacion", "")
		evento = self.request.GET.get("evento", "")
		estado = self.request.GET.get("estado", "")

		Activacion = self.request.GET.get("Activacion", "")
		if Activacion != "":
			act = Activaciones.objects.get(idActivacion=Activacion)
			activacion = act.nombre
			cliente = act.Cliente.nombre
			pendientes = ""

		#f = self.request.GET.get("f", "")
		#if filtro == "":
		#	return Eventos.objects.all()
		if pendientes != "":
			if pendientes == "Pendientes":
				eventos = eventos.filter(fecha__gte=hoy)
			if pendientes == "Pasados":
				eventos = eventos.filter(fecha__lt=hoy)
		if cliente != "":
			eventos = eventos.filter(Activacion__Cliente__nombre__icontains=cliente)
		if activacion != "":
			eventos = eventos.filter(Activacion__nombre__icontains=activacion)
		if evento != "":
			eventos = eventos.filter(nombre__icontains=evento)
		if estado != "":
			eventos = eventos.filter(estado=estado)
		
		eventos = eventos.order_by(orden)
		context['eventos'] = eventos


		context['hoy'] = hoy
		context['pendientes'] = eventos.filter(fecha__gte=hoy)
		context['orden'] = orden
		initial = {
			"pendientes": pendientes,
			"cliente": cliente,
			"activacion": activacion,
			"evento": evento,
			"estado": estado,
		}
		context['filtros'] = filtroEventosForm(initial=initial)
		return context

	# def get_ordering(self):
	# 	ordering = self.request.GET.get('orden', '-idEvento')
	# 	#ordering = "fecha"
	# 	return ordering

	# def get_queryset(self):
	# 	filtro = self.request.GET.get("filtro", "")
	# 	f = self.request.GET.get("f", "")
	# 	if filtro == "":
	# 		return Eventos.objects.all()
	# 	elif filtro == "fecha":
	# 		return Eventos.objects.filter(fecha=f)
	# 	elif filtro == "estado":
	# 		return Eventos.objects.filter(estado=f)
	# 	elif filtro == "plan":
	# 		return Eventos.objects.filter(Planes__nombre__contains=f)


# ahora se usa la de arriba
def eventos_VIEJO(request):
	try:
		idActivacion = request.GET['activacion']
		activacion = Activaciones.objects.get(idActivacion=idActivacion)
		eventos = activacion.Eventos.all()
		cliente = activacion.Cliente
		titulos = ["#", "Evento", "Fecha", "Horas", "Plan(es)", "Comentarios", "Estado"]
	except MultiValueDictKeyError:
		idActivacion = ""
		activacion = ""
		eventos = Eventos.objects.all()
		cliente = ""
		titulos = ["#", "Cliente","Activación", "Evento", "Fecha", "Horas", "Plan(es)", "Comentarios", "Estado"]

	context = {
		"cliente": cliente,
		"activacion": activacion,
		"titulos": titulos,
		"pendientes": eventos.filter(fecha__gte=date.today()),
		"eventos": eventos,
		"hoy": date.today()
	}
	return render(request, 'eventos.html', context)


def agregar_evento(request):
	if request.method == 'POST':
		
		nPlanes = int(request.POST['nPlanes'])
		activacion = -1
		try:
			if request.POST['ActivacionSelect'] != "-1": # activacion no elejida
				activacion = Activaciones.objects.get(idActivacion=request.POST['ActivacionSelect'])
			form = EventosSelectForm(nPlanes, False, request.POST, request.FILES)
			select = True
		except:
			if request.POST['Activacion'] != "-1":
				activacion = Activaciones.objects.get(idActivacion=request.POST['Activacion'])
			form = EventosForm(nPlanes, request.POST, request.FILES)
			select = False

		count = 0
		mensaje_error = []
		nombre_unico = True
		values = []
		for key, value in request.POST.items():
			if "plan_" in key:
				count += 1
				if value == '-1':
					mensaje_error.append("Elija el plan %d " % count)
				elif value in values:
					mensaje_error.append("Se repite el plan %d " % count)
				values.append(value)
		if count != int(nPlanes):
			mensaje_error = []

		if form.is_valid() and count == int(nPlanes) and mensaje_error == [] and activacion != -1:

			eventos = activacion.Eventos.all()
			nombre = request.POST['nombre']
			for e in eventos:
				if e.nombre == nombre:
					nombre_unico = False
					break

			if nombre_unico:
				evento = Eventos(Activacion=activacion)
				#date(1943,3, 13)  #year, month, day
				evento.fecha = date(int(request.POST['fecha_year']), int(request.POST['fecha_month']), int(request.POST['fecha_day']))  #year, month, day
				evento.fecha_instalacion = evento.fecha
				evento.fecha_desinstalacion = evento.fecha
				evento.nombre = request.POST['nombre']
				evento.horas = request.POST['horas']
				evento.comentarios = request.POST['comentarios']
				evento.save()

				planes = []
				for i in range(1, nPlanes + 1):
					planes.append([Planes.objects.get(idPlan=request.POST["plan_%d" % i]), int(request.POST["cantidad_%d" % i])])

#				num = 0
				i = 1
				for plan, cantidad in planes:
#					for i in range(1, cantidad + 1):
#					num += 1
#					planEvento = PlanesEvento(Evento=evento, Plan=plan, n=num)
					planEvento = PlanesEvento(Evento=evento, Plan=plan, cantidad=cantidad, n=i)
					planEvento.save()
					i += 1

					for nPlan in range(1, cantidad + 1):
						for itemPlan in plan.ItemsPlan.all():
							#if itemPlan.activo:
							for nItem in range(1, itemPlan.cantidad + 1):
#								itemPlanEvento = ItemsPlanEvento(PlanesEvento=planEvento, ItemsPlan=itemPlan, ItemsEstacion=None, n=n)
								itemPlanEvento = ItemsPlanEvento(PlanesEvento=planEvento, ItemsPlan=itemPlan, ItemsEstacion=None, nPlan=nPlan, nItem=nItem)
								itemPlanEvento.save()
								if itemPlan.Item.multiple:
									break

				#return redirect('eventos')
				return custom_redirect('evento', evento=evento.idEvento)
	
	else:
		try:
			nPlanes = int(request.GET['nPlanes'])
		except MultiValueDictKeyError:
			nPlanes = 1

		try:
			idActivacion = request.GET['activacion']
			activacion = Activaciones.objects.get(idActivacion=idActivacion)
			#form = EventosForm(nPlanes)
			form = EventosSelectForm(nPlanes, False, initial={"ActivacionSelect": idActivacion})
			select = False
		except MultiValueDictKeyError:
			activacion = ""
			form = EventosSelectForm(nPlanes, False)
			select = True

		mensaje_error = []
		nombre_unico = True

	
	context = {
		"eventos_form": form,
		"activacion": activacion,
		"nPlanes": nPlanes,
		"mensaje_error": mensaje_error,
		"nombre_unico": nombre_unico,
		"select": select,
	}
	return render(request, 'agregar_evento.html', context)


def planes(request):
	planes = Planes.objects.all()
	
	titulos = ["#", "Plan", "Items", "Elegible"]

	context = {
		"planes": planes,
		"titulos": titulos,
	}
	return render(request, 'planes.html', context)


def agregar_plan(request):
	if request.method == 'POST':
		nombre_unico = True
		nItems = int(request.POST['nItems'])
		form = PlanesForm(nItems, request.POST, request.FILES)
		
		count = 0
		mensaje_error = []
		values = []
		for key, value in request.POST.items():
			if "item_" in key:
				count += 1
				if value == '-1':
					mensaje_error.append("Elija el item %d " % count)
				elif value in values:
					mensaje_error.append("Se repite el item %d " % count)
				values.append(value)
		if count != int(nItems):
			mensaje_error = []

		if form.is_valid() and count == int(nItems) and mensaje_error == []:
		# try:
		# 	items = Items.objects.filter(idItem__in=request.POST.getlist("items"))
		# 	#nItems = len(items)
		# 	nombres = [item.nombre for item in items]
		# 	fieldNum = -1 # para contar el csrf token
		# 	for key in request.POST:
		# 		fieldNum += 1
		# 		if key == "items":
		# 			break
		# 	nombres = [""]*fieldNum + nombres # para calzar con ciclo en html linea 138
		# except MultiValueDictKeyError:
		# 	items = []
		# 	#nItems = 0
		# 	nombres = []
		# form = PlanesForm(len(items), request.POST, request.FILES)
		# paso = int(request.POST["paso"])
		# if not(form.is_valid()):
		# 	paso = 1
		# else:
			# verificar uniqueness
			planes = Planes.objects.all()
			nombre = request.POST['nombre']
			for p in planes:
				if p.nombre == nombre:
					nombre_unico = False
					break
		#			paso = 1
		#	if nombre_unico and paso == 3:
			if nombre_unico:
				plan = Planes(nombre=nombre)
				plan.save()

				items = []
				for i in range(1, nItems + 1):
					items.append([Items.objects.get(idItem=request.POST["item_%d" % i]), request.POST["cantidad_%d" % i]])
		#		cantidades = []
		#		for i in range(1, len(items)+1):
		#			cantidades.append(request.POST['cantidad_%d' % i])

		#		for item, cantidad in zip(items, cantidades):
				n = 1
				for item, cantidad in items:
					itemsPlan = ItemsPlan(Plan=plan, Item=item, cantidad=cantidad, n=n)
					itemsPlan.save()
					n += 1

				return redirect('planes')
	else:
		try:
			editar = request.GET['editar']
			editar = ast.literal_eval(editar)
			nItems = int(editar['nItems'])
			form = PlanesForm(nItems, initial=editar)
		except MultiValueDictKeyError:
			try:
				nItems = int(request.GET['nItems'])
			except MultiValueDictKeyError:
				nItems = 1
			form = PlanesForm(nItems)

		nombre_unico = True
		mensaje_error = []
	#	paso = 1
	#	nombres = []
	context = {
		"planes_form": form,
		"nItems": nItems,
		"nombre_unico": nombre_unico,
		"mensaje_error": mensaje_error,
	#	"paso": paso,
	#	"nombres": nombres
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
	if request.method == 'POST':
		nombre_unico = True
		nItems = int(request.POST['nItems'])
		form = EstacionesForm(nItems, request.POST, request.FILES)
		
		count = 0
		mensaje_error = []
		values = []
		for key, value in request.POST.items():
			if "item_" in key:
				count += 1
				if value == '-1':
					mensaje_error.append("Elija el item %d " % count)
				elif value in values:
					mensaje_error.append("Se repite el item %d " % count)
				values.append(value)
		if count != int(nItems):
			mensaje_error = []

		if form.is_valid() and count == int(nItems) and mensaje_error == []:
			# verificar uniqueness
			estaciones = Estaciones.objects.all()
			nombre = request.POST['nombre']
			for e in estaciones:
				if e.nombre == nombre:
					nombre_unico = False
					break
			if nombre_unico:
				estacion = Estaciones(nombre=nombre)
				estacion.save()

				items = []
				for i in range(1, nItems + 1):
					items.append([Items.objects.get(idItem=request.POST["item_%d" % i]), request.POST["cantidad_%d" % i]])

				n = 1
				for item, cantidad in items:
					itemsEstacion = ItemsEstacion(Estacion=estacion, Item=item, cantidad=cantidad, n=n)
					itemsEstacion.save()
					n += 1

				return redirect('estaciones')
	else:
		try:
			editar = request.GET['editar']
			editar = ast.literal_eval(editar)
			nItems = int(editar['nItems'])
			form = EstacionesForm(nItems, initial=editar)
		except MultiValueDictKeyError:
			try:
				nItems = int(request.GET['nItems'])
			except MultiValueDictKeyError:
				nItems = 1
			form = EstacionesForm(nItems)

		nombre_unico = True
		mensaje_error = []

	context = {
		"estaciones_form": form,
		"nItems": nItems,
		"nombre_unico": nombre_unico,
		"mensaje_error": mensaje_error,
	}
	return render(request, 'agregar_estacion.html', context)

# def agregar_estacion(request):
# 	nombre_unico = True
# 	if request.method == 'POST':
# 		nItems = int(request.POST['nItems'])
# 		form = EstacionesForm(nItems, request.POST, request.FILES)

# 		if form.is_valid():
# 			# verificar uniqueness
# 			estaciones = Estaciones.objects.all()
# 			for e in estaciones:
# 				if e.nombre == request.POST['nombre']:
# 					nombre_unico = False
#					break
# 			if nombre_unico == True:
# 				estacion = Estaciones(nombre=request.POST['nombre'])
# 				#estacion.nombre = request.POST['nombre']
# 				estacion.save()

# 				items = []
# 				for key, value in request.POST.items():
# 					if "item_" in key:
# 						items.append(Items.objects.get(idItem=value))
# 				for item in items:
# 					itemsEstacion = ItemsEstacion(Estacion=estacion, Item=item)
# 					itemsEstacion.save()

# 				return redirect('estaciones')
# 	else:
# 		try:
# 			nItems = int(request.GET['nItems'])
# 		except MultiValueDictKeyError:
# 			nItems = 1
# 		form = EstacionesForm(nItems)
# 	context = {
# 		"estaciones_form": form,
# 		"nItems": nItems,
# 		"nombre_unico": nombre_unico,
# 	}
# 	return render(request, 'agregar_estacion.html', context)


def items(request):
	items = Items.objects.all()
	
	titulos = ["#", "Item", "Multiple"]

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
		evento = request.POST['evento']
		form = TrabajadoresForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()

			if evento == "":
				return redirect('trabajadores')
			else:
				return custom_redirect('evento', evento=evento, edit="logistica")
	else:
		form = TrabajadoresForm()
		try:
			evento = request.GET['evento']
		except MultiValueDictKeyError:
			evento = ""
	context = {
		"trabajadores_form": form,
		"evento": evento,
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
		evento = request.POST['evento']
		form = ContactosForm(request.POST, request.FILES)
		if form.is_valid():
			idCliente = request.POST['cliente']
			contacto = form.save(commit=False)
			contacto.Cliente = Clientes.objects.get(idCliente=idCliente)
			contacto.save()
			
			if evento == "":
				return custom_redirect('activaciones', cliente=idCliente)
			else:
				return custom_redirect('evento', evento=evento, edit="coordinacion")
	else:
		try:
			idCliente = request.GET['cliente']
			cliente = Clientes.objects.get(idCliente=idCliente)
			form = ContactosForm(initial={"Cliente": cliente})
		except MultiValueDictKeyError:
			return redirect('clientes')
		try:
			evento = request.GET['evento']
		except MultiValueDictKeyError:
			evento = ""
	context = {
		"contactos_form": form,
		"cliente": cliente,
		"evento": evento,
	}
	return render(request, 'agregar_contacto.html', context)

def agregar_contacto_select(request):
	if request.method == 'POST':
		try:
			evento = request.POST['evento']
		except MultiValueDictKeyError:
			evento = ""
		try:
			cliente = request.POST['cliente']
		except MultiValueDictKeyError:
			cliente = ""

		form = ContactosFormSelect(request.POST, request.FILES)
		if form.is_valid():
			form.save()

			if evento != "":
				return custom_redirect('evento', evento=evento, edit="coordinacion")
			elif cliente != "":
				return custom_redirect('activaciones', cliente=cliente)
			else:
				return redirect('contactos')
	else:
		initial = {}
		try:
			evento = request.GET['evento']
			initial["Cliente"] = Eventos.objects.get(idEvento=evento).Activacion.Cliente.idCliente
		except MultiValueDictKeyError:
			evento = ""
		try:
			cliente = request.GET['cliente']
			initial["Cliente"] = Clientes.objects.get(idCliente=cliente)
		except MultiValueDictKeyError:
			cliente = ""

		form = ContactosFormSelect(initial=initial)
	context = {
		"contactos_form": form,
		"cliente": cliente,
		"evento": evento,
	}
	return render(request, 'agregar_contacto.html', context)




def evento(request):
	error = False
	reporte = False
	nErrores = 0
	cargos = Cargos.objects.all()
	recurrentes = Recurrentes.objects.all()
	pendientes = Pendientes.objects.all()
	valid_trabajador = "n/a"
	valid_contacto = "n/a"
	if request.method == 'POST':
		idEvento = request.POST['evento']
		evento = Eventos.objects.get(idEvento=idEvento)

		coordinacion_form = None
		logistica_form = None
		trabajador_nuevo_form = None
		contacto_nuevo_form = None
		edit = request.POST['edit']
		tab = None
		if edit == "coordinacion":
			try:
				# Contacto nuevo
				request.POST["contacto_nuevo"]
				contacto_nuevo_form = ContactosForm(request.POST)
				valid_contacto = contacto_nuevo_form.is_valid()
				post = request.POST.copy()
				if valid_contacto:
					c_nuevo = contacto_nuevo_form.save(commit=False)
					c_nuevo.Cliente = evento.Activacion.Cliente
					c_nuevo.save()
					post["Contacto"] = c_nuevo.idContacto
				coordinacion_form = CoordinacionForm(evento, post, request.FILES)
			except MultiValueDictKeyError:
				valid_contacto = "n/a"
				coordinacion_form = CoordinacionForm(evento, request.POST, request.FILES)
				if coordinacion_form.is_valid():
					
					multiples_eventos = [evento]
					eventos_activacion = evento.Activacion.Eventos.all()
					for key, value in request.POST.items():
						if "multiples_" in key:
							multiples_eventos.append(eventos_activacion.get(idEvento=key.split("_")[1]))

					for ev in multiples_eventos:

						contacto = request.POST['Contacto']
						if contacto == "":
							ev.Contacto = None
						else:
							Contacto = ev.Activacion.Cliente.Contactos.get(idContacto=contacto)
							if Contacto != ev.Contacto:
								ev.Contacto = Contacto

						#date(1943,3, 13)  #year, month, day
						if (request.POST['fecha_instalacion_year'] == "0" and request.POST['fecha_instalacion_month'] == "0" and request.POST['fecha_instalacion_day'] == "0"):
							ev.fecha_instalacion = None
						if (request.POST['fecha_instalacion_year'] != "0" and request.POST['fecha_instalacion_month'] != "0" and request.POST['fecha_instalacion_day'] != "0"):
							ev.fecha_instalacion = date(int(request.POST['fecha_instalacion_year']), int(request.POST['fecha_instalacion_month']), int(request.POST['fecha_instalacion_day']))  #year, month, day
						if (request.POST['fecha_desinstalacion_year'] == "0" and request.POST['fecha_desinstalacion_month'] == "0" and request.POST['fecha_desinstalacion_day'] == "0"):
							ev.fecha_desinstalacion = None
						if (request.POST['fecha_desinstalacion_year'] != "0" and request.POST['fecha_desinstalacion_month'] != "0" and request.POST['fecha_desinstalacion_day'] != "0"):
							ev.fecha_desinstalacion = date(int(request.POST['fecha_desinstalacion_year']), int(request.POST['fecha_desinstalacion_month']), int(request.POST['fecha_desinstalacion_day']))  #year, month, day
						
						hora_instalacion = request.POST['hora_instalacion']
						if hora_instalacion == "":
							hora_instalacion = None
						if hora_instalacion != ev.hora_instalacion:
							ev.hora_instalacion = hora_instalacion

						hora_desinstalacion = request.POST['hora_desinstalacion']
						if hora_desinstalacion == "":
							hora_desinstalacion = None
						if hora_desinstalacion != ev.hora_desinstalacion:
							ev.hora_desinstalacion = hora_desinstalacion

						inicio_servicio = request.POST['inicio_servicio']
						if inicio_servicio == "":
							inicio_servicio = None
						if inicio_servicio != ev.inicio_servicio:
							ev.inicio_servicio = inicio_servicio
						
						fin_servicio = request.POST['fin_servicio']
						if fin_servicio == "":
							fin_servicio = None
						if fin_servicio != ev.fin_servicio:
							ev.fin_servicio = fin_servicio

						ev.direccion = request.POST['direccion']
						ev.save()
						#return custom_redirect('evento', evento=idEvento)
				else:
					error = True

		elif edit == "logistica":
			try:
				# Trabajador nuevo
				request.POST["trabajador_nuevo"]
				trabajador_nuevo_form = TrabajadoresForm(request.POST)
				valid_trabajador = trabajador_nuevo_form.is_valid()
				if valid_trabajador:
					trabajador_nuevo_form.save()
				logistica_form = LogisticaTrabajadoresForm(request.POST, request.FILES)
				logistica_planes_form = LogisticaPlanesForm(evento.PlanesEvento.all(), request.POST, request.FILES)
			except MultiValueDictKeyError:
				valid_trabajador = "n/a"
				logistica_form = LogisticaTrabajadoresForm(request.POST, request.FILES)
				logistica_planes_form = LogisticaPlanesForm(evento.PlanesEvento.all(), request.POST, request.FILES)

				if logistica_form.is_valid() and logistica_planes_form.is_valid():

				# Cargos Trabajadores
					multiples_eventos = [evento]
					eventos_activacion = evento.Activacion.Eventos.all()
					for key, value in request.POST.items():
						if "multiples_" in key:
							multiples_eventos.append(eventos_activacion.get(idEvento=key.split("_")[1]))

					for ev in multiples_eventos:

						for cargo in cargos:
							try:
								idTrabajadores = request.POST.getlist(cargo.nombre)
								trabajadores = Trabajadores.objects.filter(idTrabajador__in=idTrabajadores)
							except MultiValueDictKeyError:
								continue # trabajadores = []

							trabajadoresEvento_actuales = ev.TrabajadoresEvento.filter(Cargo=cargo)
							for trabajadorEvento_actual in trabajadoresEvento_actuales:
								if trabajadorEvento_actual.Trabajador not in trabajadores:
									trabajadorEvento_actual.delete()
							trabajadoresEvento_actuales = ev.TrabajadoresEvento.filter(Cargo=cargo)

							for trabajador in trabajadores:
								if trabajador not in [trabajadorEvento_actual.Trabajador for trabajadorEvento_actual in trabajadoresEvento_actuales]:
									TrabajadoresEvento(Evento=ev, Trabajador=trabajador, Cargo=cargo).save()
				
				# Planes
					for key, value in request.POST.items():
						if "planEvento_" in key:
							split = key.split("_")
							planEvento = PlanesEvento.objects.get(idPlanesEvento=int(split[1]))
							itemPlan = ItemsPlan.objects.get(idItemsPlan=int(split[3]))
							nPlan = int(split[5])
							nItem = int(split[7])
							if value == "-1":
								itemEstacion = None
							else:
								itemEstacion = ItemsEstacion.objects.get(idItemsEstacion=value)

							# if itemPlan.Item.multiple:
							# 	for i in range(itemPlan.cantidad):
							# 		itemPlanEvento = ItemsPlanEvento.objects.get(PlanesEvento=planEvento, ItemsPlan=itemPlan, n=(i+1))
							# 		itemPlanEvento.ItemsEstacion = itemEstacion
							# 		itemPlanEvento.save()
							# else:
							# 	itemPlanEvento = ItemsPlanEvento.objects.get(PlanesEvento=planEvento, ItemsPlan=itemPlan, n=n)
							# 	itemPlanEvento.ItemsEstacion = itemEstacion
							# 	itemPlanEvento.save()

							itemPlanEvento = ItemsPlanEvento.objects.get(PlanesEvento=planEvento, ItemsPlan=itemPlan, nPlan=nPlan, nItem=nItem)
							itemPlanEvento.ItemsEstacion = itemEstacion
							itemPlanEvento.save()

					#evento.save()
					#return custom_redirect('evento', evento=idEvento)
				else:
					error = True
		elif edit == "checklist":
			# Cargar al camion
			for key, value in request.POST.items():
				if "item_" in key:
					item = ItemsPlanEvento.objects.get(idItemsPlanEvento=key.split("_")[1])
					if value == "on":
						item.check = True
					else:
						item.check = False
					item.save()


			# Tareas recurrentes
			multiples_eventos = [evento]
			eventos_activacion = evento.Activacion.Eventos.all()
			for key, value in request.POST.items():
				if "multiples_" in key:
					multiples_eventos.append(eventos_activacion.get(idEvento=key.split("_")[1]))

				for ev in multiples_eventos:

					for recurrente in recurrentes:
						value = request.POST[recurrente.nombre.replace(" ", "")]
						recurrentesEvento = recurrente.RecurrentesEvento.get(Evento=ev)
						if value == "on":
							recurrentesEvento.check = True
						else:
							recurrentesEvento.check = False
						recurrentesEvento.save()

			#return custom_redirect('evento', evento=idEvento)

		elif edit == "checkout":
			#Pago trabajadores
			###


			# Tareas pendientes
			multiples_eventos = [evento]
			eventos_activacion = evento.Activacion.Eventos.all()
			for key, value in request.POST.items():
				if "multiples_" in key:
					multiples_eventos.append(eventos_activacion.get(idEvento=key.split("_")[1]))

				for ev in multiples_eventos:

					for pendiente in pendientes:
						value = request.POST[pendiente.nombre.replace(" ", "")]
						pendientesEvento = pendiente.PendientesEvento.get(Evento=ev)
						if value == "on":
							pendientesEvento.check = True
						else:
							pendientesEvento.check = False
						pendientesEvento.save()
# Falta pagos
# Falta pagos

			# Reportes
			try:
				evento.satisfaccion = int(request.POST["satisfaccion"])
			except MultiValueDictKeyError:
				pass
			evento.comentarios_satisfaccion = request.POST["comentarios_satisfaccion"]

			errores_evento = evento.Errores.all()
			nErrores = int(request.POST["nErrores"])
			errores_nuevos = []
			for key, value in request.POST.items():
				if "error" in key:
					errores_nuevos.append(value)
			print ("errores_nuevos: ", len(errores_nuevos))
			print ("nErrores: ", nErrores)
			if len(errores_nuevos) != nErrores:
				reporte = True
			else:
				for i in range(1, len(errores_evento) - len(errores_nuevos) + 1):
					errores_evento[len(errores_evento) - i].delete()
				for i in range(len(errores_nuevos)):
					if i < len(errores_evento):
						errores_evento[i].error = errores_nuevos[i]
						errores_evento[i].save()
					else:
						nuevo_error = Errores(Evento=evento, error=errores_nuevos[i])
						nuevo_error.save()

				evento.save()

				#return custom_redirect('evento', evento=idEvento)
		if not error and reporte == False and valid_trabajador == "n/a" and valid_contacto == "n/a":

			evento = Eventos.objects.get(idEvento=idEvento)

			multiples_eventos = [evento]
			eventos_activacion = evento.Activacion.Eventos.all()
			for key, value in request.POST.items():
				if "multiples_" in key:
					multiples_eventos.append(eventos_activacion.get(idEvento=key.split("_")[1]))

				for ev in multiples_eventos:

					estado = 5
					empty = ["", None]
				# Coordinación
					if ev.fecha_instalacion in empty or ev.fecha_desinstalacion in empty or ev.hora_instalacion in empty or ev.hora_desinstalacion in empty or ev.inicio_servicio in empty or ev.fin_servicio in empty or ev.direccion in empty or ev.Contacto in empty:
						estado = 0
				# Logística
					elif ev.Trabajadores.all().count() == 0 or None in [it.ItemsEstacion for it in ItemsPlanEvento.objects.filter(PlanesEvento__in=ev.PlanesEvento.all())]:
						estado = 1
				# Check-list
					elif False in [tarea.check for tarea in ev.RecurrentesEvento.all()] or False in [it.check for it in ItemsPlanEvento.objects.filter(PlanesEvento__in=ev.PlanesEvento.all())]:
						estado = 2
		 		# Check-out
					elif False in [tarea.check for tarea in ev.PendientesEvento.all()]: # Falta pagos
						estado = 3
				# Facturación
					#elif 
					#	estado = 4
		 # Falta pagos
					#print(estado)
					ev.estado = estado
					ev.save()

			return custom_redirect('evento', evento=idEvento)

	# GET
	else:
		try:
			idEvento = request.GET['evento']
			evento = Eventos.objects.get(idEvento=idEvento)
		except MultiValueDictKeyError:
			return redirect('eventos')
		try:
			coordinacion_form = None
			logistica_form = None
			trabajador_nuevo_form = None
			contacto_nuevo_form = None
			edit = request.GET['edit']
			if edit == "coordinacion":
				coordinacion_form = CoordinacionForm(evento, initial={
					"Contacto":evento.Contacto, 
					"inicio_servicio":evento.inicio_servicio, 
					"fin_servicio":evento.fin_servicio, 
					"fecha_instalacion":evento.fecha_instalacion, 
					"hora_instalacion":evento.hora_instalacion, 
					"fecha_desinstalacion":evento.fecha_desinstalacion, 
					"hora_desinstalacion":evento.hora_desinstalacion, 
					"direccion":evento.direccion
					})
				contacto_nuevo_form = ContactosForm()

			elif edit == "logistica":
				initial_trabajadores = {}
				for cargo in cargos:
					initial_trabajadores[cargo.nombre] = [trabajadorEvento.Trabajador.idTrabajador for trabajadorEvento in evento.TrabajadoresEvento.filter(Cargo=cargo)]
				logistica_form = LogisticaTrabajadoresForm(initial=initial_trabajadores)

				initial_planes = {}
				planesEvento = evento.PlanesEvento.all()
				for planEvento in planesEvento:
					for nPlan in range(1, planEvento.cantidad + 1):
						#activo problema :/
						# if planEvento.ItemsPlanEvento.filter(ItemsPlan=itemPlan).count() > 0:
						for itemPlan in planEvento.Plan.ItemsPlan.all():
							for nItem in range(1, itemPlan.cantidad + 1):
								try:
									init = ItemsPlanEvento.objects.get(PlanesEvento=planEvento, ItemsPlan=itemPlan, nItem=nItem, nPlan=nPlan).ItemsEstacion.idItemsEstacion
								except AttributeError: # (ItemsEstacion no definido en ItemsPlanEvento)
									init = None
								initial_planes['planEvento_%d_itemPlan_%d_nPlan_%d_nItem_%d' % (planEvento.idPlanesEvento, itemPlan.idItemsPlan, nPlan, nItem)] = init
								
								if itemPlan.Item.multiple:
									break;
				logistica_planes_form = LogisticaPlanesForm(planesEvento, initial=initial_planes)
				trabajador_nuevo_form = TrabajadoresForm()

			elif edit == "checklist":
				pass

			elif edit == "checkout":
				pass

		except MultiValueDictKeyError:
			edit = False

		
		tab = request.GET.get("tab", "menu")
		#origen = request.META['HTTP_REFERER']
		#if "edit=coordinacion" in origen or "itinerario" in origen:
		#	tab = "coordinacion"
		#elif "edit=logistica" in origen:
		#	tab = "logistica"
		#elif "edit=checklist" in origen:
		#	tab = "checklist"
		

	lista_planes = []
	for planEvento in evento.PlanesEvento.all():
		itemsPlanEvento = planEvento.ItemsPlanEvento.all() #.order_by('PlanesEvento', 'nPlan', 'ItemsPlan', 'nItem')
		lista_planes.append([])
		nPlan = planEvento.cantidad
		plan_actual = -1
		nPlan_actual = -1
		for it in itemsPlanEvento:
			if it.nPlan != nPlan_actual or it.PlanesEvento.n != plan_actual:
				lista_planes[-1].append([])
				plan_actual = it.PlanesEvento.n
				nPlan_actual = it.nPlan

			if it.ItemsPlan.Item.multiple:
				num = "(x%d)" % it.ItemsPlan.cantidad
			else:
				num = it.nItem

			initial_checklist = {}
			initial_checklist['item_%d' % it.idItemsPlanEvento] = it.check

			if edit == "logistica":
				estacion = logistica_planes_form['planEvento_%d_itemPlan_%d_nPlan_%d_nItem_%d' % (planEvento.idPlanesEvento, it.ItemsPlan.idItemsPlan, it.nPlan, it.nItem)]
				check = None
			elif edit == "checklist":
				estacion = it.ItemsEstacion
				check = EventoChecklistForm(it.idItemsPlanEvento, initial={"item_%d" % it.idItemsPlanEvento: it.check})['item_%d' % it.idItemsPlanEvento]
			else:
				estacion = it.ItemsEstacion
				check = it.check
			lista_planes[-1][-1].append([it.ItemsPlan.Item, num, estacion, check])

	# Tareas recurrentes
	for recurrente in recurrentes:
		try:
			recurrente.RecurrentesEvento.get(Evento=evento)
		except RecurrentesEvento.DoesNotExist:
			ev = RecurrentesEvento(Recurrente=recurrente, Evento=evento)
			ev.save()

	if edit == "checklist":
		initial = {}
		for recurrente in recurrentes:
			initial[recurrente.nombre.replace(" ", "")] = RecurrentesEvento.objects.get(Evento=evento, Recurrente=recurrente).check
		lista_recurrentes = RecurrentesEventoForm(initial=initial)
	else:
		lista_recurrentes = []
		for recurrente in recurrentes:
			lista_recurrentes.append([recurrente.nombre, recurrente.RecurrentesEvento.get(Evento=evento).check])

	# Tareas pendientes
	for pendiente in pendientes:
		try:
			pendiente.PendientesEvento.get(Evento=evento)
		except PendientesEvento.DoesNotExist:
			ev = PendientesEvento(Pendiente=pendiente, Evento=evento)
			ev.save()

	if edit == "checkout":
		initial = {}
		for pendiente in pendientes:
			initial[pendiente.nombre.replace(" ", "")] = PendientesEvento.objects.get(Evento=evento, Pendiente=pendiente).check
		lista_pendientes = PendientesEventoForm(initial=initial)

		initial = {}
		initial["satisfaccion"] = evento.satisfaccion
		initial["comentarios_satisfaccion"] = evento.comentarios_satisfaccion
		if reporte:
			reporte_form = ReportesForm(nErrores, request.POST)
		else:
			errores_evento = evento.Errores.all()
			nErrores = len(errores_evento)
			for i in range(1, len(errores_evento) + 1):
				initial["error_%d" % i] = errores_evento[i-1].error
			reporte_form = ReportesForm(nErrores, initial=initial)
		print(nErrores)
	else:
		lista_pendientes = []
		for pendiente in pendientes:
			lista_pendientes.append([pendiente.nombre, pendiente.PendientesEvento.get(Evento=evento).check])
		reporte_form = ""

	multiples_form = None
	if edit != False:
		multiples_form = multiplesEventoForm(evento)

	context = {
		"evento": evento,
		"edit": edit,
		"coordinacion_form": coordinacion_form,
		"logistica_form": logistica_form,
		"error": error,
		"tab": tab,
		"lista_planes": lista_planes,
		"cargos": cargos,
		"lista_recurrentes": lista_recurrentes,
		"lista_pendientes": lista_pendientes,
		"reporte_form": reporte_form,
		"nErrores": nErrores,
		"trabajador_nuevo_form": trabajador_nuevo_form,
		"valid_trabajador": valid_trabajador,
		"contacto_nuevo_form": contacto_nuevo_form,
		"valid_contacto": valid_contacto,
		"multiples_form": multiples_form,
	}
	return render(request, 'evento.html', context)




def cargos(request):
	cargos = Cargos.objects.all()
	
	#titulos = ["#", "Nombre", "RUT", "Teléfono", "Mail"]

	context = {
		"cargos": cargos,
		#"titulos": titulos,
	}
	return render(request, 'cargos.html', context)


def agregar_cargo(request):
	if request.method == 'POST':
		form = CargosForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()

			return redirect('cargos')
	else:
		cargos = Cargos.objects.all().reverse()
		initial ={}
		if len(cargos) > 0:
			initial["n"] = cargos[0].n + 1
		form = CargosForm(initial=initial)
	context = {
		"cargos_form": form,
	}
	return render(request, 'agregar_cargo.html', context)


def recurrentes(request):
	recurrentes = Recurrentes.objects.all()
	
	#titulos = ["#", "Nombre", "RUT", "Teléfono", "Mail"]

	context = {
		"recurrentes": recurrentes,
		#"titulos": titulos,
	}
	return render(request, 'recurrentes.html', context)


def agregar_recurrente(request):
	if request.method == 'POST':
		form = RecurrentesForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()

			return redirect('recurrentes')
	else:
		recurrentes = Recurrentes.objects.all().reverse()
		initial ={}
		if len(recurrentes) > 0:
			initial["n"] = recurrentes[0].n + 1
		form = RecurrentesForm(initial=initial)
	context = {
		"recurrentes_form": form,
	}
	return render(request, 'agregar_recurrente.html', context)


def pendientes(request):
	pendientes = Pendientes.objects.all()
	
	context = {
		"pendientes": pendientes,
		#"titulos": titulos,
	}
	return render(request, 'pendientes.html', context)


def agregar_pendiente(request):
	if request.method == 'POST':
		form = PendientesForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()

			return redirect('pendientes')
	else:
		pendientes = Pendientes.objects.all().reverse()
		initial ={}
		if len(pendientes) > 0:
			initial["n"] = pendientes[0].n + 1
		form = PendientesForm(initial=initial)
	context = {
		"pendientes_form": form,
	}
	return render(request, 'agregar_pendiente.html', context)


def facturas(request):
	facturas = Facturas.objects.all()
	
	context = {
		"facturas": facturas,
		#"titulos": titulos,
	}
	return render(request, 'facturas.html', context)


def agregar_factura(request):
	mensaje_error = ""
	if request.method == 'POST':
		form = FacturasForm(request.POST, request.FILES)
		if form.is_valid(): # and activacion != -1:
			activacion = request.POST["activacion"]
			
			act = Activaciones.objects.get(idActivacion=activacion)
			facturas = act.Facturas.all()
			monto_restante = act.monto
			for f in facturas:
				monto_restante -= f.monto
			
			monto = int(request.POST["monto"])
			if monto > monto_restante:
				mensaje_error = "Este monto es mayor al total que queda por facturar de la activación."
			else:
				nFactura = int(request.POST["nFactura"])
				fecha_facturacion = date(int(request.POST['fecha_facturacion_year']), int(request.POST['fecha_facturacion_month']), int(request.POST['fecha_facturacion_day']))  #year, month, day
				
				#adelanto = int(request.POST["adelanto"])
				plazo = int(request.POST["plazo"])
				fecha_pago = fecha_facturacion + timedelta(days=plazo)

				#factura = Facturas(nFactura=nFactura, Activacion=Activaciones.objects.get(idActivacion=activacion), fecha_facturacion=fecha_facturacion, monto=monto, pago=adelanto, fecha_pago=fecha_pago)
				factura = Facturas(nFactura=nFactura, Activacion=act, fecha_facturacion=fecha_facturacion, monto=monto, fecha_pago=fecha_pago)
				factura.save()

				return redirect('activaciones')
	else:
		activacion = request.GET["activacion"]
		ultima = Facturas.objects.first()
		if ultima == None:
			nFactura = 1
		else:
			nFactura = ultima.nFactura + 1

		act = Activaciones.objects.get(idActivacion=activacion)
		facturas = act.Facturas.all()
		monto_restante = act.monto
		for f in facturas:
			monto_restante -= f.monto

		initial = {
			"nFactura": nFactura,
			"fecha_facturacion": date.today(),
			"monto": monto_restante,
			"plazo": 30,
			"activacion": activacion,
		}
		#try:
		#	initial["Activacion"] = request.GET["activacion"]
		#except MultiValueDictKeyError:
		#	pass
		form = FacturasForm(initial=initial)

	context = {
		"activacion": activacion,
		"facturas_form": form,
		"mensaje_error": mensaje_error,
	}
	return render(request, 'agregar_factura.html', context)


def ingresos(request):
	ingresos = Ingresos.objects.all()
	
	context = {
		"ingresos": ingresos,
		#"titulos": titulos,
	}
	return render(request, 'ingresos.html', context)


def agregar_ingreso(request):
	mensaje_error = ""
	if request.method == 'POST':
		form = IngresosForm(request.POST, request.FILES)
		if form.is_valid():
			activacion = request.POST["activacion"]
			factura = request.POST["factura"]
			act = Activaciones.objects.get(idActivacion=activacion)
			
			monto = int(request.POST["monto"])

			ingresos_totales = act.Ingresos.all()
			monto_restante_total = act.monto
			for i in ingresos_totales:
				monto_restante_total -= i.monto

			monto_restante = 0
			if factura == "-":
				fact = None
				facturas = act.Facturas.all()
				monto_restante = act.monto
				for f in facturas:
					monto_restante -= f.monto
			elif factura != "Weddi":
				fact = Facturas.objects.get(nFactura=factura)
				ingresos = fact.Ingresos.all()
				monto_restante = fact.monto
				for i in ingresos:
					monto_restante -= i.monto

			
			if monto > monto_restante and factura == "-":
				mensaje_error = "Este monto es mayor al total que queda por facturar de la activación. Considere asociar este pago a una de las facturas existentes."
			elif monto > monto_restante and factura != "-" and factura != "Weddi":
				mensaje_error = "Este monto es mayor al total que queda por pagar de la facturación."
			elif (monto > monto_restante_total) and factura != "Weddi":
				mensaje_error = "Error, hay un pago en la activación que no tiene factura asociada, se recomienda primero asociarla a esta factura."
			elif (monto > monto_restante_total) and factura == "Weddi":
				mensaje_error = "Este monto es mayor al total que queda por pagar de la activación."
			else:
				fecha = date(int(request.POST['fecha_year']), int(request.POST['fecha_month']), int(request.POST['fecha_day']))  #year, month, day
				comentarios = request.POST["comentarios"]

				if factura == "Weddi":
					ingreso = Ingresos(Factura=None, Activacion=act, fecha=fecha, monto=monto, comentarios=comentarios)
				else:
					ingreso = Ingresos(Factura=fact, Activacion=act, fecha=fecha, monto=monto, comentarios=comentarios)
				ingreso.save()

				return redirect('activaciones')
	else:
		activacion = request.GET["activacion"]
		factura = request.GET["factura"]
		
		if factura == "-":
			act = Activaciones.objects.get(idActivacion=activacion)
			facturas = act.Facturas.all()
			monto_restante = act.monto
			for f in facturas:
				monto_restante -= f.monto
		elif factura == "Weddi":
			act = Activaciones.objects.get(idActivacion=activacion)
			ingresos = act.Ingresos.all()
			monto_restante = act.monto
			for i in ingresos:
				monto_restante -= i.monto
		else:
			fact = Facturas.objects.get(nFactura=factura)
			ingresos = fact.Ingresos.all()
			monto_restante = fact.monto
			for i in ingresos:
				monto_restante -= i.monto

		initial = {
			"monto": monto_restante,
			"fecha": date.today(),
		}
		form = IngresosForm(initial=initial)

	context = {
		"activacion": activacion,
		"factura": factura,
		"ingresos_form": form,
		"mensaje_error": mensaje_error,
	}
	return render(request, 'agregar_ingreso.html', context)


def itinerario_crear(request):
	error = ""
	if request.method == 'POST':
		form_fecha = itinerarioFechaForm(request.POST)
		if form_fecha.is_valid():
			desde = date(int(request.POST['desde_year']), int(request.POST['desde_month']), int(request.POST['desde_day']))  #year, month, day
			hasta = date(int(request.POST['hasta_year']), int(request.POST['hasta_month']), int(request.POST['hasta_day']))  #year, month, day
			if desde > hasta:
				error = "Fechas incorrectas"
			else:
				return custom_redirect('itinerario', trabajador=request.POST['trabajador'], desde=desde, hasta=hasta)

		form_eventos = itinerarioEventosForm(request.POST)
		if form_eventos.is_valid():
			eventos = request.POST.getlist("eventos")
			return custom_redirect('itinerario', trabajador=request.POST['trabajador'], eventos=eventos)
	else:
		form_fecha = itinerarioFechaForm()
		form_eventos = itinerarioEventosForm()


	context = {
		"itinerario_fecha": form_fecha,
		"itinerario_eventos": form_eventos,
		"error": error,
	}
	return render(request, 'itinerario_crear.html', context)


def itinerario(request):
	eventos = ""
	errores_info = []
	itinerario = []
	dias = []
	if request.method == 'POST':
		#checks
		evento = Eventos.objects.get(idEvento=request.POST["evento"])
		tipo = request.POST["tipo"]
		seguimiento = request.POST["seguimiento"]
		if tipo == 'INSTALACIÓN':
			evento.seguimiento_instalacion = seguimiento
		elif tipo == 'DESINSTALACIÓN':
			evento.seguimiento_desinstalacion = seguimiento
		elif tipo == 'INICIO SERVICIO':
			evento.seguimiento_inicio_servicio = seguimiento
		elif tipo == 'FIN SERVICIO':
			evento.seguimiento_fin_servicio = seguimiento
		evento.save()
		
	#else:
	try:
		desde = request.GET["desde"].split("-")
		desde = date(int(desde[0]), int(desde[1]), int(desde[2]))
		hasta = request.GET["hasta"].split("-")
		hasta = date(int(hasta[0]), int(hasta[1]), int(hasta[2]))
		eventos = Eventos.objects.filter(fecha__gte=desde, fecha__lte=hasta)
	except MultiValueDictKeyError:
		try:
			eventos = ast.literal_eval(request.GET["eventos"])
			eventos = Eventos.objects.filter(idEvento__in=eventos)
		except MultiValueDictKeyError:
			return redirect("itinerario_crear")
	trabajador = request.GET["trabajador"]
	if trabajador != "-1":
		eventos = eventos.filter(Trabajadores__idTrabajador=trabajador).distinct()
	eventos = eventos.order_by("fecha")
	
	for evento in eventos:
		if evento.hora_instalacion == None:
			errores_info.append([evento.idEvento, "hora de instalación"])
		if evento.hora_desinstalacion == None:
			errores_info.append([evento.idEvento, "hora de desinstalación"])
		if evento.inicio_servicio == None:
			errores_info.append([evento.idEvento, "hora de inicio del servicio"])
		if evento.fin_servicio == None:
			errores_info.append([evento.idEvento, "hora de fin del servicio"])
		if evento.fecha_instalacion == None:
			errores_info.append([evento.idEvento, "fecha de instalación"])
		if evento.fecha_desinstalacion == None:
			errores_info.append([evento.idEvento, "fecha de desinstalación"])

	if errores_info == []:
		#fecha = desde
		#while fecha <= hasta:
		#	fecha += timedelta(days=1)
		fecha = -1
		for ev in eventos:
			if ev.fecha != fecha:
				fecha = ev.fecha
				itinerario.append([])
				dias.append(fecha)

				for evento in eventos.filter(fecha=fecha):
					itinerario[-1].append([evento.hora_instalacion, "INSTALACIÓN", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
					itinerario[-1].append([evento.inicio_servicio, "INICIO SERVICIO", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
					itinerario[-1].append([evento.fin_servicio, "FIN SERVICIO", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
					itinerario[-1].append([evento.hora_desinstalacion, "DESINSTALACIÓN", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])

				itinerario[-1].sort(key=lambda x: x[0])

	context = {
		"eventos": eventos,
		"itinerario": itinerario,
		"dias": dias,
		"errores_info": errores_info,
	}
	return render(request, 'itinerario.html', context)



############################################################## Editar ##############################################################
############################################################## Editar ##############################################################

def editar_cliente(request):
	if request.method == 'POST':
		cliente = Clientes.objects.get(idCliente=request.POST['cliente'])
		form = ClientesForm(request.POST, request.FILES)
		if form.is_valid() or cliente.nombre == request.POST['nombre']:
			#c = form.save(commit=False)
			#c.idCliente = cliente.idCliente
			#c.save()
			nombre = request.POST['nombre']
			if cliente.nombre != nombre:
				cliente.nombre = nombre
			direccion = request.POST['direccion']
			if cliente.direccion != direccion:
				cliente.direccion = direccion
			cliente.save()
			return redirect('clientes')
	else:
		cliente = Clientes.objects.get(idCliente=request.GET['cliente'])
		form = ClientesForm(initial={"nombre": cliente.nombre, "direccion": cliente.direccion})
	context = {
		"clientes_form": form,
		"cliente": cliente,
	}
	return render(request, 'editar_cliente.html', context)


def editar_activacion(request):
	if request.method == 'POST':
		activacion = Activaciones.objects.get(idActivacion=request.POST['Activacion'])
		form = ActivacionesSelectForm(request.POST, request.FILES)
		try:
			menuCliente = request.POST['menuCliente']
		except MultiValueDictKeyError:
			menuCliente = ""

		nombre_unico = True
		nombre = request.POST['nombre']
		cliente = Clientes.objects.get(idCliente=request.POST['Cliente'])
		if (nombre != activacion.nombre and cliente.idCliente == activacion.Cliente.idCliente) or (cliente.idCliente != activacion.Cliente.idCliente):
			activaciones = cliente.Activaciones.all()
			for a in activaciones:
				if a.nombre == nombre:
					nombre_unico = False
					break

		if form.is_valid() and nombre_unico:
			a = form.save(commit=False)
			a.idActivacion = activacion.idActivacion
			a.save()

			if menuCliente != "":
				return custom_redirect('activaciones', cliente=menuCliente)
			else:
				return redirect('activaciones')
	else:
		activacion = Activaciones.objects.get(idActivacion=request.GET['Activacion'])
		form = ActivacionesSelectForm(initial={"Cliente":activacion.Cliente, "nombre": activacion.nombre, "monto":activacion.monto,"descripcion": activacion.descripcion})
		try:
			menuCliente = request.GET['cliente']
		except MultiValueDictKeyError:
			menuCliente = ""
		nombre_unico = True

	context = {
		"activaciones_form": form,
		"menuCliente": menuCliente,
		"activacion": activacion,
		"nombre_unico": nombre_unico,
	}
	return render(request, 'editar_activacion.html', context)


def editar_evento(request):
	if request.method == 'POST':
		evento = Eventos.objects.get(idEvento=request.POST['evento'])
		nPlanes = int(request.POST['nPlanes'])
		form = EventosSelectForm(nPlanes, True, request.POST, request.FILES)
		try:
			menuActivacion = request.POST['menuActivacion']
		except MultiValueDictKeyError:
			menuActivacion = ""		

		count = 0
		mensaje_error = []
		nombre_unico = True
		values = []
		for key, value in request.POST.items():
			if "plan_" in key:
				count += 1
				if value == '-1':
					mensaje_error.append("Elija el plan %d " % count)
				elif value in values:
					mensaje_error.append("Se repite el plan %d " % count)
				values.append(value)
		if count != int(nPlanes):
			mensaje_error = []

		nombre = request.POST['nombre']
		activacion = Activaciones.objects.get(idActivacion=request.POST['ActivacionSelect'])
		if (nombre != evento.nombre and activacion.idActivacion == evento.Activacion.idActivacion) or (activacion.idActivacion != evento.Activacion.idActivacion):
			eventos = activacion.Eventos.all()
			for e in eventos:
				if e.nombre == nombre:
					nombre_unico = False
					break

		if form.is_valid() and count == int(nPlanes) and mensaje_error == [] and nombre_unico:
			#date(1943,3, 13)  #year, month, day
			if evento.Activacion.idActivacion != activacion.idActivacion:
				evento.Activacion = activacion
			evento.fecha = date(int(request.POST['fecha_year']), int(request.POST['fecha_month']), int(request.POST['fecha_day']))  #year, month, day
			if evento.nombre != nombre:
				evento.nombre = nombre
			if evento.horas != request.POST['horas']:
				evento.horas = request.POST['horas']
			if evento.comentarios != request.POST['comentarios']:
				evento.comentarios = request.POST['comentarios']
			evento.save()

			planesNuevos = []
			for i in range(1, nPlanes+1):
				cantidad = int(request.POST["cantidad_%d" % i])
				#for j in range(1, cantidad+1):
				planesNuevos.append([Planes.objects.get(idPlan=request.POST["plan_%d" % i]), cantidad])

			# Eliminar planes que no se encuentran en la nueva lista
			planesActuales = evento.PlanesEvento.all()
			for planActual in planesActuales:
				if planActual.Plan.idPlan not in [plan.idPlan for plan, cant in planesNuevos]:
					planActual.delete()

			# Agregar nuevos planes y cambiar cantidades de los existentes
			num = 0
			for nuevoPlan, cantidad in planesNuevos:
				#filtro = planesActuales.filter(Plan=nuevoPlan) #.order_by("n")
				try:
					planActual = planesActuales.get(Plan=nuevoPlan)
				except PlanesEvento.DoesNotExist:
					planActual = PlanesEvento(Evento=evento, Plan=nuevoPlan, cantidad=0)
				dif = cantidad - planActual.cantidad
				
				num += 1
				planActual.n = num
				planActual.cantidad = cantidad
				planActual.save()

				if dif > 0:
					for nPlan in range(cantidad - dif + 1, cantidad + 1):
						for itemPlan in nuevoPlan.ItemsPlan.all():
							#if itemPlan.activo:
							for nItem in range(1, itemPlan.cantidad + 1):
								itemPlanEvento = ItemsPlanEvento(PlanesEvento=planActual, ItemsPlan=itemPlan, ItemsEstacion=None, nPlan=nPlan, nItem=nItem)
								itemPlanEvento.save()
								if itemPlan.Item.multiple:
									break
				elif dif < 0:
					for it in planActual.ItemsPlanEvento.all():
						if it.nPlan > cantidad:
							it.delete()

			# planesActuales = evento.PlanesEvento.all().order_by("n")
			# actuales = len(planesActuales)
			# nuevos = len(planesNuevos)
			# for planActual, nuevoPlan in zip(planesActuales, planesNuevos):
			# 	if planActual.Plan.idPlan != nuevoPlan.idPlan:
			# 		num = planActual.n
			# 		planActual.delete()
			# 		planEvento = PlanesEvento(Evento=evento, Plan=nuevoPlan, n=num)
			# 		planEvento.save()
			# 		for itemPlan in nuevoPlan.ItemsPlan.all():
			# 				for n in range(1, itemPlan.cantidad + 1):
			# 					itemPlanEvento = ItemsPlanEvento(PlanesEvento=planEvento, ItemsPlan=itemPlan, ItemsEstacion=None, n=n)
			# 					itemPlanEvento.save()

			# planesActuales = evento.PlanesEvento.all().order_by("n")
			# if nuevos > actuales:
			# 	for nuevoPlan in planesNuevos[actuales:]:
			# 		num = 0
			# 		for i in range(len(planesActuales)):
			# 			if (i+1) != planesActuales[i].n:
			# 				num = i+1
			# 				break
			# 		if num == 0:
			# 			num = len(planesActuales) + 1

			# 		planEvento = PlanesEvento(Evento=evento, Plan=nuevoPlan, n=num)
			# 		planEvento.save()
			# 		for itemPlan in nuevoPlan.ItemsPlan.all():
			# 				for n in range(1, itemPlan.cantidad + 1):
			# 					itemPlanEvento = ItemsPlanEvento(PlanesEvento=planEvento, ItemsPlan=itemPlan, ItemsEstacion=None, n=n)
			# 					itemPlanEvento.save()
			# elif actuales > nuevos:
			# 	for planActual in planesNuevos[actuales:]:
			# 		planActual.delete()

			if menuActivacion != "":
				return custom_redirect('eventos', activacion=menuActivacion)
			else:
				return redirect('eventos')
	else:
		evento = Eventos.objects.get(idEvento=request.GET['evento'])
		nPlanes = evento.Planes.all().count()
		initial={"ActivacionSelect":evento.Activacion.idActivacion, "nombre": evento.nombre, "fecha": evento.fecha, "horas": evento.horas, "comentarios": evento.comentarios}
		
		plan = -1
		I = -1
		cant = -1
		for planEvento in evento.PlanesEvento.all(): #.order_by("n"):
			initial['plan_%d' % (planEvento.n)] = planEvento.Plan.idPlan
			initial['cantidad_%d' % (planEvento.n)] = planEvento.cantidad
		# 	if plan == -1:
		# 		I = 1
		# 		cant = 1
		# 		plan = planEvento.Plan.idPlan
		# 		initial['plan_%d' % (I)] = planEvento.Plan.idPlan
		# 	elif plan == planEvento.Plan.idPlan:
		# 		cant += 1
		# 	else:
		# 		initial['cantidad_%d' % (I)] = cant
		# 		I += 1
		# 		cant = 1
		# 		plan = planEvento.Plan.idPlan
		# 		initial['plan_%d' % (I)] = plan
		# initial['cantidad_%d' % (I)] = cant

		# nPlanes = I
		form = EventosSelectForm(nPlanes, True, initial=initial)
		try:
			menuActivacion = request.GET['activacion']
		except MultiValueDictKeyError:
			menuActivacion = ""
		count = 0
		mensaje_error = []
		nombre_unico = True

	
	context = {
		"eventos_form": form,
		"menuActivacion": menuActivacion,
		"evento": evento,
		"nPlanes": nPlanes,
		"count": count,
		"mensaje_error": mensaje_error,
		"nombre_unico": nombre_unico,
	}
	return render(request, 'editar_evento.html', context)


def editar_plan(request):
	if request.method == 'POST':
		nuevo_plan = request.POST['nuevo_plan']
		if nuevo_plan != "-1":
			initial = {}
			for key, value in request.POST.items():
				if "csrf" not in key:
					initial[key] = value
			return custom_redirect('agregar_plan', editar=initial)

		nombre_unico = True
		plan = Planes.objects.get(idPlan=request.POST['plan'])
		nItems = int(request.POST['nItems'])
		form = PlanesForm(nItems, request.POST, request.FILES)
		try:
			form_mostrar = MostrarPlanForm(initial={"mostrar": request.POST['mostrar']})
		except MultiValueDictKeyError:
			form_mostrar = MostrarPlanForm(initial={"mostrar": False})
		
		count = 0
		mensaje_error = []
		values = []
		for key, value in request.POST.items():
			if "item_" in key:
				count += 1
				if value == '-1':
					mensaje_error.append("Elija el item %d " % count)
				elif value in values:
					mensaje_error.append("Se repite el item %d " % count)
				values.append(value)
		if count != int(nItems):
			mensaje_error = []

		if form.is_valid() and count == int(nItems) and mensaje_error == []:
			# verificar uniqueness
			nombre = request.POST['nombre']
			if nombre != plan.nombre:
				planes = Planes.objects.all()
				for p in planes:
					if p.nombre == nombre:
						nombre_unico = False
						break

			if nombre_unico:
				if plan.nombre != nombre:
					plan.nombre = nombre
				try:
					if request.POST['mostrar'] == "on":
						mostrar = True
				except MultiValueDictKeyError:
					mostrar = False
				if plan.mostrar != mostrar:
					plan.mostrar = mostrar
				plan.save()


				itemsNuevos = []
				for i in range(1, nItems+1):
					cantidad = int(request.POST["cantidad_%d" % i])
					#for j in range(1, cantidad+1):
					itemsNuevos.append([Items.objects.get(idItem=request.POST["item_%d" % i]), cantidad])

				# Eliminar items que no se encuentran en la nueva lista
				itemsActuales = plan.ItemsPlan.all()
				for itemActual in itemsActuales:
					if itemActual.Item.idItem not in [item.idItem for item, cant in itemsNuevos]:
						itemActual.delete()

				# Agregar nuevos items y cambiar cantidades de los existentes
				num = 0
				for nuevoItem, cantidad in itemsNuevos:
					#filtro = planesActuales.filter(Plan=nuevoPlan) #.order_by("n")
					try:
						itemActual = itemsActuales.get(Item=nuevoItem)
						nuevo = False
					except ItemsPlan.DoesNotExist:
						itemActual = ItemsPlan(Plan=plan, Item=nuevoItem, cantidad=0)
						nuevo = True
					dif = cantidad - itemActual.cantidad
					
					num += 1
					itemActual.n = num
					itemActual.cantidad = cantidad
					itemActual.save()

					if dif > 0:
						for planEvento in plan.PlanesEvento.all():
							for nPlan in range(1, planEvento.cantidad + 1):
								for nItem in range(cantidad - dif + 1, cantidad + 1):
									if not(itemActual.Item.multiple and not(nuevo)):
										itemPlanEvento = ItemsPlanEvento(PlanesEvento=planEvento, ItemsPlan=itemActual, ItemsEstacion=None, nPlan=nPlan, nItem=nItem)
										itemPlanEvento.save()
									if itemActual.Item.multiple:
										break
					elif dif < 0:
						for it in itemActual.ItemsPlanEvento.all():
							if it.nItem > cantidad:
								it.delete()

				return redirect('planes')
	else:
		plan = Planes.objects.get(idPlan=request.GET['plan'])
		itemsPlan = plan.ItemsPlan.all()
		nItems = itemsPlan.count()
		initial = {"nombre": plan.nombre}
		
		for itemPlan in itemsPlan:
			initial['item_%d' % (itemPlan.n)] = itemPlan.Item.idItem
			initial['cantidad_%d' % (itemPlan.n)] = itemPlan.cantidad

		form = PlanesForm(nItems, initial=initial)
		nombre_unico = True
		mensaje_error = []
		form_mostrar = MostrarPlanForm(initial={"mostrar": plan.mostrar})

	context = {
		"plan": plan,
		"form_mostrar": form_mostrar,
		"planes_form": form,
		"nItems": nItems,
		"nombre_unico": nombre_unico,
		"mensaje_error": mensaje_error,
	}
	return render(request, 'editar_plan.html', context)


def editar_estacion(request):
	if request.method == 'POST':
		# nueva_estacion = request.POST['nueva_estacion']
		# if nueva_estacion != "-1":
		# 	initial = {}
		# 	for key, value in request.POST.items():
		# 		if "csrf" not in key:
		# 			initial[key] = value
		# 	return custom_redirect('agregar_estacion', editar=initial)

		nombre_unico = True
		estacion = Estaciones.objects.get(idEstacion=request.POST['estacion'])
		nItems = int(request.POST['nItems'])
		form = EstacionesForm(nItems, request.POST, request.FILES)
		
		count = 0
		mensaje_error = []
		values = []
		for key, value in request.POST.items():
			if "item_" in key:
				count += 1
				if value == '-1':
					mensaje_error.append("Elija el item %d " % count)
				elif value in values:
					mensaje_error.append("Se repite el item %d " % count)
				values.append(value)
		if count != int(nItems):
			mensaje_error = []

		if form.is_valid() and count == int(nItems) and mensaje_error == []:
			# verificar uniqueness
			nombre = request.POST['nombre']
			if nombre != estacion.nombre:
				estaciones = Estaciones.objects.all()
				for e in estaciones:
					if e.nombre == nombre:
						nombre_unico = False
						break

			if nombre_unico:
				if estacion.nombre != nombre:
					estacion.nombre = nombre
				estacion.save()


				itemsNuevos = []
				for i in range(1, nItems+1):
					cantidad = int(request.POST["cantidad_%d" % i])
					#for j in range(1, cantidad+1):
					itemsNuevos.append([Items.objects.get(idItem=request.POST["item_%d" % i]), cantidad])

				# Eliminar items que no se encuentran en la nueva lista
				itemsActuales = estacion.ItemsEstacion.all()
				for itemActual in itemsActuales:
					if itemActual.Item.idItem not in [item.idItem for item, cant in itemsNuevos]:
						itemActual.delete()

				# Agregar nuevos items y cambiar cantidades de los existentes
				num = 0
				for nuevoItem, cantidad in itemsNuevos:
					#filtro = planesActuales.filter(Plan=nuevoPlan) #.order_by("n")
					try:
						itemActual = itemsActuales.get(Item=nuevoItem)
					except ItemsEstacion.DoesNotExist:
						itemActual = ItemsEstacion(Estacion=estacion, Item=nuevoItem, cantidad=0)
										
					num += 1
					itemActual.n = num
					itemActual.cantidad = cantidad
					itemActual.save()

				return redirect('estaciones')
	else:
		estacion = Estaciones.objects.get(idEstacion=request.GET['estacion'])
		itemsEstacion = estacion.ItemsEstacion.all()
		nItems = itemsEstacion.count()
		initial = {"nombre": estacion.nombre}
		
		for itemEstacion in itemsEstacion:
			initial['item_%d' % (itemEstacion.n)] = itemEstacion.Item.idItem
			initial['cantidad_%d' % (itemEstacion.n)] = itemEstacion.cantidad

		form = EstacionesForm(nItems, initial=initial)
		nombre_unico = True
		mensaje_error = []

	context = {
		"estacion": estacion,
		"estaciones_form": form,
		"nItems": nItems,
		"nombre_unico": nombre_unico,
		"mensaje_error": mensaje_error,
	}
	return render(request, 'editar_estacion.html', context)


def editar_item(request):
	if request.method == 'POST':
		item = Items.objects.get(idItem=request.POST['item'])
		nombre = request.POST['nombre']
		form = ItemsForm(request.POST, request.FILES)
		if form.is_valid() or item.nombre == nombre:
			#it = form.save(commit=False)
			#it.idItem = item.idItem
			#it.save()
			if item.nombre != nombre:
				item.nombre = nombre

			multiple_anterior = item.multiple
			try:
				request.POST['multiple']
				multiple = True
			except MultiValueDictKeyError:
				multiple = False
			if item.multiple != multiple:
				item.multiple = multiple
			item.save()

			if multiple_anterior and not(multiple):
				for itemPlan in item.ItemsPlan.all():
					for itemPlanEvento in itemPlan.ItemsPlanEvento.all():
						for nItem in range(2, itemPlan.cantidad + 1):
							itemPlanEvento = ItemsPlanEvento(PlanesEvento=itemPlanEvento.PlanesEvento, ItemsPlan=itemPlan, ItemsEstacion=None, nPlan=itemPlanEvento.nPlan, nItem=nItem)
							itemPlanEvento.save()
			elif not(multiple_anterior) and multiple:
				for itemPlan in item.ItemsPlan.all():
					for itemPlanEvento in itemPlan.ItemsPlanEvento.all():
						if itemPlanEvento.nItem > 1:
							itemPlanEvento.delete()

			return redirect('items')
	else:
		item = Items.objects.get(idItem=request.GET['item'])
		form = ItemsForm(initial={'nombre': item.nombre, 'multiple': item.multiple})
	context = {
		"item": item,
		"items_form": form,
	}
	return render(request, 'editar_item.html', context)


def editar_trabajador(request):
	mensaje_error = []
	if request.method == 'POST':
		trabajador = Trabajadores.objects.get(idTrabajador=request.POST["trabajador"])
		nombre = request.POST['nombre']
		rut = request.POST['rut']
		telefono = request.POST['telefono']
		mail = request.POST['mail']
		trabajadores = Trabajadores.objects.all()

		for t in trabajadores:
			if trabajador != t:
				if t.nombre == nombre:
					mensaje_error.append("Ya existe un Trabajador con este Nombre.")
				if t.rut == rut:
					mensaje_error.append("Ya existe un Trabajador con este RUT.")
				if t.telefono == telefono:
					mensaje_error.append("Ya existe un Trabajador con este Teléfono.")
				if t.mail == mail:
					mensaje_error.append("Ya existe un Trabajador con este Mail.")

		form = TrabajadoresForm(request.POST, request.FILES)
		if len(mensaje_error) == 0:
			if trabajador.nombre != nombre:
				trabajador.nombre = nombre
			if trabajador.rut != rut:
				trabajador.rut = rut
			if trabajador.telefono != telefono:
				trabajador.telefono = telefono
			if trabajador.mail != mail:
				trabajador.mail = mail

			trabajador.save()

			return redirect('trabajadores')
	else:
		trabajador = Trabajadores.objects.get(idTrabajador=request.GET["trabajador"])
		initial = {"nombre":trabajador.nombre, "rut":trabajador.rut, "telefono":trabajador.telefono, "mail":trabajador.mail}
		form = TrabajadoresForm(initial=initial)
	context = {
		"trabajador": trabajador,
		"trabajadores_form": form,
		"mensaje_error":mensaje_error,
	}
	return render(request, 'editar_trabajador.html', context)

def editar_contacto(request):
	mensaje_error = []
	if request.method == 'POST':
		contacto = Contactos.objects.get(idContacto=request.POST["contacto"])
		nombre = request.POST['nombre']
		telefono = request.POST['telefono']
		mail = request.POST['mail']
		contactos = Contactos.objects.all()

		for c in contactos:
			if contacto != c:
				if c.nombre == nombre and nombre != "":
					mensaje_error.append("Ya existe un Contacto con este Nombre.")
				if c.telefono == telefono and telefono != "":
					mensaje_error.append("Ya existe un Contacto con este Teléfono.")
				if c.mail == mail and mail != "":
					mensaje_error.append("Ya existe un Contacto con este Mail.")

		form = ContactosFormSelect(request.POST, request.FILES)
		if len(mensaje_error) == 0:
			idCliente = request.POST["Cliente"]
			if idCliente == "":
				contacto.Cliente = None
			else:
				cliente = Clientes.objects.get(idCliente=idCliente)
				if contacto.Cliente != cliente:
					contacto.Cliente = cliente
			if contacto.nombre != nombre:
				contacto.nombre = nombre
			if contacto.telefono != telefono:
				contacto.telefono = telefono
			if contacto.mail != mail:
				contacto.mail = mail

			contacto.save()

			return redirect('contactos')
	else:
		contacto = Contactos.objects.get(idContacto=request.GET["contacto"])
		initial = {"Cliente":contacto.Cliente, "nombre":contacto.nombre, "telefono":contacto.telefono, "mail":contacto.mail}
		form = ContactosFormSelect(initial=initial)
	context = {
		"contacto": contacto,
		"contactos_form": form,
		"mensaje_error":mensaje_error,
	}
	return render(request, 'editar_contacto.html', context)


def editar_cargo(request):
	if request.method == 'POST':
		cargo = Cargos.objects.get(idCargo=request.POST["cargo"])
		nombre = request.POST['nombre']
		form = CargosForm(request.POST, request.FILES)
		if form.is_valid() or cargo.nombre == nombre:
			if cargo.nombre != nombre:
				cargo.nombre = nombre
			n = request.POST["n"]
			if cargo.n != n:
				cargo.n = n
			cargo.save()

			return redirect('cargos')
	else:
		cargo = Cargos.objects.get(idCargo=request.GET["cargo"])
		initial = {"nombre":cargo.nombre, "n":cargo.n}
		form = CargosForm(initial=initial)
	context = {
		"cargo": cargo,
		"cargos_form": form,
	}
	return render(request, 'editar_cargo.html', context)


def editar_recurrente(request):
	if request.method == 'POST':
		recurrente = Recurrentes.objects.get(idRecurrente=request.POST["recurrente"])
		nombre = request.POST['nombre']
		form = RecurrentesForm(request.POST, request.FILES)
		if form.is_valid() or recurrente.nombre == nombre:
			if recurrente.nombre != nombre:
				recurrente.nombre = nombre
			n = request.POST["n"]
			if recurrente.n != n:
				recurrente.n = n
			recurrente.save()

			return redirect('recurrentes')
	else:
		recurrente = Recurrentes.objects.get(idRecurrente=request.GET["recurrente"])
		initial = {"nombre":recurrente.nombre, "n":recurrente.n}
		form = RecurrentesForm(initial=initial)
	context = {
		"recurrente": recurrente,
		"recurrentes_form": form,
	}
	return render(request, 'editar_recurrente.html', context)


def editar_pendiente(request):
	if request.method == 'POST':
		pendiente = Pendientes.objects.get(idPendiente=request.POST["pendiente"])
		nombre = request.POST['nombre']
		form = PendientesForm(request.POST, request.FILES)
		if form.is_valid() or pendiente.nombre == nombre:
			if pendiente.nombre != nombre:
				pendiente.nombre = nombre
			n = request.POST["n"]
			if pendiente.n != n:
				pendiente.n = n
			pendiente.save()

			return redirect('pendientes')
	else:
		pendiente = Pendientes.objects.get(idPendiente=request.GET["pendiente"])
		initial = {"nombre":pendiente.nombre, "n":pendiente.n}
		form = PendientesForm(initial=initial)
	context = {
		"pendiente": pendiente,
		"pendientes_form": form,
	}
	return render(request, 'editar_pendiente.html', context)


def editar_factura(request):
	if request.method == 'POST':
		activacion = Activaciones.objects.get(idActivacion=request.POST["activacion"])
		form = FacturasForm(request.POST, request.FILES)
		if form.is_valid():
			f = form.save(commit=false)
			f.Activacion = activacion
			f.save()

			return redirect('facturas')
	else:
		nFactura = Facturas.objects.first().nFactura + 1
		initial = {
			"nFactura": nFactura,
			"fecha_facturacion": date.today(),
			"pago": 0,
			"plazo": 30,
		}
		try:
			initial["Activacion"] = Activaciones.objects.get(idActivacion=request.GET["activacion"])
		except MultiValueDictKeyError:
			pass
		form = FacturasForm("Adelanto", initial=initial)

	context = {
		#"activacion": activacion,
		"facturas_form": form,
	}
	return render(request, 'agregar_factura.html', context)





################################################################ Eliminar ##################################################################
################################################################ Eliminar ##################################################################

def eliminar_cliente(request):
	cliente = Clientes.objects.get(idCliente=request.GET['cliente'])
	cliente.delete()
	return redirect('clientes')


def eliminar_activacion(request):
	activacion = Activaciones.objects.get(idActivacion=request.GET['Activacion'])
	activacion.delete()
	try:
		return custom_redirect('activaciones', cliente=request.GET['cliente'])
	except MultiValueDictKeyError:
		return redirect('activaciones')

def eliminar_evento(request):
	evento = Eventos.objects.get(idEvento=request.GET['evento'])
	evento.delete()
	try:
		return custom_redirect('eventos', activacion=request.GET['activacion'])
	except MultiValueDictKeyError:
		return redirect('eventos')


def eliminar_contacto(request):
	contacto = Contactos.objects.get(idContacto=request.GET['contacto'])
	contacto.delete()
	try:
		return custom_redirect('activaciones', cliente=request.GET['cliente'])
	except MultiValueDictKeyError:
		return redirect('contactos')


def eliminar_plan(request):
	plan = Planes.objects.get(idPlan=request.GET['plan'])
	plan.delete()
	return redirect('planes')


def eliminar_estacion(request):
	estacion = Estaciones.objects.get(idEstacion=request.GET['estacion'])
	estacion.delete()
	return redirect('estaciones')


def eliminar_item(request):
	item = Items.objects.get(idItem=request.GET['item'])
	item.delete()
	return redirect('items')


def eliminar_trabajador(request):
	trabajador = Trabajadores.objects.get(idTrabajador=request.GET['trabajador'])
	trabajador.delete()
	return redirect('trabajadores')


def eliminar_cargo(request):
	cargo = Cargos.objects.get(idCargo=request.GET['cargo'])
	cargo.delete()
	return redirect('cargos')


def eliminar_recurrente(request):
	recurrente = Recurrentes.objects.get(idRecurrente=request.GET['recurrente'])
	recurrente.delete()
	return redirect('recurrentes')


def eliminar_pendiente(request):
	pendiente = Pendientes.objects.get(idPendiente=request.GET['pendiente'])
	pendiente.delete()
	return redirect('pendientes')


def eliminar_factura(request):
	factura = Facturas.objects.get(nFactura=request.GET['nFactura'])
	factura.delete()
	return redirect('facturas')


def eliminar_ingreso(request):
	ingreso = Ingresos.objects.get(idIngreso=request.GET['idIngreso'])
	ingreso.delete()
	return redirect('ingresos')









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

