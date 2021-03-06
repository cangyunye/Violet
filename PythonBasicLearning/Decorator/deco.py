"""
Python中的装饰器(decorator)
想理解Python的decorator首先要知道在Python中函数也是一个对象，所以你可以

将函数复制给变量
将函数当做参数
返回一个函数

把@log放到now()函数的定义处，相当于执行了语句：
now = log(now)

概括的讲，装饰器的作用就是为已经存在的函数或对象添加额外的功能。

"""
#初级装饰器
def log(func):
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper  #调用log，返回的wrapper，而非wrapper()

#给装饰器传文本
def logz(text):
    def decorator(func):
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator
#装饰器内参数判断
def logl(level):
    def decorator(func):
        def wrapper(*args, **kw):
            if level == 0:
                print('[INFO]:%s():' % (func.__name__))
            elif level == 1:
                print('[WARN]:%s():' % (func.__name__))
            elif level == 2:
                print('[DEBUG]:%s():' % (func.__name__))
            elif level == 3:
                print('[ERROR]:%s():' % (func.__name__))
            else:
                print('[FATAL]:%s():' % (func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator
#基于类实现的装饰器
class logging(object):
   def __init__(self, func):
       self.func = func    
   def __call__(self, *args, **kwargs):
       print ("[DEBUG]: enter function {func}()".format(func=self.func.__name__) )       
       return self.func(*args, **kwargs)

# @logging
def say(something):
   print ("say {}!".format(something))
say = logging(say)



class logging2(object):
   def __init__(self, level='INFO'):
       self.level = level
   def __call__(self, func):  # 接受函数
        def wrapper(*args, **kwargs):
            print ("[{level}]: enter function {func}()".format(level=self.level,func=func.__name__))
            func(*args, **kwargs)        
        return wrapper  # 返回函数

@logging2(level='INFO')
def say2(something):
   print ("say {}!".format(something))
# say=logging(level='INFO')(say)




@log
def now(para):
    print('Test: now() = log(now)(),para=%s' % (para))

@logz('execute')
def nowz():
    print('Test: nowz = logz(text)(nowz)()')

@logl(1)#入参为int
def nowl():
    print('Test: nowl = logz(level)(nowl)()')

now('Para in Func')
nowz()
nowl()
say("what?")
say2("Lucky!")

