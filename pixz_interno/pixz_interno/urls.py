"""EducaMas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from Eventos import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
	url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '../login/'}, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^no_autorizado/', views.no_autorizado, name='no_autorizado'),
    url(r'^editar_password/', views.editar_password, name='editar_password'),

	url(r'^$', views.index, name='index'),
	url(r'^clientes/', views.clientes, name='clientes'),
	url(r'^agregar_cliente/', views.agregar_cliente, name='agregar_cliente'),
	url(r'^editar_cliente/', views.editar_cliente, name='editar_cliente'),
	url(r'^eliminar_cliente/', views.eliminar_cliente, name='eliminar_cliente'),

	url(r'^activaciones/', views.activaciones, name='activaciones'),
	url(r'^agregar_activacion/', views.agregar_activacion, name='agregar_activacion'),
	url(r'^editar_activacion/', views.editar_activacion, name='editar_activacion'),
	url(r'^eliminar_activacion/', views.eliminar_activacion, name='eliminar_activacion'),
	
	url(r'^eventos/', views.eventos.as_view(), name='eventos'),
	url(r'^evento/', views.evento, name='evento'),
	url(r'^agregar_evento/', views.agregar_evento, name='agregar_evento'),
	url(r'^editar_evento/', views.editar_evento, name='editar_evento'),
	url(r'^eliminar_evento/', views.eliminar_evento, name='eliminar_evento'),
	
	url(r'^planes/', views.planes, name='planes'),
	url(r'^agregar_plan/', views.agregar_plan, name='agregar_plan'),
	url(r'^editar_plan/', views.editar_plan, name='editar_plan'),
	url(r'^eliminar_plan/', views.eliminar_plan, name='eliminar_plan'),
	
	url(r'^estaciones/', views.estaciones, name='estaciones'),
	url(r'^agregar_estacion/', views.agregar_estacion, name='agregar_estacion'),
	url(r'^editar_estacion/', views.editar_estacion, name='editar_estacion'),
	url(r'^eliminar_estacion/', views.eliminar_estacion, name='eliminar_estacion'),
	
	url(r'^items/', views.items, name='items'),
	url(r'^agregar_item/', views.agregar_item, name='agregar_item'),
	url(r'^editar_item/', views.editar_item, name='editar_item'),
	url(r'^eliminar_item/', views.eliminar_item, name='eliminar_item'),

	url(r'^trabajadores/', views.trabajadores, name='trabajadores'),
	url(r'^agregar_trabajador/', views.agregar_trabajador, name='agregar_trabajador'),
	url(r'^editar_trabajador/', views.editar_trabajador, name='editar_trabajador'),
	url(r'^eliminar_trabajador/', views.eliminar_trabajador, name='eliminar_trabajador'),

	url(r'^cargos/', views.cargos, name='cargos'),
	url(r'^agregar_cargo/', views.agregar_cargo, name='agregar_cargo'),
	url(r'^editar_cargo/', views.editar_cargo, name='editar_cargo'),
	url(r'^eliminar_cargo/', views.eliminar_cargo, name='eliminar_cargo'),
	
	url(r'^contactos/', views.contactos, name='contactos'),
	url(r'^agregar_contacto/', views.agregar_contacto, name='agregar_contacto'),
	url(r'^agregar_contacto_select/', views.agregar_contacto_select, name='agregar_contacto_select'),
	url(r'^editar_contacto/', views.editar_contacto, name='editar_contacto'),
	url(r'^eliminar_contacto/', views.eliminar_contacto, name='eliminar_contacto'),

	url(r'^recurrentes/', views.recurrentes, name='recurrentes'),
	url(r'^agregar_recurrente/', views.agregar_recurrente, name='agregar_recurrente'),
	url(r'^editar_recurrente/', views.editar_recurrente, name='editar_recurrente'),
	url(r'^eliminar_recurrente/', views.eliminar_recurrente, name='eliminar_recurrente'),

	url(r'^pendientes/', views.pendientes, name='pendientes'),
	url(r'^agregar_pendiente/', views.agregar_pendiente, name='agregar_pendiente'),
	url(r'^editar_pendiente/', views.editar_pendiente, name='editar_pendiente'),
	url(r'^eliminar_pendiente/', views.eliminar_pendiente, name='eliminar_pendiente'),

	url(r'^facturas/', views.facturas.as_view(), name='facturas'),
	url(r'^agregar_factura/', views.agregar_factura, name='agregar_factura'),
	#url(r'^editar_factura/', views.editar_factura, name='editar_factura'),
	url(r'^eliminar_factura/', views.eliminar_factura, name='eliminar_factura'),

	url(r'^ingresos/', views.ingresos, name='ingresos'),
	url(r'^agregar_ingreso/', views.agregar_ingreso, name='agregar_ingreso'),
	#url(r'^editar_ingreso/', views.editar_ingreso, name='editar_ingreso'),
	url(r'^eliminar_ingreso/', views.eliminar_ingreso, name='eliminar_ingreso'),

	url(r'^itinerario_crear/', views.itinerario_crear, name='itinerario_crear'),
	url(r'^itinerario/', views.itinerario, name='itinerario'),

	url(r'^calendario/', views.calendario, name='calendario'),

	url(r'^costos_variables/', views.costos_variables.as_view(), name='costos_variables'),
	url(r'^agregar_costo_variable/', views.agregar_costo_variable, name='agregar_costo_variable'),
	url(r'^editar_costo_variable/', views.editar_costo_variable, name='editar_costo_variable'),
	url(r'^eliminar_costo_variable/', views.eliminar_costo_variable, name='eliminar_costo_variable'),

	url(r'^tipos_costo_variable/', views.tipos_costo_variable, name='tipos_costo_variable'),
	url(r'^agregar_tipo_costo_variable/', views.agregar_tipo_costo_variable, name='agregar_tipo_costo_variable'),
	url(r'^editar_tipo_costo_variable/', views.editar_tipo_costo_variable, name='editar_tipo_costo_variable'),
	url(r'^eliminar_tipo_costo_variable/', views.eliminar_tipo_costo_variable, name='eliminar_tipo_costo_variable'),

]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
