import requests
import json
from urllib.parse import quote
import re

class Web_api:
    def __init__(self, pname, ip, port):  # ip = 111.42.40.137   port = 8083
        self.proj_name = pname
        base_ip = "http://" + ip + ":" + port
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"}
        self.login_url = base_ip + "/login/%2Fq%2Fstatus%3Aopen"
        self.subproj_url = base_ip + "/changes/?O=81&S={}&n=25&q=project%3A{}"
        self.detail_url = base_ip + "/changes/{}~{}/detail?O=516714"
        self.files_url = base_ip + "/changes/{}~{}/revisions/{}/files"
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

    def judge_is_api(self, regex, cont):
        for line, code_str in enumerate(cont):
            r = regex.search(code_str)
            if r:
                return r[0], r.end(), True, line
        return "", -1, False, len(cont)

    def judge_in_api(self, flag, endpos, cont): # 此处的cont就是从api标志往下一直到变更代码开头
        if flag == "api.":   # api.function(...).then(...) | $http(...).then(...) or .catch(...) .finally()
        # 一般来说是 api.function().then()|catch()|finally(), 如果cont遍历完，括号没匹配完则说明变更代码包含在api接口代码中，否则就是不包含
            # 先找到api.后面的(，然后压入栈中，遇见)就弹出
            cont[0], stack, flag = cont[0][endpos : len(cont[0])], [], False
            num = 1
            for code_str in cont:
                p = -1
                for index, c in enumerate(code_str):
                    if num:
                        if c == "(":
                            stack.append("(")
                            flag = True
                        if c == ")" and flag:
                            stack.pop()
                            p = index
                        if len(stack) == 0 and flag: # ".then" or ".catch" or ".finally"   api.func().then()
                            num -= 1
                            length = len(code_str)
                            for k in [".then", ".catch", ".finally"]:
                                if k in code_str[p+1:length]:
                                    num += 1
                                    break
                    else:
                        break
                if num == 0:
                    break
            if len(stack) == 0: # 意味着stack为空，则说明api接口代码结构已经匹配完成
                return False
            else:
                return True

        elif flag == "$.ajax":  # $.ajax(...)   需要注意的是url这个参数，判断一下/api/是否在其中，如果在则说明这是和api接口有关的，否则则说明无关
            cont[0], stack, flag, in_flag = cont[0][endpos: len(cont[0])], [], False, False
            for code_str in cont:
                if "url:" in code_str:
                    if "/api/" in code_str[code_str.index("url:") + 4, len(code_str)]:
                        in_flag = True
                for c in code_str:
                    if c == "(":
                        stack.append("(")
                        flag = True
                    if c == ")" and flag:
                        stack.pop()
                    if len(stack) == 0 and flag:
                        break
            if len(stack) == 0:
                return False
            else:
                return True if in_flag else False

        elif flag == "$http":   # 同上，只不过结构和api.的相同
            cont[0], stack, flag, in_flag = cont[0][endpos: len(cont[0])], [], False, False
            num = 1
            for code_str in cont:
                p = -1
                if "url:" in code_str:
                    if "/api/" in code_str[code_str.index("url:") + 4, len(code_str)]:
                        in_flag = True
                for index, c in enumerate(code_str):
                    if num:
                        if c == "(":
                            stack.append("(")
                            flag = True
                        if c == ")" and flag:
                            stack.pop()
                            p = index
                        if len(stack) == 0 and flag:  # ".then" or ".catch" or ".finally"   api.func().then()
                            num -= 1
                            length = len(code_str)
                            for k in [".then", ".catch", ".finally"]:
                                if k in code_str[p + 1:length]:
                                    num += 1
                                    break
                    else:
                        break
                if num == 0:
                    break
            if len(stack) == 0:  # 意味着stack为空，则说明api接口代码结构已经匹配完成
                return False
            else:
                return True if in_flag else False

        else:   # flag == "public function", php型，找$rules, 结构就是public function xxx {...}
            cont[0], stack, flag, in_flag = cont[0][endpos: len(cont[0])], [], False, False
            for code_str in cont:
                if "$rules" in code_str:
                    if "=" in code_str[code_str.index("$rules") + 6, len(code_str)]:
                        in_flag = True
                for c in code_str:
                    if c == "{":
                        stack.append("{")
                        flag = True
                    if c == "}" and flag:
                        stack.pop()
                    if len(stack) == 0 and flag:
                        break
            if len(stack) == 0:
                return False
            else:
                return True if in_flag else False

    def api_judge_in(self, cont, code_type, regex_js, regex_php): # 判断变更代码中是否有api接口信息
        self.judge_is_api(regex_js, cont) if code_type == "js" else self.judge_is_api(regex_php, cont)

    def api_judge_out(self, pre_cont, code_type, regex_js, regex_php):    # 判断变更代码是否属于api接口代码
        # 先从pre_cont中倒着找，看能不能找到(看代码长度，可以往前找不超过300行，如果超过忽略)
        length = len(pre_cont)
        start = 0 if length <= 300 else length - 300
        copy_cont = pre_cont[start : length + 1]
        copy_cont.reverse()
        flag, endpos, status, line = self.judge_is_api(regex_js, copy_cont) if code_type == "js" else self.judge_is_api(regex_php, copy_cont)    # 这里判断是否有api接口代码
        # 如果有，则开始判断cont代码是否包含在该api接口代码结构中
        if status:
            copy_cont2 = copy_cont[0 : line + 1].reverse()
            self.judge_in_api(flag, endpos, copy_cont2)
            pass    # 根据不同的代码类型，以及不同的标志来决定不同的代码结构
        pass

    def get_api_msg(self):  # 确认为api接口代码后，找寻api描述信息---注释

        pass

    def judge_code(self, pre_cont, cont, code_type, regex_js, regex_php):
        flag, endpos, status, line = self.api_judge_in(cont, code_type, regex_js, regex_php)
        if not status:  # 注意line2的行号为ab公共代码从后往前数的行号
            flag2, endpos, status2, line2 = self.api_judge_out(pre_cont, code_type, regex_js, regex_php)    # 变更代码中没有，但被包含在api接口代码中的
            if status2:
                self.get_api_msg()
            else:   # 不在api接口代码中的
                pass
        else:   # 变更代码中有api接口的，直接找注释信息即可
            self.get_api_msg()

    # def save(self, plink_list):
    #     with open("test.txt", "w", encoding="utf-8") as f:
    #         f.write(json.dumps(plink_list, ensure_ascii=False, indent=2))
    #     print("ok")

    def run(self):
        self.session = self.login() # 登陆
        plink_list, pages = self.get_link_list()  # 获取所有的当前页面链接信息, 默认从第一页开始
        # self.save(plink_list) # 测试
        regex_js = re.compile(r"\bapi\.|(?<!\w)\$\.ajax(?!\w)|(?<!\w)\$http(?!\w)")    # 将正则对象提前准备好，优化时间
        regex_php = re.compile(r"\bpublic\s+function(?!\w)") #
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
                        suffix = f.split(".")[-1]
                        if suffix in ["js", "php"]:
                            if self.path_judge(f):
                                diff_url = files_url + "/{}/diff?context=ALL&intraline&whitespace=IGNORE_NONE".format(quote(f, "utf-8"))
                                diff_data = self.deal_json(self.parse_url(diff_url))    # 开始获取diff数据
                                temp, linea, lineb = [], 0, 0
                                code_type = "js" if suffix == "js" else "php"
                                for cont in diff_data["content"]:
                                    if "ab" in cont:    # 公共代码, 记录代码行号，同时记录
                                        temp = cont["ab"]
                                        length = len(temp)
                                        linea += length
                                        lineb += length
                                    elif "a" in cont and "b" not in cont:   # 删除, 判断a, 记录代码行号
                                        self.judge_code(temp, cont["a"], code_type, regex_js, regex_php)
                                        linea += len(cont["a"])
                                        pass
                                    elif "b" in cont and "a" not in cont:   # 新增，判断b，记录代码行号
                                        self.judge_code(temp, cont["b"], code_type, regex_js, regex_php)
                                        lineb += len(cont["b"])
                                        pass
                                    else:   # 修改，调用删除，新增接口
                                        self.judge_code(temp, cont["a"], code_type, regex_js, regex_php)
                                        linea += len(cont["a"])
                                        self.judge_code(temp, cont["b"], code_type, regex_js, regex_php)
                                        lineb += len(cont["b"])
                                        pass
                                pass

        # 关于缓存，我个人的意见是把已经确定的文件链接进行标记（包含patch），然后每次遍历时可以防止重复从而减少时间