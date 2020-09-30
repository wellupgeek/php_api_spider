import requests
import json
from urllib.parse import quote

class Network:
    def __init__(self, pro_name, ip, port, cache):
        base_url = "http://" + ip + ":" + port
        self.pro_name = pro_name
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"}
        self.login_url = base_url + "/login/%2Fq%2Fstatus%3Aopen"
        self.subproj_url = base_url + "/changes/?O=81&S={}&n=25&q=project%3A{}"
        self.detail_url = base_url + "/changes/{}~{}/detail?O=516714"
        self.files_url = base_url + "/changes/{}~{}/revisions/{}/files"
        self.session = None
        self.cache = cache
        self.new_cache = []

    def login(self):
        account = {"username":"liuqingli", "password":"liuqingli"}
        session = requests.session()
        session.post(self.login_url, headers=self.headers, data=account)
        self.session = session

    def deal_json(self, json_str):  #把响应内容变成真正的json文件后读取
        return json.loads(json_str.split(")]}'")[-1])

    def parse_url(self, url):
        r = self.session.get(url)
        return r.content.decode() if r.status_code == 200 else ""

    def get_subproj_urls(self, page = 0):   # 默认从第一页开始, 返回每页对应的子项目url，格式[{1:[1263, 1123]},{}]
        subpurl_list = []
        while True:
            p_url = self.subproj_url.format(page * 25, self.pro_name)  # 获取每一页的所有子项目链接
            print("当前的url： ", p_url)
            r = self.deal_json(self.parse_url(p_url))
            if len(r) > 0:
                t_dict = {"page":page + 1, "p_url":p_url, "nums":[i["_number"] for i in r]}
                subpurl_list.append(t_dict)
                page += 1
            else:
                break
        return subpurl_list

    def get_file_urls(self, subpurl_list):
        subp_record = []
        for p_list in subpurl_list:
            for num in p_list["nums"]:
                url = self.detail_url.format(self.pro_name, num)
                d_temp = self.parse_url(url)
                if d_temp != "":
                    detail = self.deal_json(d_temp)
                    patchsets = len(detail["revisions"])
                    temp_dict = {"subject":detail["subject"], "id":detail["id"],
                                 "files":{"files_url":[self.files_url.format(self.pro_name, num, patch) for patch in range(1,patchsets + 1)],
                                          "patchsets":patchsets}}
                    subp_record.append(temp_dict)
        return subp_record

    def path_judge(self, file_path):
        test_list = ["app/", "public/heu_assets/", "resources/views/alarm/"]
        for t in test_list:
            if t in file_path:
                return True
        return False

    def get_code_urls(self, subp_record):
        diff_list = []
        for p in subp_record:
            for url in p["files"]["files_url"]:
                if url not in self.cache:
                    self.new_cache.append(url)
                    files = self.deal_json(self.parse_url(url))
                    print("url: ", url)
                    if files != "":
                        files_list = files.keys()
                        for f in files_list:
                            suffix = f.split(".")[-1]
                            if suffix in ["js", "php"]:
                                if self.path_judge(f):
                                    diff_url = url + "/{}/diff?context=ALL&intraline&whitespace=IGNORE_NONE".format(quote(f, "utf-8"))
                                    temp = {"subject":p["subject"], "id":p["id"], "file_path":url, "file_type":suffix, "diff_url":diff_url}
                                    diff_list.append(temp)
        return diff_list

    def get_code_content(self, diff_list):
        for f in diff_list:
            content = self.deal_json(self.parse_url(f["diff_url"]))["content"]
            f["content"] = content

    def run(self):
        #1.登录
        self.login()
        #2. 获取所有子项目链接
        subpurl_list = self.get_subproj_urls()
        #3. 获取子项目所有文件链接(判断js和php以及路径)
        subp_record = self.get_file_urls(subpurl_list)
        #4. 获取对应的代码信息
        diff_list = self.get_code_urls(subp_record)
        #5. 获取diff请求的响应，即代码内容
        self.get_code_content(diff_list)
        del subpurl_list
        del subp_record
        return diff_list

# if __name__ == "__main__":
#     start = time.time()
#     cache = []
#     if os.path.exists("cache.txt"):
#         with open("cache.txt", "r", encoding="utf-8") as f:
#             for line in f.readlines():
#                 cache.append(line.split("\n")[0])
#     else:
#         open("cache.txt", "w")
#     network = Network("php_web_api_v0", "111.42.40.137", "8083", cache)
#     network.run()
#     end = time.time()
#     print("共花费时间%.2f秒" %(end-start))
#     with open("cache.txt", "a", encoding="utf-8") as f:
#         for line in network.new_cache:
#             f.write(line)
#             f.write("\n")