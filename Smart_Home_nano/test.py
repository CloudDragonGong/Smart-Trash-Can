class A:
    def a(self):
        print('okk')

    def b(self):
        bb(self)


aa = A()


def bb(class_A):
    class_A.a()

aa.b()
