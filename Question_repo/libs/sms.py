import urllib.request
import urllib
import json


def send_sms(mobile, captcha):
    flag = True
    # 这个是短信API地址
    url = 'https://open.ucpaas.com/ol/sms/sendsms'

    # 准备一下头,声明body的格式
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    # 还有我们准备用Post传的值，这里值用字典的形式
    values = {
     "sid":"424ba67011f7dac65fb5b6a09241c6a1",
     "token":"ebe77f586cf5cef1e22baeff26311ea9",
     "appid":"32eec568bf184618a222bebbefb4bd5b",
     "templateid":"461339",
     "param":str(captcha),
     "mobile":mobile,
    }

    try:
        # 将字典格式化成bytes格式
        data = json.dumps(values).encode('utf-8')
        # 创建一个request,放入我们的地址、数据、头
        request = urllib.request.Request(url, data, headers)
        html = urllib.request.urlopen(request).read().decode('utf-8')
        # html = '{"code":"000000","count":"1","create_date":"2018-07-23 13:34:06","mobile":"15811564298","msg":"OK","smsid":"852579cbb829c08c917f162b267efce6","uid":""}'
        code = json.loads(html)["code"]
        print(f"code:{code}")
        if code == "000000":
            flag = True
        else:
            flag = False
    except Exception as ex:
        flag = False
    return flag

