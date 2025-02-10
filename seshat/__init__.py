import sys
import inspect
from datetime import datetime
import pprint
from functools import wraps, partial
from threading import Lock
from . import proxy


class Seshat:

	def __init__(self):
		self._lock_ = Lock()
		pp = pprint.PrettyPrinter(stream=self)
		self._print_ = pp.pprint
		self.record = partial(self._record_, self)  # decorator
		self.write = partial(self._write_, self)  # called by pp
		self._writeline_ = partial(self._write_, self, indent=0)
		self._logfile_ = None
		self._proxies_ = {}

	def save_log(self, logfilepath):
		self._logfile_ = open(logfilepath, 'a')

	def proxy(self, obj):
		objId = id(obj)
		if objId not in self._proxies_:
			proxied = proxy.Proxy(obj)
			self._proxies_[objId] = proxied
			return proxied
		else:
			return obj

	def _log_function_(self, module_name, func_caller, func_name):
		message = f"{datetime.now()} [FUNC] [{module_name}] [ {func_caller} >> {func_name}() ]\n"
		self._writeline_(message)

	def _log_(self, caller_module, caller, message, symbol):
		message = f"{datetime.now()} {symbol} [ {caller_module} ] << {caller} >> : {message}\n"
		self._lock_.acquire()
		self._writeline_(message)
		self._lock_.release()

	def info(self, message):
		caller = inspect.stack()[1][3]
		frm = inspect.stack()[1]
		caller_module = inspect.getmodule(frm[0]).__name__
		self._log_(caller_module, caller, message, '[INFO]')

	def warn(self, message):
		caller = inspect.stack()[1][3]
		frm = inspect.stack()[1]
		caller_module = inspect.getmodule(frm[0]).__name__
		self._log_(caller_module, caller, message, '[WARN]')

	def error(self, message):
		caller = inspect.stack()[1][3]
		frm = inspect.stack()[1]
		caller_module = inspect.getmodule(frm[0]).__name__
		self._log_(caller_module, caller, message, u'[ERROR]')

	@staticmethod
	def _write_(self, stream, indent=1):
		spacer = '\t' * indent
		sys.stdout.write(spacer + stream)
		if self._logfile_ is not None:
			self._logfile_.write(spacer + stream)

	@staticmethod
	def _record_(self, func):
		stack = inspect.stack()
		frm = stack[1]
		caller_module = inspect.getmodule(frm[0])
		func_name = func.__name__

		@wraps(func)
		def interceptor(*args, **kwargs):
			stack = inspect.stack()
			caller = stack[1].function
			self._lock_.acquire()
			self._log_function_(caller_module.__name__, caller, func_name)
			if args:
				self._writeline_("args:\n")
				self._print_(args)
			if kwargs:
				self._writeline_("kwargs:\n")
				self._print_(kwargs)
			_return_ = (func(*args, **kwargs))
			if _return_:
				self._writeline_("return:\n")
				self._print_(_return_)
			self._lock_.release()
			return _return_
		return interceptor

seshat = Seshat()