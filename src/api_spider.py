import requests

class Web_api:
    def __init__(self):
        self.login_url = "http://111.42.40.137:8083/login/%2Fq%2Fstatus%3Aopen"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"}
        pass

    def login(self):
        account = {"username":"liuqingli", "password":"liuqingli"}
        session = requests.session()
        response = session.post(self.login_url, headers=self.headers, data=account)

    def run(self): # 主要逻辑实现
        # 1. 登陆

        # 2. 获取所有的当前页面链接信息
        # 3. ...
        # 4. 生成下一页链接，开始循环，直至页面结束
        pass