from multiprocessing import Process, Pool
class Test():
    def __init__(self, a):
        self.a = a

    def monterT(self):
        self.a+=1
        print(self.a)

def monter():
    global t
    t.monterT()


a=10
t = Test(a)
monter()
monter()
print(t.a)
print()
with Pool(processes=1) as pool:
    pool.apply(monter)
    pool.apply(monter)
    pool.apply(monter)
print(t.a)
