#coding=utf-8
import urllib
import urllib2

import json,random,time,datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

lbs_key = "8325164e247e15eea68b59e89200988b"

qua_url = "http://touch.qunar.com/api/hotel/hotellist"
lbs_url1 = "http://restapi.amap.com/v3/place/text"
lbs_url2 = "http://restapi.amap.com/v3/geocode/geo"

proxy_file = "fastip.txt"

global curProxy

def getVerifiedProxies():
    proxyList = []
    inFile = open(proxy_file)
    while True:
        ll = inFile.readline().strip()
        if len(ll) == 0: break
        line = ll.strip().split('|')
        protocol = line[5]
        ip = line[1]
        port = line[2]
        proxy = {protocol: ':'.join([ip,port])}
        proxyList += proxy,
    return proxyList

proxyList = getVerifiedProxies()


def getRandomProxy(proxyList):
    return random.choice(proxyList)


# 使用代理发起模拟post请求
def post(post_path, post_dict):
    global curProxy
    proxy_support = urllib2.ProxyHandler(curProxy)

    requestHeader = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}

    post_data = urllib.urlencode(post_dict)

    opener = urllib2.build_opener( proxy_support)
    urllib2.install_opener(opener)
    req = urllib2.Request(post_path, data=post_data, headers=requestHeader)
    try:
        conn = urllib2.urlopen(req, timeout=10)
        html = conn.read()
    except:
        print "proxy unavailable"
        curProxy = getRandomProxy(proxyList)
        print 'set a new proxy:', curProxy
        return post(post_path, post_dict)
    try:
        # 对返回的html数据进行json解析
        res = json.loads(html)
    except:
        print "json error"
        curProxy = getRandomProxy(proxyList)
        print 'set a new proxy:', curProxy
        return post(post_path, post_dict)
    return res

# 获取去哪儿酒店数据
def QuaPost(cityname,perpage, page):
    qua_data = {
        "sort":0,
        "checkInDate":str(datetime.date.today()),
        "checkOutDate":str(datetime.date.today() + datetime.timedelta(days=1)),
        "couponsSelected":-1,
        "type":0,
        "city":cityname,
        "pageNum":perpage,
        "page":page,
    }
    qua_res = post(qua_url, qua_data)
    if not qua_res:
        return None
    return qua_res["data"]["hotels"]

# 获取address对应高德经纬度
def LBSPost(address):
    lbs_data = {
        "key": lbs_key,
        "address": address
    }
    lbs_res = post(lbs_url2, lbs_data)
    if not lbs_res:
        return None
    loc = "UnknownLBS"
    try:
        loc = lbs_res["geocodes"][0]["location"]
    except:
        print "lbs failed: ", lbs_res
    return loc


# 主函数
# cityname： 城市
# output: 数据输出文件名
def dataCollect(cityname, output,perpage=15, start_page=1):
    outFile = open(output, 'w')
    outFile.write('name|addr|price|qua_gpoint|comment_cnt|comment_score|lbs_gpoint\n')
    totalCnt = 0
    page = start_page
    flag = True
    print "page", page, ":", flag
    while flag:
        time_start = time.time()
        hotels = QuaPost(cityname, perpage, page)
        print "page", page, ":", len(hotels), "hotels"
        if hotels:
            for hotel in hotels:
                if hotel.has_key("attrs"):
                    name = hotel["attrs"]["hotelName"] if hotel["attrs"].has_key("hotelName") else "Undefined"
                    addr = hotel["attrs"]["hotelAddress"] if hotel["attrs"].has_key("hotelAddress") else "Undefined"
                    price = hotel["price"] if hotel.has_key("price") else "Undefined"
                    qua_gpoint = hotel["attrs"]["gpoint"] if hotel["attrs"].has_key("gpoint") else "Undefined"
                    comment_cnt = hotel["attrs"]["CommentCount"] if hotel["attrs"].has_key("CommentCount") else "Undefined"
                    comment_score = hotel["attrs"]["CommentScore"] if hotel["attrs"].has_key("CommentScore") else "Undefined"
                    lbs_gpoint = LBSPost(addr) if addr is not "Undefined" else "UnknownAddress"
                    outFile.write('%s|%s|%s|%s|%s|%s|%s\n'
                                  % (name,addr,price,qua_gpoint,comment_cnt,comment_score,lbs_gpoint))
                    totalCnt += 1
        else:
            print "cannot get hotels"
            break
        time_end = time.time()
        print "page", page, ":", time_end-time_start, "s"
        page += 1
        flag = len(hotels) > 0
        # print "page", page, ":", flag
    outFile.close()

    return totalCnt
#
# QuaPost("上海",1000)
# LBSPost("杭州上城区中山中路299号")
if __name__ == "__main__":
    time_start = time.time()
    if len(sys.argv) == 5:
        print "Ready to collect data: ",time.strftime("%Y-%m-%d %H:%M %p", time.localtime())
        #print sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
        global curProxy
        curProxy = getRandomProxy(proxyList)
        dataCnt = dataCollect(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
        time_end = time.time()
        print "End: ",time.strftime("%Y-%m-%d %H:%M %p", time.localtime())
        print "======Data Collected====== "
        print "time cost:", time_end-time_start, "s"
        print "data count:", dataCnt
    else:
        print "Invalid Argvs"

