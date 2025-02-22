import inspect
from datetime import datetime

# taken from: http://code.activestate.com/recipes/496741-object-proxying/

class Proxy(object):
	__slots__ = ["_obj", "__weakref__"]

	def __init__(self, obj):
		object.__setattr__(self, "_obj", obj)
		object.__setattr__(self, "_message", "cocksucker")

	#
	# proxying (special cases)
	#
	def __getattribute__(self, name):
		caller = inspect.stack()[1][3]
		frm = inspect.stack()[1]
		caller_module = inspect.getmodule(frm[0]).__name__
		cls_name = type(self).__name__.split(':')[-1]
		access_type = "READ"
		paren = ""
		attrib = getattr(object.__getattribute__(self, "_obj"), name)
		if callable(attrib):
			paren = "()"
			access_type = "CALL"
		print(f"{datetime.now()} [{access_type}] [{caller_module}] << {caller} >> {cls_name}.{name}{paren}")
		# print("[{}] {} [{}] << {} >> {}.{}".format(datetime.now(), '[READ]', caller_module, caller, cls_name, name))
		return attrib

	def __delattr__(self, name):
		delattr(object.__getattribute__(self, "_obj"), name)

	def __setattr__(self, name, value):
		caller = inspect.stack()[1][3]
		frm = inspect.stack()[1]
		caller_module = inspect.getmodule(frm[0]).__name__
		cls_name = type(self).__name__.split(':')[-1]
		print(f"{datetime.now()} [WRITE] [{caller_module}] << {caller} >> {cls_name}.{name}")
		# print("{} {} [{}] << {} >> {}.{}".format(datetime.now(), '[WRITE]', caller_module, caller, cls_name, name))
		setattr(object.__getattribute__(self, "_obj"), name, value)

	def __nonzero__(self):
		return bool(object.__getattribute__(self, "_obj"))

	def __str__(self):
		return str(object.__getattribute__(self, "_obj"))

	def __repr__(self):
		return repr(object.__getattribute__(self, "_obj"))

	#
	# factories
	#
	_special_names = [
		'__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
		'__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
		'__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
		'__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
		'__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
		'__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
		'__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
		'__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
		'__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
		'__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
		'__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
		'__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
		'__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
		'__truediv__', '__xor__', 'next',
	]

	@classmethod
	def _create_class_proxy(cls, theclass):
		"""creates a proxy for the given class"""

		def make_method(name):
			def method(self, *args, **kw):
				return getattr(object.__getattribute__(self, "_obj"), name)(*args, **kw)

			return method

		namespace = {}
		for name in cls._special_names:
			if hasattr(theclass, name):
				namespace[name] = make_method(name)
		# return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)
		return type("sechat.Proxy:%s" % theclass.__name__, (cls,), namespace)

	def __new__(cls, obj, *args, **kwargs):
		"""
		creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are
		passed to this class' __init__, so deriving classes can define an
		__init__ method of their own.
		note: _class_proxy_cache is unique per deriving class (each deriving
		class must hold its own cache)
		"""
		try:
			cache = cls.__dict__["_class_proxy_cache"]
		except KeyError:
			cls._class_proxy_cache = cache = {}
		try:
			theclass = cache[obj.__class__]
		except KeyError:
			cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
		ins = object.__new__(theclass)
		theclass.__init__(ins, obj, *args, **kwargs)
		return ins
