import requests
import json
from urllib.parse import quote

class Web_api:
    def __init__(self, pname, ip, port):  # ip = 111.42.40.137   port = 8083
        self.proj_name = pname
        base_ip = "http://" + ip + ":" + port
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"}
        self.login_url = base_ip + "/login/%2Fq%2Fstatus%3Aopen"
        self.subproj_url = base_ip + "/changes/?O=81&S={}&n=25&q=project%3A{}"
        self.detail_url = base_ip + "/changes/{}~{}/detail?O=516714"
        self.files_url = base_ip + "/changes/{}~{}/revisions/{}/files"
        # self.diff_url = "/{}/diff?context=ALL&intraline&whitespace=IGNORE_NONE"
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

    def path_judge(self, file_path):
        test_list = ["app/", "public/heu_assets/", "resources/views/alarm/"]
        for t in test_list:
            if t in file_path:
                return True
        return False

    # def save(self, plink_list):
    #     with open("test.txt", "w", encoding="utf-8") as f:
    #         f.write(json.dumps(plink_list, ensure_ascii=False, indent=2))
    #     print("ok")

    def run(self):
        self.session = self.login() # 登陆
        plink_list, pages = self.get_link_list()  # 获取所有的当前页面链接信息, 默认从第一页开始
        # self.save(plink_list) # 测试
        for i, p in enumerate(plink_list):
            for j in p[i + 1]:
                detail_url = self.detail_url.format(self.proj_name, j["number"])
                # 获取patch个数
                detail = self.deal_json(self.parse_url(detail_url))
                patchs = len(detail["revisions"])
                for patch in range(1, patchs + 1): # 遍历每个patch
                    files_url = self.files_url.format(self.proj_name, j["number"], patch)
                    files = self.deal_json(self.parse_url(files_url))
                    files_list = files.keys()
                    for f in files_list:    # 遍历每个文件
                        if f.split(".")[-1] in ["js", "php"]:
                            if self.path_judge(f):
                                diff_url = files_url + "/{}/diff?context=ALL&intraline&whitespace=IGNORE_NONE".format(quote(f, "utf-8"))
                                diff_data = self.deal_json(self.parse_url(diff_url))    # 开始获取diff数据

                                pass

        # 关于缓存，我个人的意见是把已经确定的文件链接进行标记（包含patch），然后每次遍历时可以防止重复从而减少时间