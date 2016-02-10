from base.models.sponsor import Sponsor

from threading import Lock
from sqlalchemy import desc
import datetime


sponsor_ads_counter_lock = Lock()
sponsor_ads_counter = 0

def get_sponsor():
	"""
	Returns a sponsor using a round robin with weight algorithm
	The pay ammount of the sponsor is used as the weight
	Returns a tuple: (sponsor, total_ammount)
	"""
	global sponsor_ads_counter_lock, sponsor_ads_counter
	# Filter by no enddate or enddate in the future
	sponsors = Sponsor.query.order_by(desc(Sponsor.ammount)).all()
	# was unable to do it in the query. So manual filtering here.
	sponsors2 = []
	for sponsor in sponsors:
		# somehow the datetime comparison did not work. So parse the string as date (e.g. '28-02-2016')
		if (sponsor.enddate is None) or (datetime.datetime.now()<=datetime.datetime.strptime(sponsor.enddate, '%d-%m-%Y')):
			sponsors2.append(sponsor)
	sponsors = sponsors2
	if len(sponsors) == 0:
		return (None, 0)
		
	total_ammount = 0	
	# Determine the total ammount to see if we need to restart the cycle
	for sponsor in sponsors:
			total_ammount += sponsor.ammount
			
	# Restart the cycle if required
	with sponsor_ads_counter_lock:
		sponsor_ads_counter -= 1
		if sponsor_ads_counter <= 0:
			sponsor_ads_counter = total_ammount
		local_sponsor_ads_counter = sponsor_ads_counter
	
	# Search for the "current" sponsor
	total = total_ammount
	for sponsor in sponsors:
		total -= sponsor.ammount
		if local_sponsor_ads_counter > total:
			break
			
	return (sponsor, total_ammount)
