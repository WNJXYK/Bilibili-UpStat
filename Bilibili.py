import requests, json, os

class BDev:
    def __init__(self, debug=False, path=None):
        # Init
        self.debug = debug
        self.cookie = None
        if path is not None: os.chdir(path)

        # Read Cookie
        try:
            fp = open(os.path.abspath("Cookie.txt"), "r")
            self.cookie = fp.readline()
            if self.debug: print(self.cookie)
        except Exception as e:
            raise Exception("Bilibili-Dev - Cannot read cookie in cookie.txt. Error : %s" % str(e))

        # Login
        mid, msg = self.check_user()
        if mid is None:
            raise Exception("Bilibili-Dev - Invalid cookie. Message : %s" % msg)
        else:
            print(" * Bilibili-Dev : Welcome User %d." % mid)
        self.mid = mid

    def check_user(self):
        code, text = self.get("https://member.bilibili.com/x/web/elec/user", {})
        ret = json.loads(text)
        if self.debug: print(ret)

        if ret["code"] == 0:
            return ret["data"]["mid"], ""

        return None, ret["message"]

    def account(self):
        ret = {}

        code, text = self.get("https://api.bilibili.com/x/relation/stat", {"vmid": self.mid, "jsonp":"jsonp"})
        if code != 200: return None, "Http " + str(code)
        jsonp = json.loads(text)
        if jsonp["code"] != 0: return None, jsonp["message"]
        if self.debug: print(jsonp)
        ret["followers"] = jsonp["data"]["follower"]

        code, text = self.get("https://api.bilibili.com/x/space/upstat", {"mid": self.mid, "jsonp":"jsonp"})
        if code != 200: return None, "Http " + str(code)
        jsonp = json.loads(text)
        if jsonp["code"] != 0: return None, jsonp["message"]
        if self.debug: print(jsonp)
        ret["archives"] = jsonp["data"]["archive"]["view"]
        ret["articles"] = jsonp["data"]["article"]["view"]
        ret["likes"] = jsonp["data"]["likes"]

        code, text = self.get("https://api.bilibili.com/x/space/acc/info", {"mid": self.mid, "jsonp": "jsonp"})
        if code != 200: return None, "Http " + str(code)
        jsonp = json.loads(text)
        if jsonp["code"] != 0: return None, jsonp["message"]
        if self.debug: print(jsonp)
        ret["name"] = jsonp["data"]["name"]
        ret["level"] = int(jsonp["data"]["level"])

        code, text = self.get("https://api.vc.bilibili.com/session_svr/v1/session_svr/single_unread", {})
        if code != 200: return None, "Http " + str(code)
        jsonp = json.loads(text)
        if jsonp["code"] != 0: return None, jsonp["message"]
        if self.debug: print(jsonp)
        ret["unread"] = jsonp["data"]["follow_unread"]

        return ret, ""

    def upstat(self):
        ret = {}

        code, text = self.get("https://member.bilibili.com/x/web/index/stat", {})
        if code != 200: return None, "Http " + str(code)
        jsonp = json.loads(text)
        if jsonp["code"] != 0: return None, jsonp["message"]
        if self.debug: print(jsonp)

        ret["click"] = (jsonp["data"]["total_click"], jsonp["data"]["incr_click"])
        ret["reply"] = (jsonp["data"]["total_reply"], jsonp["data"]["incr_reply"])
        ret["coin"] = (jsonp["data"]["total_coin"], jsonp["data"]["inc_coin"])
        ret["share"] = (jsonp["data"]["total_share"], jsonp["data"]["inc_share"])
        ret["dm"] = (jsonp["data"]["total_dm"], jsonp["data"]["incr_dm"])
        ret["fans"] = (jsonp["data"]["total_fans"], jsonp["data"]["incr_fans"])
        ret["elec"] = (jsonp["data"]["total_elec"], jsonp["data"]["inc_elec"])
        ret["fav"] = (jsonp["data"]["total_fav"], jsonp["data"]["inc_fav"])

        return ret, ""

    def get(self, url, params):
        headers = {
            "Accept": "*/*",
            "Accept - Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://member.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        }
        if self.cookie is not None: headers["Cookie"] = self.cookie

        response = requests.get(
            url,
            params=params,
            headers=headers
        )

        return response.status_code, response.text

# print(BDev().upstat())
# print(BDev().message())
# print(BDev().account())