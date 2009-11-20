# This module provides internationalization support
#

# International support
language_codes = ['en_US','pt_PT']

def url_language():
	""" Returns the language part of the url http://server/lang/* """
	url_lang = cherrypy.request.path_info.split("/",2)[1]    
	if url_lang in language_codes:
		return "/"+url_lang
	return ""
	 
def set_request_language():
	cherrypy.request.lang = url_language()
	#print "LANG", cherrypy.request.lang
	

def translate_string(str):    
    """ This function is used with _("string") """
    if url_language() == "/pt_PT" and str == "Hello":
        return u"Olá"
    return str

# Set the lang set tool
cherrypy.tools.set_request_language = cherrypy.Tool('on_start_resource', set_request_language)
cherrypy.config.update({'tools.set_request_language.on': True})

cherrypy.root.pt_PT = cherrypy.root
