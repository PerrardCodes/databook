import classe as c
d = "bonjour"

for i in range(5):
    v0 = c.Classe(d)#,m={})#,m={})
    Vol = v0.get()#Vol,instant,t
    #v0.m={}
    print(v0.m.keys())
    v0.m['volume'] = Vol
    del v0
