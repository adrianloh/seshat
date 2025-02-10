import asyncio
import aiohttp
from seshat import seshat

seshat.save_log("seshat.log")

@seshat.record
def call_with_args(a, b, c):
	pass

@seshat.record
def call_with_kwargs(a, b, c, d=None, e=None):
	pass

@seshat.record
def call_with_return_one(o):
	return o

@seshat.record
def call_with_return_many(o1, o2):
	return o1, o2

@seshat.record
def call_generator(length):
	for i in range(length):
		yield i

@seshat.record
async def http_get(url):
	async with aiohttp.ClientSession() as session:
		res = await session.get(url)
		if res.status == 200:
			return await res.json()
		else:
			return None

# TESTS

def test_call_with_args(T):
	call_with_args(1, 2, 3)

class A: pass
def b(): pass

def test_call_with_kwargs(T):
	call_with_kwargs(1, 2, 3, d=A(), e=b)

def test_call_with_return(T):
	o = dict(a=1, b=2, c=3)
	a = call_with_return_one(o)
	if a != o:
		T.fail()

def test_call_with_return_many(T):
	o1 = dict(a=1, b=2, c=3)
	o2 = dict(d=4, e=5, f=6)
	a, b = call_with_return_many(o1, o2)
	if a != o1 or b != o2:
		T.fail()

def test_call_generator(T):
	collect = []
	length = 10
	for i in call_generator(length):
		collect.append(i)
	if len(collect) != length:
		T.fail()

def test_call_async(T):
	loop = asyncio.get_event_loop()
	loop.run_until_complete(http_get("https://httpbin.org/get"))
	loop.close()

def test_log(T):
	def log_message():
		seshat.info("Hello world")
		seshat.warn("This is not going to end well...")
		seshat.error("Told you so")
	log_message()


class D:
	def __init__(self):
		self.name = "Monica Bellucci"
		self.age = 60 # whoa

	def info(self):
		return f"{self.name} is {self.age} years old but I'd still tap that!"


def test_proxy(T):

	def c(d):
		# Class method call
		return d.info()

	def b(d):
		# Accessing attribute
		x = d.name
		c(d)

	def a(d):
		# Assigment to attribute
		d.age = 48
		b(d)

	d = D()
	d = seshat.proxy(d) # replace with proxy
	print(type(d)) #=>  <class 'seshat.proxy.sechat.Proxy:D'>

	a(d) # use the proxy as you would the original `d`

