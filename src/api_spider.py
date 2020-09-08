import requests
import json

class Web_api:
    def __init__(self, pname):
        self.proj_name = pname
        self.login_url = "http://111.42.40.137:8083/login/%2Fq%2Fstatus%3Aopen"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"}
        self.subproj_url = "http://111.42.40.137:8083/changes/?O=81&S={}&n=25&q=project%3A{}"
        self.session = None

    def login(self):
        account = {"username":"liuqingli", "password":"liuqingli"}
        session = requests.session()
        session.post(self.login_url, headers=self.headers, data=account)
        return session

    def deal_json(self, json_str):
        return json.loads(json_str.split(")]}'")[-1])

    def parse_url(self, url):
        r = self.session.get(url)
        return r.content.decode()

    def get_link_list(self, page = 0):
        plink_list = []
        while True:
            p_url = self.subproj_url.format(page * 25, self.proj_name)
            print("当前的url： ", p_url)
            r, t_dict = self.deal_json(self.parse_url(p_url)), {}
            if len(r) > 0:
                temp_list = [{"id":i["id"], "subject":i["subject"], "number":i["_number"]} for i in r]
                t_dict[page + 1] = temp_list
                plink_list.append(t_dict)
                page += 1
            else:
                break
        return plink_list, page

    def save(self, plink_list):
        with open("test.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(plink_list, ensure_ascii=False, indent=2))
        print("ok")

    def run(self): # 主要逻辑实现
        # 1. 登陆
        self.session = self.login()
        # 2. 获取所有的当前页面链接信息
        plink_list, pages = self.get_link_list()  # 默认从第一页开始
        self.save(plink_list)
        # 测试看看能否成功
        # 3. ...
        # 4. 生成下一页链接，开始循环，直至页面结束
        pass