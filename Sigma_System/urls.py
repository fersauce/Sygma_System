from django.conf.urls import patterns
from django.conf.urls import url


urlpatterns = patterns('',
                       url(r'^login/$', 'Sigma_System.views.iniciarsesion',
                           name='login'),
                       url(r'^inicio/$', 'Sigma_System.views.inicio',
                           name='inicio'),
                       url(r'^finalizar/$', 'Sigma_System.views.cerrarsesion',
                           name='finalizar'),
                       url(r'^adm_u/$', 'Sigma_System.views.adm_usuario',
                           name='adm_u'),
                       url(r'^adm_u_altas/$', 'Sigma_System.views.alta_usuario',
                           name='adm_u_altas'),
                       url(r'^nuevopass/$', 'Sigma_System.views.recuperarPass',
                           name='recu_pass'),
                       url(r'^proyecto/$',
                           'Sigma_System.views.administrar_proyecto',
                           name='adm_proy'),
                       url(r'^proyecto/nuevo/$',
                           'Sigma_System.views.alta_proyecto',
                           name='adm_proy_alta'),
                       url(r'^proyecto/modificar/(?P<idProyecto>\d+)$',
                           'Sigma_System.views.modificar_proyecto',
                           name='adm_proy_mod'),
                       url(r'^proyecto/eliminar/(?P<idProyecto>\d+)$',
                           'Sigma_System.views.baja_proyecto',
                           name='adm_proy_baja'),
)