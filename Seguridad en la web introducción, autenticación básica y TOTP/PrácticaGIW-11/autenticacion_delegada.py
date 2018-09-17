# -*- coding: utf-8 -*-

#
# Víctor Fernández Rubio
# David González Jiménez
# Carlos Llames Arribas
# Marta Pastor Puente

# Víctor Fernández Rubio, David González Jiménez, Carlos Llames Arribas y
# Marta Pastor Puente declaramos que esta solución
# es fruto exclusivamente de nuestro trabajo personal. No hemos sido
# ayudados por ninguna otra persona ni hemos obtenido la solución de
# fuentes externas, y tampoco hemos compartido nuestra solución con
# nadie. Declaramos además que no hemos realizado de manera deshonesta
# ninguna otra actividad que pueda mejorar nuestros resultados
# ni perjudicar los resultados de los demás.


from bottle import run, get, request, template, response
# Resto de importaciones
from time import gmtime, strftime
import time
import string
import random
import json
import urllib2
import urllib


# Credenciales. 
# https://developers.google.com/identity/protocols/OpenIDConnect#appsetup
# Copiar los valores adecuados.
CLIENT_ID     = "141391213305-v3iltnfi94cg030r1vd0pdoa93hbkr0i.apps.googleusercontent.com"
CLIENT_SECRET = "_RBiiAIk5YNHvKZTXbeY2uCe"
RESPONSE_TYPE = "code"
SCOPE = "openid%20email"
REDIRECT_URI  = "http://localhost:8080/token"


# Fichero de descubrimiento para obtener el 'authorization endpoint' y el 
# 'token endpoint'
# https://developers.google.com/identity/protocols/OpenIDConnect#authenticatingtheuser
DISCOVERY_DOC = "https://accounts.google.com/.well-known/openid-configuration"


# Token validation endpoint para decodificar JWT
# https://developers.google.com/identity/protocols/OpenIDConnect#validatinganidtoken
TOKENINFO_ENDPOINT = 'https://www.googleapis.com/oauth2/v3/tokeninfo'


Usuario = {
		client_id = CLIENT_ID
		client_secret = CLIENT_SECRET
		response_type = RESPONSE_TYPE
		scope = SCOPE
		redirect_uri = REDIRECT_URI
		discovery_doc = DISCOVERY_DOC
		#tokeninfo_endpoint = TOKENINFO_ENDPOINT
	}



def crearSemilla():
    alfabetoBase32 = string.ascii_uppercase + "234567"     
    semilla = ""
    for i in range(32):
        semilla = semilla + str(random.choice(alfabetoBase32))
            
    return semilla

@get('/login_google')
def login_google():
	
	global Usuario
    
    Usuario['semilla'] = crearSemilla()
	
	url = "https://accounts.google.com/o/oauth2/v2/auth?"
	url += "client_id=" + Usuario["client_id"]
	url += "&client_secret=" + Usuario["client_secret"]
	url += "&response_type=" + Usuario["response_type"]
	url += "&scope=" + Usuario["scope"]
    url += "&semilla=" + Usuario["semilla"]
	
	return template ("login.tpl", URL = url);

def tokenValido(datosToken, doc):
    global Usuario

    
    if doc['jwks_uri'] != "https://www.googleapis.com/oauth2/v3/certs":
        return False
        
    if tokenData['aud'] != Usuario['client_id']:
        return False 
    
    
    if not (datosToken['iss'] == 'https://accounts.google.com' or datosToken['iss'] == 'accounts.google.com'):
        return False 
    
    
#esto es asi? o se puede de otra forma?
    tokenExpira = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(tokenData['exp'])))
    
    actualHora = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    if actualHora > tokenExpira:
        return False

    return True

@get('/token')
def token():
    
    global Usuario
    
    
    semilla = request.forms.get('semilla', type = str)
    
    codigo = request.forms.get('codigo', type = str)
    
    
    if semilla == Usuario['semilla']:
        
        doc = json.load(urllib2.urlopen(Usuario['discovery_doc']))
        token_endpoint =  doc['token_endpoint']
        
        values = {
            'code' : codigo,
            'client_id' : Usuario['client_id'],
            'client_secret' : Usuario['client_secret'],
            'redirect_uri' : Usuario['redirect_uri'],
            'grant_type' : 'authorization_code',
        }

        aux = urllib.urlencode(values)
        req = urllib2.Request(token_endpoint, aux)
        response = urllib2.urlopen(req)
        tokenDictionary = json.load(response) 

        token_id = tokenDictionary['id_token']

        url = 'https://www.googleapis.com/oauth2/v3/tokeninfo?'
        url += 'id_token=' + token_id
        datosToken = json.load(urllib2.urlopen(url))
        
        if tokenValido(datosToken, doc):
            return template('Bienvenido_usuario', datosToken['email'])
        
        else:
            return "Movimiento naranjaaaaaaaaaa!"
    
    


if __name__ == "__main__":
    # NO MODIFICAR LOS PARÁMETROS DE run()
    run(host='localhost',port=8080,debug=True)
