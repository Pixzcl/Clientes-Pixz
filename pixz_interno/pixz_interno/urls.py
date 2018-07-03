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


urlpatterns = [
	#url(r'^admin/', admin.site.urls),
	url(r'^$', views.index, name='index'),
	url(r'^agregar_cliente/', views.agregar_cliente, name='agregar_cliente'),
	url(r'^editar_cliente/', views.editar_cliente, name='editar_cliente'),
	url(r'^eliminar_cliente/', views.eliminar_cliente, name='eliminar_cliente'),

	url(r'^activaciones/', views.activaciones, name='activaciones'),
	url(r'^agregar_activacion/', views.agregar_activacion, name='agregar_activacion'),
	url(r'^editar_activacion/', views.editar_activacion, name='editar_activacion'),
	url(r'^eliminar_activacion/', views.eliminar_activacion, name='eliminar_activacion'),
	
	url(r'^eventos/', views.eventos, name='eventos'),
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
	
	


	# Sufee Admin
	url(r'^charts_chartjs/', views.charts_chartjs, name='charts_chartjs'),
	url(r'^charts_flot/', views.charts_flot, name='charts_flot'),
	url(r'^charts_peity/', views.charts_peity, name='charts_peity'),
	url(r'^dashboard/', views.dashboard, name='dashboard'),
	url(r'^font_fontawesome/', views.font_fontawesome, name='font_fontawesome'),
	url(r'^font_themify/', views.font_themify, name='font_themify'),
	url(r'^forms_advanced/', views.forms_advanced, name='forms_advanced'),
	url(r'^forms_basic/', views.forms_basic, name='forms_basic'),
	url(r'^maps_gmap/', views.maps_gmap, name='maps_gmap'),
	url(r'^maps_vector/', views.maps_vector, name='maps_vector'),
	url(r'^page_login/', views.page_login, name='page_login'),
	url(r'^page_register/', views.page_register, name='page_register'),
	url(r'^pages_forget/', views.pages_forget, name='pages_forget'),
	url(r'^tables_basic/', views.tables_basic, name='tables_basic'),
	url(r'^tables_data/', views.tables_data, name='tables_data'),
	url(r'^ui_alerts/', views.ui_alerts, name='ui_alerts'),
	url(r'^ui_badges/', views.ui_badges, name='ui_badges'),
	url(r'^ui_buttons/', views.ui_buttons, name='ui_buttons'),
	url(r'^ui_cards/', views.ui_cards, name='ui_cards'),
	url(r'^ui_grids/', views.ui_grids, name='ui_grids'),
	url(r'^ui_modals/', views.ui_modals, name='ui_modals'),
	url(r'^ui_progressbar/', views.ui_progressbar, name='ui_progressbar'),
	url(r'^ui_social_buttons/', views.ui_social_buttons, name='ui_social_buttons'),
	url(r'^ui_switches/', views.ui_switches, name='ui_switches'),
	url(r'^ui_tabs/', views.ui_tabs, name='ui_tabs'),
	url(r'^ui_typgraphy/', views.ui_typgraphy, name='ui_typgraphy'),
	url(r'^widgets/', views.widgets, name='widgets')
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
