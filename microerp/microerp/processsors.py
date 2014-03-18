
from django.conf import settings
def logo_empresa(request):
    logo_empresa = getattr(settings, 'IMG_SRC_LOGO_EMPRESA', None)
    mostra_menu_principal_lateral = getattr(settings, 'MOSTRAR_MENU_PRINCIPAL_LATERAL', True)
    rh_usa_banco_de_horas = getattr(settings, 'RH_USA_BANCO_DE_HORAS', True)
    return {
        'logo_empresa': logo_empresa,
        'mostra_menu_principal_lateral': mostra_menu_principal_lateral,
        'rh_usa_banco_de_horas': rh_usa_banco_de_horas,
        }
