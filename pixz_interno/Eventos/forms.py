import datetime
from django import forms

from .models import *

#fields = ['Titulo', 'Descripcion', 'Foto', ]
#exclude = ['campo1', 'campo2', ]

class ClientesForm(forms.ModelForm):
	class Meta:
		model = Clientes
		
		exclude = []
		widgets = {
			#'Calle': forms.TextInput(attrs={'onchange': "return codeAddress();"}),
			#'numeroCalle': forms.TextInput(attrs={'onchange': "return codeAddress();"}),
		}


class ActivacionesForm(forms.ModelForm):
	class Meta:
		model = Activaciones
		
		exclude = ["Cliente"]
		widgets = {
			"descripcion": forms.Textarea(attrs={'rows': 4}),
		}


# Opcional, con elección del cliente en un dropdown.
class ActivacionesSelectForm(forms.ModelForm):
	class Meta:
		model = Activaciones
		
		exclude = []
		widgets = {
			"descripcion": forms.Textarea(attrs={'rows': 4}),
		}

	def __init__(self, *args, **kwargs):
		super(ActivacionesSelectForm, self).__init__(*args, **kwargs)
		#self.fields['user'].queryset = User.objects.all()
		self.fields['Cliente'].label_from_instance = lambda obj: obj.nombre # lambda obj: "%s %s" % (obj.last_name, obj.first_name)


class EventosForm(forms.Form):
	nombre = forms.CharField(max_length=255, label="Nombre", widget=forms.TextInput(attrs={'class': "form-control"}))
	fecha = forms.DateField(label="Fecha", initial=datetime.date.today(), widget=forms.SelectDateWidget(attrs={'class': "standardSelect"}))
	horas = forms.IntegerField(min_value=1, label="Horas", widget=forms.NumberInput(attrs={'class': "form-control"}))
	comentarios = forms.CharField(required=False, max_length=255, label="Comentarios", widget=forms.Textarea(attrs={'rows': 4, 'class': "form-control"}))
	
	def __init__(self, nPlanes, *args, **kwargs):
		super(EventosForm, self).__init__(*args, **kwargs)
		#choices = [['1', 'First',], ['2', 'Second',]]
		choices = [['-1', '------']]
		planes = Planes.objects.all()
		for p in planes:
			if p.mostrar == True:
				choices.append([p.idPlan, p.nombre])

		for i in range(1, nPlanes+1):
			self.fields['plan_%d' % i] = forms.ChoiceField(label="Plan %d" % i, choices=choices, widget=forms.Select(attrs={'class': "standardSelect"}))
			self.fields['cantidad_%d' % i] = forms.IntegerField(min_value=1, label="plan %d " % i, widget=forms.NumberInput(attrs={'class': "form-control", 'value': 1}))


class EventosSelectForm(forms.Form):
	ActivacionSelect = forms.ChoiceField(label="Activación", choices=[], widget=forms.Select(attrs={'class': "standardSelect"}))
	nombre = forms.CharField(max_length=255, label="Nombre", widget=forms.TextInput(attrs={'class': "form-control"}))
	fecha = forms.DateField(label="Fecha", initial=datetime.date.today(), widget=forms.SelectDateWidget(attrs={'class': "standardSelect"}))
	horas = forms.IntegerField(min_value=1, label="Horas", widget=forms.NumberInput(attrs={'class': "form-control"}))
	comentarios = forms.CharField(required=False, max_length=255, label="Comentarios", widget=forms.Textarea(attrs={'rows': 4, 'class': "form-control"}))
	
	def __init__(self, nPlanes, edit, *args, **kwargs):
		super(EventosSelectForm, self).__init__(*args, **kwargs)
		#choices = [['1', 'First',], ['2', 'Second',]]
		choices = [['-1', '------']]
		planes = Planes.objects.all()
		for p in planes:
			if p.mostrar == True:
				choices.append([p.idPlan, p.nombre])

		if edit:
			choices_activaciones = []
		else:
			choices_activaciones = [['-1', '------']]
		clientes = Clientes.objects.all()
		for c in clientes:
			for a in c.Activaciones.all():
				choices_activaciones.append([a.idActivacion, c.nombre + " - " + a.nombre])
		#activaciones = Activaciones.objects.all()
		#for a in activaciones:
		#	choices_activaciones.append([a.idActivacion, a.nombre])

		self.fields['ActivacionSelect'].choices = choices_activaciones
		for i in range(1, nPlanes+1):
			self.fields['plan_%d' % i] = forms.ChoiceField(label="Plan %d" % i, choices=choices, widget=forms.Select(attrs={'class': "standardSelect"}))
			self.fields['cantidad_%d' % i] = forms.IntegerField(min_value=1, label="plan %d " % i, widget=forms.NumberInput(attrs={'class': "form-control", 'value': 1}))


class PlanesForm(forms.Form):
	nombre = forms.CharField( max_length=255, label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
	
	def __init__(self, nItems, *args, **kwargs):
		super(PlanesForm, self).__init__(*args, **kwargs)
		choices = [['-1', '------']]
		items = Items.objects.all()
		for it in items:
			#if it.activo:
			choices.append([it.idItem, it.nombre])

		#self.fields['items'] = forms.MultipleChoiceField(label="Items", choices=choices, widget=forms.SelectMultiple(attrs={'class': "standardSelect", 'id': "items"}))
		for i in range(1, nItems+1):
			self.fields['item_%d' % i] = forms.ChoiceField(label="Item %d" % i, choices=choices, widget=forms.Select(attrs={'class': "standardSelect"}))
			self.fields['cantidad_%d' % i] = forms.IntegerField(min_value=1, label="item %d " % i, widget=forms.NumberInput(attrs={'class': "form-control", 'value': 1}))

class MostrarPlanForm(forms.Form):
	mostrar = forms.BooleanField(required=False, label="Elegible", widget=forms.CheckboxInput(attrs={'class': "switch-input"}))


class EstacionesForm(forms.Form):
	nombre = forms.CharField( max_length=255, label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
	
	def __init__(self, nItems, *args, **kwargs):
		super(EstacionesForm, self).__init__(*args, **kwargs)
		choices = [['-1', '------']]
		items = Items.objects.all()
		for it in items:
			choices.append([it.idItem, it.nombre])

		for i in range(1, nItems+1):
			self.fields['item_%d' % i] = forms.ChoiceField(label="Item %d" % i, choices=choices, widget=forms.Select(attrs={'class': "standardSelect"}))
			self.fields['cantidad_%d' % i] = forms.IntegerField(min_value=1, label="item %d " % i, widget=forms.NumberInput(attrs={'class': "form-control", 'value': 1}))


class ItemsForm(forms.ModelForm):
	class Meta:
		model = Items
		exclude = []
		widgets = {
			'nombre': forms.TextInput(attrs={'class': "form-control"}),
			'multiple': forms.CheckboxInput(attrs={'class': "switch-input"}),
		}


class TrabajadoresForm(forms.ModelForm):
	class Meta:
		model = Trabajadores
		exclude = []
		widgets = {
			'nombre': forms.TextInput(attrs={'class': "form-control"}),
			'rut': forms.TextInput(attrs={'class': "form-control"}),
			'telefono': forms.TextInput(attrs={'class': "form-control"}),
			'mail': forms.TextInput(attrs={'class': "form-control"}),
		}


class ContactosForm(forms.ModelForm):
	class Meta:
		model = Contactos
		exclude = ["Cliente"]
		widgets = {
		}
class ContactosFormSelect(forms.ModelForm):
	class Meta:
		model = Contactos
		exclude = []
		widgets = {
			'Cliente': forms.Select(attrs={'class': "form-control"}),
			'nombre': forms.TextInput(attrs={'class': "form-control"}),
			'telefono': forms.TextInput(attrs={'class': "form-control"}),
			'mail': forms.TextInput(attrs={'class': "form-control"}),
		}
	def __init__(self, *args, **kwargs):
		super(ContactosFormSelect, self).__init__(*args, **kwargs)
		#self.fields['user'].queryset = User.objects.all()
		self.fields['Cliente'].label_from_instance = lambda obj: obj.nombre # lambda obj: "%s %s" % (obj.last_name, obj.first_name)


class CoordinacionForm(forms.ModelForm):
	#choices = []
	#contactos = Contactos.objects.all()
	#for e in contactos:
	#	choices.append([e.idContacto, e.nombre])
	#contacto = forms.ChoiceField(label="Contacto", choices=choices)
	class Meta:
		model = Eventos
		fields = ["Contacto", "inicio_servicio", "fin_servicio", "fecha_instalacion", "hora_instalacion", "fecha_desinstalacion", "hora_desinstalacion", "direccion"]
		widgets = {
				"Contacto": forms.Select(attrs={'class': "standardSelect"}),
				"inicio_servicio": forms.TimeInput(attrs={'placeholder': "ej: 18:30", 'class': "form-control"}),
				"fin_servicio": forms.TimeInput(attrs={'placeholder': "ej: 18:30", 'class': "form-control"}),
				"hora_instalacion": forms.TimeInput(attrs={'placeholder': "ej: 18:30", 'class': "form-control"}),
				"hora_desinstalacion": forms.TimeInput(attrs={'placeholder': "ej: 18:30", 'class': "form-control"}),
				"fecha_instalacion": forms.SelectDateWidget(empty_label=("Año", "Mes", "Día"), attrs={'class': "standardSelect"}),
				"fecha_desinstalacion": forms.SelectDateWidget(empty_label=("Año", "Mes", "Día"), attrs={'class': "standardSelect"}),
				"direccion": forms.TextInput(attrs={'class': "form-control"}),
			}
	def __init__(self, evento, *args, **kwargs):
		super(CoordinacionForm, self).__init__(*args, **kwargs)
		#self.fields['user'].queryset = User.objects.all()
		#self.fields['Contacto'].label_from_instance = lambda obj: obj.nombre # lambda obj: "%s %s" % (obj.last_name, obj.first_name)
		contactos = evento.Activacion.Cliente.Contactos.all()
		choices = [["", '------']]
		for contacto in contactos:
			choices.append([contacto.idContacto, contacto.nombre])
		self.fields['Contacto'].choices = choices

class LogisticaTrabajadoresForm(forms.Form):
	#empty = []
	#Supervisor = forms.MultipleChoiceField(required=False, label="Supervisor(es)", choices=empty, widget=forms.SelectMultiple(attrs={'class': "standardSelect"}))
	#Montaje = forms.MultipleChoiceField(required=False, label="Montaje", choices=empty, widget=forms.SelectMultiple(attrs={'class': "standardSelect"}))
	#Desmontaje = forms.MultipleChoiceField(required=False, label="Desmontaje", choices=empty, widget=forms.SelectMultiple(attrs={'class': "standardSelect"}))
	#Operador = forms.MultipleChoiceField(required=False, label="Operador(es)", choices=empty, widget=forms.SelectMultiple(attrs={'class': "standardSelect"}))
	
	#Trabajadores = forms.ModelMultipleChoiceField(queryset=Trabajadores.objects.all())
	def __init__(self, *args, **kwargs):
		super(LogisticaTrabajadoresForm, self).__init__(*args, **kwargs)
		choices = []
		trabajadores = Trabajadores.objects.all()
		for t in trabajadores:
			choices.append([t.idTrabajador, t.nombre])

		cargos = Cargos.objects.all()
		for cargo in cargos:
			self.fields[cargo.nombre] = forms.MultipleChoiceField(required=False, label=cargo.nombre, choices=choices, widget=forms.SelectMultiple(attrs={'class': "standardSelect"}))
		#self.fields['Supervisor'].choices = choices
		#self.fields['Montaje'].choices = choices
		#self.fields['Desmontaje'].choices = choices
		#self.fields['Operador'].choices = choices
	

class LogisticaPlanesForm(forms.Form):
	#choices = []
	#estaciones = Estaciones.objects.all()
	#for p in planes:
	#	choices.append([p.idPlan, p.nombre])

	def __init__(self, planesEvento, *args, **kwargs):
		super(LogisticaPlanesForm, self).__init__(*args, **kwargs)

		estaciones = Estaciones.objects.all()
		for planEvento in planesEvento:
			for nPlan in range(1, planEvento.cantidad + 1):
				#activo problema :/
				# if planEvento.ItemsPlanEvento.filter(ItemsPlan=itemPlan).count() > 0:
				for itemPlan in planEvento.Plan.ItemsPlan.all():
					for nItem in range(1, itemPlan.cantidad + 1):
						choices = [['-1', '------']]
						for e in estaciones:
							if itemPlan.Item in e.Items.all():
								choices.append([e.ItemsEstacion.get(Item=itemPlan.Item).idItemsEstacion, e.nombre])
						#print(choices)
						self.fields['planEvento_%d_itemPlan_%d_nPlan_%d_nItem_%d' % (planEvento.idPlanesEvento, itemPlan.idItemsPlan, nPlan, nItem)] = forms.ChoiceField(required=False, label='planEvento_%d_itemPlan_%d' % (planEvento.idPlanesEvento, itemPlan.idItemsPlan), choices=choices, widget=forms.Select(attrs={'class': "standardSelect"}))


class EventoChecklistForm(forms.Form):
	def __init__(self, idItemPlanEvento, *args, **kwargs):
		super(EventoChecklistForm, self).__init__(*args, **kwargs)

		self.fields['item_%d' % idItemPlanEvento] = forms.BooleanField(required=False, label="Check", widget=forms.CheckboxInput(attrs={'class': "switch-input"}))


class CargosForm(forms.ModelForm):
	class Meta:
		model = Cargos
		exclude = []
		widgets = {
			'nombre': forms.TextInput(attrs={'class': "form-control"}),
			'n': forms.NumberInput(attrs={'class': "form-control"}),
		}


class RecurrentesForm(forms.ModelForm):
	class Meta:
		model = Recurrentes
		exclude = []
		widgets = {
			'nombre': forms.TextInput(attrs={'class': "form-control"}),
			'n': forms.NumberInput(attrs={'class': "form-control"}),
		}


class PendientesForm(forms.ModelForm):
	class Meta:
		model = Pendientes
		exclude = []
		widgets = {
			'nombre': forms.TextInput(attrs={'class': "form-control"}),
			'n': forms.NumberInput(attrs={'class': "form-control"}),
		}


class RecurrentesEventoForm(forms.Form):

	def __init__(self, *args, **kwargs):
		super(RecurrentesEventoForm, self).__init__(*args, **kwargs)

		recurrentes = Recurrentes.objects.all()
		for recurrente in recurrentes:
			self.fields[recurrente.nombre.replace(" ", "")] = forms.BooleanField(required=False, label=recurrente.nombre, widget=forms.CheckboxInput(attrs={'class': "switch-input"}))


class PendientesEventoForm(forms.Form):

	def __init__(self, *args, **kwargs):
		super(PendientesEventoForm, self).__init__(*args, **kwargs)

		pendientes = Pendientes.objects.all()
		for pendiente in pendientes:
			self.fields[pendiente.nombre.replace(" ", "")] = forms.BooleanField(required=False, label=pendiente.nombre, widget=forms.CheckboxInput(attrs={'class': "switch-input"}))

class ReportesForm(forms.Form):
	choices=[[5,""],[4,""],[3,""],[2,""],[1,""]]
	satisfaccion = forms.IntegerField(required = False, label="Satisfacción", widget=forms.RadioSelect(choices=choices, attrs={'class': "form-check-input"}))
	comentarios_satisfaccion = forms.CharField(required=False, max_length=255, label="Comentarios Satisfacción", widget=forms.Textarea(attrs={'rows': 4, 'class': "form-control"}))
	
	def __init__(self, nErrores, *args, **kwargs):
		super(ReportesForm, self).__init__(*args, **kwargs)

		for i in range(1, nErrores+1):
			self.fields['error_%d' % i] = forms.CharField(required=True, max_length=255, label="Error técnico %d" % i, widget=forms.Textarea(attrs={'rows': 2, 'class': "form-control"}))
