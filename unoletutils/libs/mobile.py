"""
Módulo para identificar si el dispositivo desde el cual está conectado
el cliente es un dispositivo movil.
"""



# list of mobile User Agents
mobile_uas = [
	'w3c ','acs-','alav','alca','amoi','audi','avan','benq','bird','blac',
	'blaz','brew','cell','cldc','cmd-','dang','doco','eric','hipt','inno',
	'ipaq','java','jigs','kddi','keji','leno','lg-c','lg-d','lg-g','lge-',
	'maui','maxo','midp','mits','mmef','mobi','mot-','moto','mwbp','nec-',
	'newt','noki','oper','palm','pana','pant','phil','play','port','prox',
	'qwap','sage','sams','sany','sch-','sec-','send','seri','sgh-','shar',
	'sie-','siem','smal','smar','sony','sph-','symb','t-mo','teli','tim-',
	'tosh','tsm-','upg1','upsi','vk-v','voda','wap-','wapa','wapi','wapp',
	'wapr','webc','winw','winw','xda','xda-',
	]

mobile_ua_hints = [ 'SymbianOS', 'Opera Mini', 'iPhone', "Android", "Mobile"]



def isMobile(request):
    """
    Detecta si se está conectado en un dispositivo movil.
    """
    return False # IMPORTANTE QUITAR ESTO SOLO PRUEBAS.
    mobile_browser = False
    ua = request.META['HTTP_USER_AGENT'].lower()[0:4]

    if (ua in mobile_uas):
        mobile_browser = True
    else:
        for hint in mobile_ua_hints:
            if request.META['HTTP_USER_AGENT'].lower().find(hint.lower()) > 0:
                mobile_browser = True

    return mobile_browser


def getTemplate(request, template_name):
    """
    Pasa a la plantilla para celulares en caso de estar 
    conectado desde un celular:
    Ejemplo:

    Desktop: 'aplication/index.html'
    Mobile:  'aplication/mob/index.html'
    """
    if isMobile(request):
        t = template_name.split("/")
        template_name = "/".join(t[0:-1]) + "/mob/" + t[-1]
    return template_name