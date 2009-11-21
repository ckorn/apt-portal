# GetDeb specific startup file
print "Loading GetDeb Application controllers"

import base.controllers.register 
import base.controllers.auth

# Application custom controllers
import controllers.welcome
