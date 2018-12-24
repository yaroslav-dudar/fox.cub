import json
import urllib.request

class ProxyFactory:

    URL = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt"

    @staticmethod
    def getIpPort():
        content = urllib.request.urlopen(ProxyFactory.URL).\
            read().decode('utf-8')
        return json.loads(content)["data"][0]["ipPort"]
