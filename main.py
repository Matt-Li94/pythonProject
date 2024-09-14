#汉诺塔递归问题,a上有n个圆盘，目标是把a的圆盘全部移动到c柱子上
num=0
def move(n,a,b,c):#三根柱子，中间的为工具柱子
    global num#统计运行次数
    num=num+1
    if n==1:
        print(a,'-->',c)
        return


    #把起始柱子上面的n-1个柱子移动到工具柱子上
    move(n-1,a,c,b)
    #再把起始柱子上剩下的最大的圆盘移动到目标柱子上
    print(a,'-->',c)
    move(n-1,b,a,c)#调换参数


move(5,'A','B','C')
print(num)
