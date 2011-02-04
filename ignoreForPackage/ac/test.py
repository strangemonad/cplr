class A(object):
	def f(self):
		print "f_A"
class B(A):
	def f(self):
		A.f(self)
