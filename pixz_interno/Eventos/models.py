from django.db import models

# Create your models here.

# def upload_image(obj, fname):
# 	ext = fname.split(".")[-1]
# 	image_name = "Blog_image_{}".format(obj.id_int)
# 	image_name = image_name + "." + ext
# 	return u"/".join(["blog_images", image_name])



#user = models.OneToOneField(auth.models.User, related_name="user")
#Foto = models.FileField(upload_to=upload_image)
#uploaded_at = models.DateTimeField(auto_now_add=True)


##### IMPORTANTE #####
	## Todos los campos deben tener verbose_name (para generar las vistas de forma correcta)

class Clientes(models.Model):
	idCliente = models.AutoField(primary_key=True, verbose_name="#")
	nombre = models.CharField(unique=True, max_length=255, verbose_name="Cliente", blank=False, null=False)
	direccion = models.CharField(max_length=255, verbose_name="Dirección", blank=True, null=True, default="")
	

class Activaciones(models.Model):
	idActivacion = models.AutoField(primary_key=True, verbose_name="#")
	Cliente = models.ForeignKey("Clientes", verbose_name="Cliente", related_name="Activaciones", on_delete=models.CASCADE, blank=False, null=False) #to_field="idCliente"

	nombre = models.CharField(max_length=255, verbose_name="Activación", blank=False, null=False)
	monto = models.PositiveIntegerField(verbose_name="Monto de venta", blank=False, null=False)
	#tipo = models.CharField(max_length=255, verbose_name="Tipo", blank=False, null=False)
	descripcion = models.TextField(verbose_name="Descripción", blank=True, null=True, default="")


class Eventos(models.Model):
	idEvento = models.AutoField(primary_key=True, verbose_name="#")
	Activacion = models.ForeignKey("Activaciones", verbose_name="Activación", related_name="Eventos", on_delete=models.CASCADE, blank=False, null=False)
	Contacto = models.ForeignKey("Contactos", verbose_name="Contacto", related_name="Eventos", on_delete=models.SET(None), blank=True, null=True)
	Planes = models.ManyToManyField("Planes", through="PlanesEvento", related_name="Eventos")
	Trabajadores = models.ManyToManyField("Trabajadores", through="TrabajadoresEvento", related_name="Eventos")
	
	nombre = models.CharField(max_length=255, verbose_name="Evento", blank=False, null=False)
	#horas = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="Horas", blank=False, null=False)
	horas = models.PositiveSmallIntegerField(verbose_name="Horas", blank=False, null=False)
	fecha = models.DateField(verbose_name="Fecha", blank=False, null=False)
	comentarios = models.TextField(verbose_name="Comentarios", blank=True, null=True, default="")
	
	# Logística
	#fecha_y_hora_instalacion = models.DateTimeField(verbose_name="Fecha y hora de instalacion", blank=True, null=True)
	#fecha_y_hora_desinstalacion = models.DateTimeField(verbose_name="Fecha y hora de desinstalacion", blank=True, null=True)
	fecha_instalacion = models.DateField(verbose_name="Fecha de instalacion", blank=True, null=True)
	fecha_desinstalacion = models.DateField(verbose_name="Fecha de desinstalacion", blank=True, null=True)
	hora_instalacion = models.TimeField(verbose_name="Hora de instalacion", blank=True, null=True)
	hora_desinstalacion = models.TimeField(verbose_name="Hora de desinstalacion", blank=True, null=True)
	inicio_servicio = models.TimeField(verbose_name="Inicio del servicio", blank=True, null=True)
	fin_servicio = models.TimeField(verbose_name="Fin del servicio", blank=True, null=True)
	direccion = models.CharField(max_length=255, verbose_name="Dirección", blank=True, null=True)


class Contactos(models.Model):
	idContacto = models.AutoField(primary_key=True, verbose_name="#")
	Cliente = models.ForeignKey("Clientes", verbose_name="Cliente", related_name="Contactos", on_delete=models.SET(None), blank=False, null=True)
	
	nombre = models.CharField(unique=True, max_length=255, verbose_name="Nombre", blank=False, null=False)
	#rut = models.CharField(max_length=255, verbose_name="RUT", blank=True, null=True, default="")
	telefono = models.CharField(max_length=255, verbose_name="Teléfono", blank=True, null=True, default="")
	mail = models.EmailField(max_length=255, verbose_name="Mail", blank=True, null=True, default="")


class Trabajadores(models.Model):
	idTrabajador = models.AutoField(primary_key=True, verbose_name="#")

	nombre = models.CharField(unique=True, max_length=255, verbose_name="Nombre", blank=False, null=False, error_messages={"unique":"Ya existe un trabajador con este nombre"})
	rut = models.CharField(unique=True, max_length=255, verbose_name="RUT", blank=True, null=True, default="")
	telefono = models.CharField(unique=True, max_length=255, verbose_name="Teléfono", blank=True, null=True, default="")
	mail = models.EmailField(unique=True, max_length=255, verbose_name="Mail", blank=True, null=True, default="")


class TrabajadoresEvento(models.Model):
	idTrabajadorEvento = models.AutoField(primary_key=True, verbose_name="#")
	Trabajador = models.ForeignKey("Trabajadores", verbose_name="Trabajador", related_name="TrabajadoresEvento", on_delete=models.CASCADE, blank=False, null=False)
	Evento = models.ForeignKey("Eventos", verbose_name="Evento", related_name="TrabajadoresEvento", on_delete=models.CASCADE, blank=False, null=False)
	
	tipo = models.CharField(max_length=255, verbose_name="Tipo", blank=False, null=False)


class PlanesTrabajador(models.Model):
	idPlanesTrabajador = models.AutoField(primary_key=True, verbose_name="#")
	Trabajador = models.ForeignKey("Trabajadores", verbose_name="Trabajador", related_name="PlanesTrabajador", on_delete=models.CASCADE, blank=False, null=False)
	Plan = models.ForeignKey("Planes", verbose_name="Plan", related_name="PlanesTrabajador", on_delete=models.CASCADE, blank=False, null=False)


class PlanesEvento(models.Model):
	idPlanesEvento = models.AutoField(primary_key=True, verbose_name="#")
	Evento = models.ForeignKey("Eventos", verbose_name="Evento", related_name="PlanesEvento", on_delete=models.CASCADE, blank=False, null=False)
	Plan = models.ForeignKey("Planes", verbose_name="Plan", related_name="PlanesEvento", on_delete=models.PROTECT, blank=False, null=False)
	ItemsPlan = models.ManyToManyField("ItemsPlan", through="ItemsPlanEvento", related_name="PlanesEvento")
	ItemsEstacion = models.ManyToManyField("ItemsEstacion", through="ItemsPlanEvento", related_name="PlanesEvento")


class ItemsPlanEvento(models.Model):
	idItemsPlanEvento = models.AutoField(primary_key=True, verbose_name="#")
	PlanesEvento = models.ForeignKey("PlanesEvento", verbose_name="Plan evento", related_name="ItemsPlanEvento", on_delete=models.CASCADE, blank=False, null=False)
	ItemsPlan = models.ForeignKey("ItemsPlan", verbose_name="Item plan", related_name="ItemsPlanEvento", on_delete=models.SET(None), blank=False, null=True)
	ItemsEstacion = models.ForeignKey("ItemsEstacion", verbose_name="Item estación", related_name="ItemsPlanEvento", on_delete=models.SET(None), blank=True, null=True)
	check = models.BooleanField(verbose_name="Check", default=False)


class Planes(models.Model):
	idPlan = models.AutoField(primary_key=True, verbose_name="#")
	mostrar = models.BooleanField(verbose_name="Mostrar en listado", default=True)
	Items = models.ManyToManyField("Items", through="ItemsPlan", related_name="Planes")
	Trabajadores = models.ManyToManyField("Trabajadores", through="PlanesTrabajador", related_name="Planes")

	nombre = models.CharField(unique=True, max_length=255, verbose_name="Plan", blank=False, null=False)


class ItemsPlan(models.Model):
	idItemsPlan = models.AutoField(primary_key=True, verbose_name="#")
	Plan = models.ForeignKey("Planes", verbose_name="Plan", related_name="ItemsPlan", on_delete=models.CASCADE, blank=False, null=False)
	Item = models.ForeignKey("Items", verbose_name="Item", related_name="ItemsPlan", on_delete=models.CASCADE, blank=False, null=False)
	#item = models.CharField(max_length=255, verbose_name="Item", blank=False, null=False)
	ItemsEstacion = models.ManyToManyField("ItemsEstacion", through="ItemsPlanEvento", related_name="ItemsPlan")


class Estaciones(models.Model):
	idEstacion = models.AutoField(primary_key=True, verbose_name="#")
	nombre = models.CharField(unique=True, max_length=255, verbose_name="Estación", blank=False, null=False)
	Items = models.ManyToManyField("Items", through="ItemsEstacion", related_name="Estaciones")


class ItemsEstacion(models.Model):
	idItemsEstacion = models.AutoField(primary_key=True, verbose_name="#")
	Estacion = models.ForeignKey("Estaciones", verbose_name="Estación", related_name="ItemsEstacion", on_delete=models.CASCADE, blank=False, null=False)
	Item = models.ForeignKey("Items", verbose_name="Item", related_name="ItemsEstacion", on_delete=models.CASCADE, blank=False, null=False)
	#item = models.CharField(max_length=255, verbose_name="Item", blank=False, null=False)


class Items(models.Model):
	idItem = models.AutoField(primary_key=True, verbose_name="#")
	
	nombre = models.CharField(unique=True, max_length=255, verbose_name="Item", blank=False, null=False)