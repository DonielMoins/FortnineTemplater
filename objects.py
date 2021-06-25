from typing import Optional


class Request():
	
	def __init__(self, **kwargs):
		if len(kwargs) != 0:
			self.__dict__.update(kwargs)
			self.reqtype.lower()
			if self.reqtype != "get" or "head" or "post" or "patch" or "put" or "delete" or "options":
				raise Exception("Malformed Request Type JSON") 
		else:
			self.uri = "https://example.com/api?requestParm1={0}&requestParm2={1}"
			self.reqtype = "get"
			self.headers = {
				"user-agent": "FortnineActions/0.0.1",
				"content-type":"text"
				}
			self.ReuseSession = True

class Profile():
	def __init__(self, ProfileName = "Default Name", Requests=[Request()], settings: Optional[dict] = {}):
		self.ProfileName = ProfileName
		self.Requests = Requests
		
		# at this point im just typing in english
		if len(settings) != 0: self.__dict__.update(settings) 

