# PlayDeb specifc startup file

# Common utility pages
from common.controllers import register, auth, install, logout, login, \
	release_select

# Main pages
from common.controllers import \
	updates, about, contact, sponsors
	
# Admin only
from common.controllers import packages, app

# Error handling
from common.controllers import error_404

# We need a custom welcome controller for the sponsor ads integration
from applications.playdeb.controllers import welcome

