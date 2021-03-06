import os, ast
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
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

from django.utils.datastructures import MultiValueDictKeyError
#from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import update_session_auth_hash


#from django.contrib.auth import logout
#def logout_view(request):
#    logout(request)
	# Redirect to a success page.

def is_admin(user):
	permisos = ["admin"]
	return user.TipoUsuario.tipo in permisos

def is_admin_or_staff(user):
	permisos = ["admin", "staff"]
	return user.TipoUsuario.tipo in permisos

def is_admin_or_staff_or_freelance(user):
	permisos = ["admin", "staff", "freelance"]
	return user.TipoUsuario.tipo in permisos




@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def index(request):

	# Satisfaccion del cliente
	eventos = Eventos.objects.all()
	satisfaccion = [eventos.filter(satisfaccion=5), eventos.filter(satisfaccion=4), eventos.filter(satisfaccion=3), eventos.filter(satisfaccion=2), eventos.filter(satisfaccion=1)]
	evaluados = 0.0
	for s in satisfaccion:
		evaluados += s.count()

	# Errores tecnicos
	errores = Errores.objects.all()

	#Eventos proximos
	hoy = date.today()
	eventos_semanas1 = eventos.filter(fecha__gte=hoy, fecha__lte=hoy+timedelta(weeks=1)).order_by("fecha")
	eventos_semanas2 = eventos.filter(fecha__gte=hoy, fecha__lte=hoy+timedelta(weeks=2))
	eventos_mes = eventos.filter(fecha__gte=hoy, fecha__lte=hoy+relativedelta(months=1))
	eventos_todos = eventos.filter(fecha__gte=hoy)

	resumen7 = []
	for ev in eventos_semanas1:
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


	# Bar Chart: Facturacion mensual
	nMeses = 6
	mes = (hoy - relativedelta(months=nMeses)).replace(day=1)
	facturacion_mensual_meses = [0]*nMeses
	facturacion_mensual_data_facturado = [0]*nMeses
	facturacion_mensual_data_pagado = [0]*nMeses
	facturacion_mensual_metas = [0]*nMeses

	facturas = Facturas.objects.all()
	facturas_pagadas = Facturas.pagadas()[0]
	metas = Metas.objects.filter(mes__gt=hoy - relativedelta(months=nMeses)).reverse()
	#if len(metas) < nMeses:
	#	metas = metas.reverse()

	for i in range(nMeses):
		mes = mes + relativedelta(months=1)
		facturas_mes = facturas.filter(fecha_facturacion__gte=mes, fecha_facturacion__lt=mes+relativedelta(months=1))

		data_facturado = 0
		data_pagado = 0
		for factura in facturas_mes:
			data_facturado += factura.montoIVA
			for ingreso in factura.Ingresos.all():
				data_pagado += ingreso.monto

		facturacion_mensual_meses[i] = mes #mes.strftime("%B")
		facturacion_mensual_data_facturado[i] = data_facturado
		facturacion_mensual_data_pagado[i] = data_pagado
		if len(metas) > i:
			facturacion_mensual_metas[i] = metas[i].meta


	# Pie Chart: Ventas por tipo de evento: Total
	activaciones = Activaciones.objects.all()
	tipos_evento = ["Pixz", "Weddi", "Producción", "Tech"]
	monto_tipos_total = [0]*len(tipos_evento)
	i = 0
	for tipo in tipos_evento:
		for activacion in activaciones.filter(tipo=tipo):
			monto_tipos_total[i] += activacion.montoIVA
		i+=1

	# Pie Chart: Ventas por tipo de evento: Anual
	monto_tipos_meses = [0]*len(tipos_evento)
	i = 0
	for tipo in tipos_evento:
		for activacion in activaciones.filter(tipo=tipo):
			for factura in activacion.Facturas.filter(fecha_facturacion__gte=hoy.replace(day=1)-relativedelta(months=nMeses)):
				monto_tipos_meses[i] += factura.montoIVA
		i+=1



	context = {
		"errores": errores,
		"resumen7": resumen7,
		"eventos_semanas2": eventos_semanas2.count(),
		"eventos_mes": eventos_mes.count(),
		"eventos_todos": eventos_todos.count(),
		"s5": satisfaccion[0].count(),
		"s4": satisfaccion[1].count(),
		"s3": satisfaccion[2].count(),
		"s2": satisfaccion[3].count(),
		"s1": satisfaccion[4].count(),
		#"facturacion_mensual_meses": facturacion_mensual_meses,
		"facturacion_mensual_data_facturado": facturacion_mensual_data_facturado,
		"facturacion_mensual_data_pagado": facturacion_mensual_data_pagado,
		"facturacion_mensual_metas": facturacion_mensual_metas,
		"tipos_evento": tipos_evento,
		"monto_tipos_total": monto_tipos_total,
		"monto_tipos_meses": monto_tipos_meses,
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

	i=1
	for m in facturacion_mensual_meses:
		context["mes" + str(i)] = m
		i+=1

	#i=1
	#for t in tipos_evento:
	#	context["tipo" + str(i)] = t
	#	i+=1

	return render(request, 'index.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def calendario(request):
	hoy = date.today()
	eventos = Eventos.objects.filter(fecha__gte=hoy, fecha__lte=hoy+timedelta(weeks=1)).order_by("fecha")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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
		titulos = ["#","Activación", "Tipo", "Monto", "Monto + IVA", "Descripción"]
		contactos = cliente.Contactos.all()
		titulos_contactos = ["#", "Nombre", "Teléfono", "Mail"]
	except MultiValueDictKeyError:
		idCliente = ""
		cliente = ""
		activaciones = Activaciones.objects.all()
		titulos = ["#", "Cliente","Activación", "Tipo", "Monto", "Monto + IVA", "Facturas", "Descripción", "Facturación"]
		contactos = None
		titulos_contactos = None

	pendientes = []
	venta = 0
	for act in activaciones:
		venta += act.montoIVA
		if act.Eventos.filter(fecha__gte=date.today()).count() > 0:
			pendientes.append(act)

	p1=Activaciones.por_cobrar()
	monto_p1 = 0
	for a in p1:
		monto_p1 += a.montoIVA
		for i in a.Ingresos.all():
			monto_p1 -= i.monto
	p2=Activaciones.por_vencer()
	monto_p2 = 0
	for a in p2:
		monto_p2 += a.montoIVA
		for i in a.Ingresos.all():
			monto_p2 -= i.monto
	p3=Activaciones.vencidas()
	monto_p3 = 0
	for a in p3:
		monto_p3 += a.montoIVA
		for i in a.Ingresos.all():
			monto_p3 -= i.monto

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
		"por_cobrar": monto_p1,
		"por_vencer": monto_p2,
		"vencidas": monto_p3,
	}
	return render(request, 'activaciones.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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
				if activacion.tipo == "Weddi":
					activacion.montoIVA = activacion.monto
				else:
					activacion.montoIVA = activacion.monto*1.19
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


class eventos(LoginRequiredMixin, UserPassesTestMixin, ListView):
	def test_func(self):
		return is_admin_or_staff(self.request.user)
	def get_login_url(self):
		if not self.request.user.is_authenticated:
			return super(eventos, self).get_login_url()
		else:
			return "/no_autorizado/"

	model = Eventos
	context_object_name = "eventos"
	template_name = "eventos.html"
	#paginate_by = 100  # if pagination is desired

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		eventos = Eventos.objects.all()
		totales = eventos.count()

		hoy = date.today()
		context['pendientes'] = eventos.filter(fecha__gte=hoy).count()

		
		
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
		
		context['filtrados'] = eventos.count()
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
@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def planes(request):
	planes = Planes.objects.all()
	
	titulos = ["#", "Plan", "Items", "Elegible"]

	context = {
		"planes": planes,
		"titulos": titulos,
	}
	return render(request, 'planes.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def estaciones(request):
	estaciones = Estaciones.objects.all()
	
	titulos = ["#", "Estación", "Items"]

	context = {
		"estaciones": estaciones,
		"titulos": titulos,
	}
	return render(request, 'estaciones.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def items(request):
	items = Items.objects.all()
	
	titulos = ["#", "Item", "Multiple"]

	context = {
		"items": items,
		"titulos": titulos,
	}
	return render(request, 'items.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def trabajadores(request):
	trabajadores = Trabajadores.objects.all()
	
	titulos = ["#", "Nombre", "RUT", "Teléfono", "Mail"]

	context = {
		"trabajadores": trabajadores,
		"titulos": titulos,
	}
	return render(request, 'trabajadores.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def contactos(request):
	contactos = Contactos.objects.all()
	
	titulos = ["#", "Nombre", "Cliente", "RUT", "Teléfono", "Mail"]

	context = {
		"contactos": contactos,
		"titulos": titulos,
	}
	return render(request, 'contactos.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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



@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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



@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def cargos(request):
	cargos = Cargos.objects.all()
	
	#titulos = ["#", "Nombre", "RUT", "Teléfono", "Mail"]

	context = {
		"cargos": cargos,
		#"titulos": titulos,
	}
	return render(request, 'cargos.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def recurrentes(request):
	recurrentes = Recurrentes.objects.all()
	
	#titulos = ["#", "Nombre", "RUT", "Teléfono", "Mail"]

	context = {
		"recurrentes": recurrentes,
		#"titulos": titulos,
	}
	return render(request, 'recurrentes.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def pendientes(request):
	pendientes = Pendientes.objects.all()
	
	context = {
		"pendientes": pendientes,
		#"titulos": titulos,
	}
	return render(request, 'pendientes.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def facturas_OLD(request):
	facturas = Facturas.objects.all()
	
	f=facturas.get(nFactura=4)
	
	context = {
		"facturas": facturas,
		#"titulos": titulos,
	}
	return render(request, 'facturas.html', context)

class facturas(LoginRequiredMixin, UserPassesTestMixin, ListView):
	def test_func(self):
		return is_admin_or_staff(self.request.user)
	def get_login_url(self):
		if not self.request.user.is_authenticated:
			return super(facturas, self).get_login_url()
		else:
			return "/no_autorizado/"

	model = Facturas
	context_object_name = "facturas"
	template_name = "facturas.html"
	#paginate_by = 100  # if pagination is desired

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		hoy = date.today()
		pendientes = Facturas.pendientes()[0]
		
		orden = self.request.GET.get("orden", "fecha_pago")
		estado = self.request.GET.get("estado", "pendientes")
		nFactura = self.request.GET.get("nFactura", "")
		# desde_year = int(self.request.GET.get("desde_year", -1))
		# desde_month = int(self.request.GET.get("desde_month", -1))
		# desde_day = int(self.request.GET.get("desde_day", -1))
		# hasta_year = int(self.request.GET.get("hasta_year", -1))
		# hasta_month = int(self.request.GET.get("hasta_month", -1))
		# hasta_day = int(self.request.GET.get("hasta_day", -1))
		# documento = self.request.GET.get("documento", "")
		# tipo = self.request.GET.get("tipo", "")
		

		if estado == "pendientes":
			facturas = pendientes
		elif estado == "pagadas":
			facturas = Facturas.pagadas()[0]
		else:
			facturas = Facturas.objects.all()

		if nFactura != "":
			facturas = facturas.filter(nFactura=int(nFactura))

		# if (desde_year != -1 and desde_month != -1 and desde_day != -1):
		# 	desde = date(desde_year, desde_month, desde_day)
		# else:
		# 	desde = hoy.replace(day=1)
		# facturas = facturas.filter(fecha_pago__gte=desde)
		
		# if (hasta_year != -1 and hasta_month != -1 and hasta_day != -1):
		# 	hasta = date(hasta_year, hasta_month, hasta_day)
		# else:
		# 	hasta = hoy
		# facturas = facturas.filter(fecha_pago__lte=hasta)

		# if documento != "":
		# 	costos = costos.filter(documento=documento)
		# if tipo != "":
		# 	costos = costos.filter(Tipo__nombre__icontains=tipo)
		
		
		facturas = facturas.order_by(orden)
		context['facturas'] = facturas
		context['orden'] = orden
		initial = {
			"estado": estado,
			"nFactura": nFactura,
			# "desde": desde,
			# "hasta": hasta,
		}
		context['filtros'] = filtroFacturasForm(initial=initial)

		filtrado = 0
		for factura in facturas:
			filtrado += factura.montoIVA
		context["filtrado"] = filtrado
		pendiente = 0
		vencidas = 0
		for factura in pendientes:
			pendiente += factura.montoIVA
			if hoy > factura.fecha_pago:
				vencidas += factura.montoIVA
			ingresos = factura.Ingresos.all()
			for ingreso in ingresos:
				pendiente -= ingreso.monto
				if hoy > factura.fecha_pago:
					vencidas -= ingreso.monto
		context["pendientes"] = pendiente
		context["vencidas"] = vencidas


		return context



@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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
				factura = Facturas(nFactura=nFactura, Activacion=act, fecha_facturacion=fecha_facturacion, monto=monto, montoIVA=monto*1.19, fecha_pago=fecha_pago)
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def ingresos(request):
	ingresos = Ingresos.objects.all()
	
	context = {
		"ingresos": ingresos,
		#"titulos": titulos,
	}
	return render(request, 'ingresos.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def agregar_ingreso(request):
	mensaje_error = ""
	if request.method == 'POST':
		factura = request.POST["factura"]
		form = IngresosForm(factura, request.POST, request.FILES)
		if form.is_valid():
			activacion = request.POST["activacion"]
			act = Activaciones.objects.get(idActivacion=activacion)
			
			monto = int(request.POST["monto"])

			ingresos_totales = act.Ingresos.all()
			monto_restante_total = act.montoIVA
			for i in ingresos_totales:
				monto_restante_total -= i.monto

			monto_restante = 0
			if factura == "-":
				fact = None
				facturas = act.Facturas.all()
				monto_restante = act.montoIVA
				for f in facturas:
					monto_restante -= f.montoIVA
			elif factura != "Weddi":
				fact = Facturas.objects.get(nFactura=factura)
				ingresos = fact.Ingresos.all()
				monto_restante = fact.montoIVA
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
			monto_restante = act.montoIVA
			for f in facturas:
				monto_restante -= f.montoIVA
		elif factura == "Weddi":
			act = Activaciones.objects.get(idActivacion=activacion)
			ingresos = act.Ingresos.all()
			monto_restante = act.monto
			for i in ingresos:
				monto_restante -= i.monto
		else:
			fact = Facturas.objects.get(nFactura=factura)
			ingresos = fact.Ingresos.all()
			monto_restante = fact.montoIVA
			for i in ingresos:
				monto_restante -= i.monto

		initial = {
			"monto": monto_restante,
			"fecha": date.today(),
		}
		form = IngresosForm(factura, initial=initial)

	context = {
		"activacion": activacion,
		"factura": factura,
		"ingresos_form": form,
		"mensaje_error": mensaje_error,
	}
	return render(request, 'agregar_ingreso.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


#@login_required
#@user_passes_test(is_admin_or_staff_or_freelance, login_url="/no_autorizado/")
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
	
	eventos = eventos.order_by("fecha_desinstalacion")
	fecha_fin = eventos.last().fecha_desinstalacion + timedelta(days=1)
	eventos = eventos.order_by("fecha_instalacion")
	fecha_inicio = eventos.last().fecha_instalacion
	
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
		
		# fecha = -1
		# for ev in eventos:
		# 	if ev.fecha != fecha:
		# 		fecha = ev.fecha
		# 		itinerario.append([])
		# 		dias.append(fecha)

		# 		for evento in eventos.filter(fecha=fecha):
		# 			itinerario[-1].append([evento.hora_instalacion, "INSTALACIÓN", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
		# 			itinerario[-1].append([evento.inicio_servicio, "INICIO SERVICIO", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
		# 			itinerario[-1].append([evento.fin_servicio, "FIN SERVICIO", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
		# 			itinerario[-1].append([evento.hora_desinstalacion, "DESINSTALACIÓN", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])

		# 		itinerario[-1].sort(key=lambda x: x[0])

		fecha = fecha_inicio
		evs_fin_servicio = []

		while fecha != fecha_fin:
			evs_instalacion = eventos.filter(fecha_instalacion=fecha)
			evs_evento = eventos.filter(fecha=fecha)
			evs_desinstalacion = eventos.filter(fecha_desinstalacion=fecha)

			if evs_instalacion.count() > 0 or evs_evento.count() > 0  or evs_desinstalacion.count() > 0 or len(evs_fin_servicio) > 0:
				itinerario.append([])
				dias.append(fecha)


				for evento in evs_fin_servicio:
					itinerario[-1].append([evento.fin_servicio, "FIN SERVICIO", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
				evs_fin_servicio = []

				for evento in evs_instalacion:
					itinerario[-1].append([evento.hora_instalacion, "INSTALACIÓN", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])

				for evento in evs_evento:
					itinerario[-1].append([evento.inicio_servicio, "INICIO SERVICIO", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
					if evento.inicio_servicio < evento.fin_servicio: # (en el mismo dia)
						itinerario[-1].append([evento.fin_servicio, "FIN SERVICIO", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
					else:
						evs_fin_servicio.append(evento)
						#itinerario[-1].append([evento.fin_servicio, "FIN SERVICIO", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])
						
				for evento in evs_desinstalacion:
					itinerario[-1].append([evento.hora_desinstalacion, "DESINSTALACIÓN", evento, "*&*&*".join([plan.nombre for plan in evento.Planes.all()])])

				itinerario[-1].sort(key=lambda x: x[0])

			fecha += timedelta(days=1)


	context = {
		"eventos": eventos,
		"itinerario": itinerario,
		"dias": dias,
		"errores_info": errores_info,
	}
	return render(request, 'itinerario.html', context)



class costos_variables(LoginRequiredMixin, UserPassesTestMixin, ListView):
	def test_func(self):
		return is_admin_or_staff(self.request.user)
	def get_login_url(self):
		if not self.request.user.is_authenticated:
			return super(costos_variables, self).get_login_url()

	model = CostosVariables
	context_object_name = "costos"
	template_name = "costos_variables.html"
	#paginate_by = 100  # if pagination is desired

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		costos = CostosVariables.objects.all()

		hoy = date.today()
		total_este_mes = 0
		for costo in costos:
			if costo.fecha.month == hoy.month:
				total_este_mes += costo.monto
		context["total_este_mes"] = total_este_mes
		
		orden = self.request.GET.get("orden", "-fecha")
		desde_year = int(self.request.GET.get("desde_year", -1))
		desde_month = int(self.request.GET.get("desde_month", -1))
		desde_day = int(self.request.GET.get("desde_day", -1))
		hasta_year = int(self.request.GET.get("hasta_year", -1))
		hasta_month = int(self.request.GET.get("hasta_month", -1))
		hasta_day = int(self.request.GET.get("hasta_day", -1))
		documento = self.request.GET.get("documento", "")
		tipo = self.request.GET.get("tipo", "")
		evento = self.request.GET.get("evento", "")


		if documento != "":
			costos = costos.filter(documento=documento)
		
		if (desde_year != -1 and desde_month != -1 and desde_day != -1):
			desde = date(desde_year, desde_month, desde_day)
		else:
			desde = hoy.replace(day=1)
		costos = costos.filter(fecha__gte=desde)
		
		if (hasta_year != -1 and hasta_month != -1 and hasta_day != -1):
			hasta = date(hasta_year, hasta_month, hasta_day)
		else:
			hasta = hoy
		costos = costos.filter(fecha__lte=hasta)

		if tipo != "":
			costos = costos.filter(Tipo__nombre__icontains=tipo)
		if evento != "":
			costos = costos.filter(Evento__idEvento=evento)
		
		costos = costos.order_by(orden)
		context['costos'] = costos
		context['orden'] = orden
		initial = {
			"desde": desde,
			"hasta": hasta,
			"documento": documento,
			"tipo": tipo,
			"evento": evento,
		}
		context['filtros'] = filtroCostosVariablesForm(initial=initial)

		filtrado = 0
		for costo in costos:
			filtrado += costo.monto
		context["filtrado"] = filtrado

		return context


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def agregar_costo_variable(request):
	if request.method == 'POST':
		form = costosVariablesForm(request.POST, request.FILES)
		if form.is_valid():
			costo = form.save()
			return redirect('costos_variables')
	else:
		initial = {"fecha": date.today()}
		form = costosVariablesForm(initial=initial)
	context = {
		"costos_variables_form": form,
	}
	return render(request, 'agregar_costo_variable.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def tipos_costo_variable(request):
	tipos = TiposCostoVariable.objects.all()
	
	titulos = ["#", "Costo"]

	context = {
		"tipos": tipos,
		"titulos": titulos,
	}
	return render(request, 'tipos_costo_variable.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def agregar_tipo_costo_variable(request):
	if request.method == 'POST':
		form = tiposCostoVariableForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('tipos_costo_variable')
	else:
		form = tiposCostoVariableForm()
	context = {
		"tipos_costo_variable_form": form,
	}
	return render(request, 'agregar_tipo_costo_variable.html', context)


class metas(LoginRequiredMixin, UserPassesTestMixin, ListView):
	def test_func(self):
		return is_admin_or_staff(self.request.user)
	def get_login_url(self):
		if not self.request.user.is_authenticated:
			return super(costos_variables, self).get_login_url()

	model = Metas
	context_object_name = "metas"
	template_name = "metas.html"
	#paginate_by = 100  # if pagination is desired

	def post(self, request, *args, **kwargs):
		metas = Metas.objects.all()
		agregar_o_quitar_meses = self.request.POST['agregar_o_quitar_meses']
		if agregar_o_quitar_meses == "agregar":
			if len(metas) == 0:
				Metas(mes=(date.today().replace(day=1) - relativedelta(months=5))).save()
			else:
				Metas(mes=(metas[0].mes + relativedelta(months=1))).save()
		elif agregar_o_quitar_meses == "quitar":
			metas[0].delete()
		else:
			for i in range(len(metas)):
				meta = int(self.request.POST['meta_%d' % i])
				if meta != metas[i].meta:
					metas[i].meta = meta
					metas[i].save()

		return redirect('metas')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		metas = Metas.objects.all()
		
		form = metasForm()

		context["metas"] = metas
		context["metas_form"] = form

		return context
























############################################################## Editar ##############################################################
############################################################## Editar ##############################################################

@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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
			if a.tipo == "Weddi":
				a.montoIVA = a.monto
			else:
				a.montoIVA = a.monto*1.19
			a.save()

			if menuCliente != "":
				return custom_redirect('activaciones', cliente=menuCliente)
			else:
				return redirect('activaciones')
	else:
		activacion = Activaciones.objects.get(idActivacion=request.GET['Activacion'])
		form = ActivacionesSelectForm(initial={"Cliente":activacion.Cliente, "nombre": activacion.nombre, "monto":activacion.monto,"descripcion": activacion.descripcion, "tipo": activacion.tipo})
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
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


# def editar_factura(request):
# 	if request.method == 'POST':
# 		activacion = Activaciones.objects.get(idActivacion=request.POST["activacion"])
# 		form = FacturasForm(request.POST, request.FILES)
# 		if form.is_valid():
# 			f = form.save(commit=false)
# 			f.Activacion = activacion
# 			f.save()

# 			return redirect('facturas')
# 	else:
# 		nFactura = Facturas.objects.first().nFactura + 1
# 		initial = {
# 			"nFactura": nFactura,
# 			"fecha_facturacion": date.today(),
# 			"pago": 0,
# 			"plazo": 30,
# 		}
# 		try:
# 			initial["Activacion"] = Activaciones.objects.get(idActivacion=request.GET["activacion"])
# 		except MultiValueDictKeyError:
# 			pass
# 		form = FacturasForm("Adelanto", initial=initial)

# 	context = {
# 		#"activacion": activacion,
# 		"facturas_form": form,
# 	}
# 	return render(request, 'agregar_factura.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def editar_costo_variable(request):
	if request.method == 'POST':
		costo = CostosVariables.objects.get(idCostoVariable=request.POST["costo"])
		form = costosVariablesForm(request.POST, request.FILES)
		if form.is_valid():
			costo.documento = request.POST["documento"]
			if request.POST["Tipo"] == "":
				costo.Tipo = None
			else:
				costo.Tipo = TiposCostoVariable.objects.get(idTipoCostoVariable=request.POST["Tipo"])
			costo.monto = request.POST["monto"]
			
			if request.POST["Evento"] == "":
				costo.Evento = None
			else:
				costo.Evento = Eventos.objects.get(idEvento=request.POST["Evento"])
			costo.fecha = date(int(request.POST['fecha_year']), int(request.POST['fecha_month']), int(request.POST['fecha_day']))  #year, month, day
			costo.comentarios = request.POST["comentarios"]
			costo.save()

			return redirect('costos_variables')
	else:
		costo = CostosVariables.objects.get(idCostoVariable=request.GET["costo"])
		initial = {"documento": costo.documento, "Tipo": costo.Tipo, "monto": costo.monto, "Evento": costo.Evento, "fecha": costo.fecha, "comentarios": costo.comentarios}
		form = costosVariablesForm(initial=initial)
	context = {
		"costo": costo,
		"costos_variables_form": form,
	}
	return render(request, 'editar_costo_variable.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def editar_tipo_costo_variable(request):
	if request.method == 'POST':
		tipo = TiposCostoVariable.objects.get(idTipoCostoVariable=request.POST["tipo"])
		nombre = request.POST['nombre']
		form = tiposCostoVariableForm(request.POST, request.FILES)
		if form.is_valid() or tipo.nombre == nombre:
			if tipo.nombre != nombre:
				tipo.nombre = nombre
			tipo.save()

			return redirect('tipos_costo_variable')
	else:
		tipo = TiposCostoVariable.objects.get(idTipoCostoVariable=request.GET["tipo"])
		initial = {"nombre":tipo.nombre}
		form = tiposCostoVariableForm(initial=initial)
	context = {
		"tipo": tipo,
		"tipos_costo_variable_form": form,
	}
	return render(request, 'editar_tipo_costo_variable.html', context)





















################################################################ Eliminar ##################################################################
################################################################ Eliminar ##################################################################

@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_cliente(request):
	cliente = Clientes.objects.get(idCliente=request.GET['cliente'])
	cliente.delete()
	return redirect('clientes')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_activacion(request):
	activacion = Activaciones.objects.get(idActivacion=request.GET['Activacion'])
	activacion.delete()
	try:
		return custom_redirect('activaciones', cliente=request.GET['cliente'])
	except MultiValueDictKeyError:
		return redirect('activaciones')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_evento(request):
	evento = Eventos.objects.get(idEvento=request.GET['evento'])
	evento.delete()
	try:
		return custom_redirect('eventos', activacion=request.GET['activacion'])
	except MultiValueDictKeyError:
		return redirect('eventos')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_contacto(request):
	contacto = Contactos.objects.get(idContacto=request.GET['contacto'])
	contacto.delete()
	try:
		return custom_redirect('activaciones', cliente=request.GET['cliente'])
	except MultiValueDictKeyError:
		return redirect('contactos')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_plan(request):
	plan = Planes.objects.get(idPlan=request.GET['plan'])
	plan.delete()
	return redirect('planes')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_estacion(request):
	estacion = Estaciones.objects.get(idEstacion=request.GET['estacion'])
	estacion.delete()
	return redirect('estaciones')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_item(request):
	item = Items.objects.get(idItem=request.GET['item'])
	item.delete()
	return redirect('items')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_trabajador(request):
	trabajador = Trabajadores.objects.get(idTrabajador=request.GET['trabajador'])
	trabajador.delete()
	return redirect('trabajadores')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_cargo(request):
	cargo = Cargos.objects.get(idCargo=request.GET['cargo'])
	cargo.delete()
	return redirect('cargos')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_recurrente(request):
	recurrente = Recurrentes.objects.get(idRecurrente=request.GET['recurrente'])
	recurrente.delete()
	return redirect('recurrentes')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_pendiente(request):
	pendiente = Pendientes.objects.get(idPendiente=request.GET['pendiente'])
	pendiente.delete()
	return redirect('pendientes')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_factura(request):
	factura = Facturas.objects.get(nFactura=request.GET['nFactura'])
	factura.delete()
	return redirect('facturas')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_ingreso(request):
	ingreso = Ingresos.objects.get(idIngreso=request.GET['idIngreso'])
	ingreso.delete()
	return redirect('ingresos')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_costo_variable(request):
	costo = CostosVariables.objects.get(idCostoVariable=request.GET['costo'])
	costo.delete()
	return redirect('costos_variables')


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def eliminar_tipo_costo_variable(request):
	tipo = TiposCostoVariable.objects.get(idTipoCostoVariable=request.GET['tipo'])
	tipo.delete()
	return redirect('tipos_costo_variable')


























################################################################ Otros ##################################################################
################################################################ Otros ##################################################################


def custom_redirect(url_name, *args, **kwargs):
	url = reverse(url_name, args=args)
	params = urlencode(kwargs)
	return HttpResponseRedirect(url + "?%s" % params)


@login_required
@user_passes_test(is_admin, login_url="/no_autorizado/")
def editar_password(request):
	edit = ""
	mensaje_error = ""
	if request.method == 'POST':
		password = request.POST["password"]
		confirm_password = request.POST["confirm_password"]
		form = editarPasswordForm(request.POST, request.FILES)
		if form.is_valid() and password == confirm_password:
			usuario = auth.models.User.objects.get(username=request.POST["username"])
			usuario.set_password(password)
			usuario.save()
			update_session_auth_hash(request, usuario)

			return custom_redirect('editar_password', edit="success")
		else:
			mensaje_error = "Contraseñas no coinciden, inténtalo de nuevo."
	
	else:
		try:
			edit = request.GET["edit"]
		except:
			pass
		form = editarPasswordForm()
	context = {
		"editar_password_form": form,
		"edit": edit,
		"mensaje_error": mensaje_error,
	}
	return render(request, 'editar_password.html', context)

def no_autorizado(request):
	return render(request, 'no_autorizado.html')


import pandas
import openpyxl
#import django_pandas
@login_required
@user_passes_test(is_admin, login_url="/no_autorizado/")
def to_excel(request):
	filename = 'Resumen.xlsx'
	path = os.path.join(settings.MEDIA_ROOT, filename)
	writer = pandas.ExcelWriter(path)

	clientes = Clientes.objects.all()
	clientes_matrix = []
	clientes_index = []
	for cliente in clientes:
		clientes_index.append(cliente.idCliente)
		clientes_matrix.append([cliente.nombre, 
								cliente.direccion])
	df_clientes = pandas.DataFrame(data=clientes_matrix, index=clientes_index, columns=["Nombre", "Dirección"])
	df_clientes.to_excel(writer, "Clientes")

	activaciones = Activaciones.objects.all()
	activaciones_matrix = []
	activaciones_index = []
	for activacion in activaciones:
		facturas = []
		pagadas = []
		pendientes = []
		for factura in activacion.Facturas.all():
			facturas.append(str(factura.nFactura))
			if factura.pagada():
				pagadas.append(str(factura.nFactura))
			else:
				pendientes.append(str(factura.nFactura))

		activaciones_index.append(activacion.idActivacion)
		activaciones_matrix.append([activacion.Cliente.nombre,
									activacion.nombre, 
									activacion.tipo, 
									activacion.monto, 
									activacion.montoIVA, 
									" ".join(facturas), 
									" ".join(pagadas), 
									" ".join(pendientes), 
									activacion.descripcion])
	df_activaciones = pandas.DataFrame(data=activaciones_matrix, index=activaciones_index, columns=["Cliente", "Activación", "Tipo", "Monto", "Monto + IVA", "Facturas", "Pagadas", "Pendientes", "Descripción"])
	df_activaciones.to_excel(writer, "Activaciones")

	eventos = Eventos.objects.all()
	eventos_matrix = []
	eventos_index = []
	for evento in eventos:
		eventos_index.append(evento.idEvento)
		eventos_matrix.append([evento.estado,
									evento.Activacion.Cliente.nombre, 
									evento.Activacion.nombre,
									evento.nombre,
									evento.fecha.strftime('%d/%m/%Y'),
									evento.horas,
									" / ".join([(str(planEvento.cantidad) + " " + planEvento.Plan.nombre) for planEvento in evento.PlanesEvento.all()]), 
									evento.comentarios])
	df_eventos = pandas.DataFrame(data=eventos_matrix, index=eventos_index, columns=["Estado", "Cliente", "Activación", "Evento", "Fecha", "Horas", "Planes", "Comentarios"])
	df_eventos.to_excel(writer, "Eventos")

	facturas = Facturas.objects.all()
	facturas_matrix = []
	facturas_index = []
	for factura in facturas:
		facturas_index.append(factura.nFactura)
		facturas_matrix.append([factura.nFactura,
								" - " if factura.Activacion==None else " - " if factura.Activacion.Cliente==None else factura.Activacion.Cliente.nombre,
								" - " if factura.Activacion==None else factura.Activacion.nombre,
								factura.fecha_facturacion.strftime('%d/%m/%Y'),
								factura.monto,
								factura.montoIVA,
								factura.fecha_pago.strftime('%d/%m/%Y')])
	df_facturas = pandas.DataFrame(data=facturas_matrix, index=facturas_index, columns=["N° de Factura", "Cliente", "Activación", "Fecha de facturación", "Monto", "Monto + IVA", "Fecha de pago"])
	df_facturas.to_excel(writer, "Facturas")

	ingresos = Ingresos.objects.all().order_by("-idIngreso")
	ingresos_matrix = []
	ingresos_index = []
	for ingreso in ingresos:
		ingresos_index.append(ingreso.idIngreso)
		ingresos_matrix.append([" - " if ingreso.Factura==None else ingreso.Factura.nFactura,
								" - " if ingreso.Activacion==None else " - " if ingreso.Activacion.Cliente==None else ingreso.Activacion.Cliente.nombre,
								" - " if ingreso.Activacion==None else ingreso.Activacion.nombre,
								ingreso.fecha.strftime('%d/%m/%Y'),
								ingreso.monto,
								ingreso.comentarios])
	df_ingresos = pandas.DataFrame(data=ingresos_matrix, index=ingresos_index, columns=["N° de Factura", "Cliente", "Activación", "Fecha", "Monto", "Comentarios"])
	df_ingresos.to_excel(writer, "Ingresos")

	costos_variables = CostosVariables.objects.all().order_by("-idCostoVariable")
	costos_variables_matrix = []
	costos_variables_index = []
	for costo_variable in costos_variables:
		costos_variables_index.append(costo_variable.idCostoVariable)
		costos_variables_matrix.append([costo_variable.documento,
								" - " if costo_variable.Tipo==None else costo_variable.Tipo.nombre,
								costo_variable.monto,
								" - " if costo_variable.Evento==None else costo_variable.Evento.nombre,
								costo_variable.fecha.strftime('%d/%m/%Y'),
								costo_variable.comentarios])
	df_costos_variables = pandas.DataFrame(data=costos_variables_matrix, index=costos_variables_index, columns=["Documento", "Tipo", "Monto", "Evento", "Fecha", "Comentarios"])
	df_costos_variables.to_excel(writer, "Costos Variables")

	trabajadores = Trabajadores.objects.all().order_by("idTrabajador")
	trabajadores_matrix = []
	trabajadores_index = []
	for trabajador in trabajadores:
		trabajadores_index.append(trabajador.idTrabajador)
		trabajadores_matrix.append([trabajador.nombre,
									trabajador.rut,
									trabajador.telefono,
									trabajador.mail])
	df_trabajadores = pandas.DataFrame(data=trabajadores_matrix, index=trabajadores_index, columns=["Nombre", "RUT", "Teléfono", "Mail"])
	df_trabajadores.to_excel(writer, "Trabajadores")

	contactos = Contactos.objects.all().order_by("idContacto")
	contactos_matrix = []
	contactos_index = []
	for contacto in contactos:
		contactos_index.append(contacto.idContacto)
		contactos_matrix.append([contacto.nombre,
									" - " if contacto.Cliente==None else contacto.Cliente.nombre,
									contacto.telefono,
									contacto.mail])
	df_contactos = pandas.DataFrame(data=contactos_matrix, index=contactos_index, columns=["Nombre", "Cliente", "Teléfono", "Mail"])
	df_contactos.to_excel(writer, "Contactos")

	errores = Errores.objects.all()
	errores_matrix = []
	errores_index = []
	for error in errores:
		errores_index.append(error.idError)
		errores_matrix.append([" - " if error.Evento==None else error.Evento.idEvento,
									error.error,
									"Si" if error.resuelto else "No"])
	df_contactos = pandas.DataFrame(data=errores_matrix, index=errores_index, columns=["Evento", "Error", "Resuelto"])
	df_contactos.to_excel(writer, "Errores técnicos")

	writer.save()

	if os.path.exists(path):
		excel = open(path, "rb")
		data = excel.read()
		response = HttpResponse(data, content_type="application/vnd.ms-excel")
		response['Content-Disposition'] = 'attachment; filename=' + filename
		return response


@login_required
@user_passes_test(is_admin_or_staff, login_url="/no_autorizado/")
def resolver_error(request):
	error = Errores.objects.get(idError=request.GET['error'])
	if request.GET['resuelto'] == 'true':
		error.resuelto = True
	elif request.GET['resuelto'] == 'false':
		error.resuelto = False
	error.save()
	return redirect('index')

