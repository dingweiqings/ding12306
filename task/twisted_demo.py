from twisted.internet import reactor   # 事件循环（终止条件，所有的socket都已经移除）
from treq import get # socket对象（如果下载完成，自动从时间循环中移除...）
from twisted.internet import defer     # defer.Deferred 特殊的socket对象 （不会发请求，手动移除）
'''
1.利用getPage创建socket
2.将socket添加到事件循环中
3.开始事件循环（无法自动结束）
'''

def response(content):
    print(content)

@defer.inlineCallbacks
def task1():
    '''
    最简单的异步
    @return:
    '''
    url = "https://www.baidu.com"
    d = get(url.encode('utf-8'),proxy={'https':'https://59.62.53.248:9000'})
    d.addCallback(response)
    yield d

########################
'''
1.利用get创建socket
2.将socket添加到事件循环中
3.开始事件循环（自动结束）
'''
def response(content):
    print(content)

@defer.inlineCallbacks
def task2():
    '''
    多个请求的封装，会把两个yield 也做成异步任务
    @return:
    '''
    url = "http://www.baidu.com"
    d = get(url.encode('utf-8'))
    d.addCallback(response)
    yield d
    url = "http://www.baidu.com"
    d = get(url.encode('utf-8'))
    d.addCallback(response)
    yield d

@defer.inlineCallbacks
def task3():
    '''
    多个请求的封装
    @return:
    '''
    url = "http://www.baidu.com"
    d1 = get(url.encode('utf-8'))
    d1.addCallback(response)

    url = "http://www.baidu.com"
    d2 = get(url.encode('utf-8'))
    d2.addCallback(response)

    url = "http://www.baidu.com"
    d3 = get(url.encode('utf-8'))
    d3.addCallback(response)
    yield defer.Deferred()

def done():
    print("shoud done")
    reactor.stop()
if __name__ == '__main__':
    #获取request task
    d = task1()
    #封装list
    dd = defer.DeferredList([d])
    #add call back 和errback
    #对多个task ,做清理
    reactor.run()
