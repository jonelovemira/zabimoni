# import Exception

class MonitorException(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class ZabbixAPILoginError(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class ZabbixAPICreateHostError(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class ZabbixAPICreateItemError(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class ItemConstructError(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class ZabbixHostNotExistError(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class AreaNotExist(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class ServiceNotExist(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class HostCannotCreate(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class ItemCannotCreate(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class HostNotExist(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class GroupNullError(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class ZabbixAPIUpdateHostError(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class IpAddressNotExist(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)

class ZabbixAPIUpdateItemError(Exception):
	def __init__(self,code):
		self.code = code
	def __str__(self):
		return repr(self.code)