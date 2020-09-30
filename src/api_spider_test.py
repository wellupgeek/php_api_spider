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
        if r.status_code == 200:
            return r.content.decode()
        return ""

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
        flag, find, is_flag = "", False, False
        record, r_end = len(cont), -1
        for line, code_str in enumerate(cont):
            if not find:
                r = regex.search(code_str)
                if r:
                    flag, find, record, r_end = r[0], True, line, r.end()
            if find and flag != "":
                if flag == "api.":
                    is_flag = True
                elif flag == "$.ajax" or flag == "$http":
                    if "url:" in code_str:
                        if "/api/" in code_str[code_str.index("url:") + 4: len(code_str)]:
                            is_flag = True
                else:
                    if "$rules" in code_str:
                        if "=" in code_str[code_str.index("$rules") + 6: len(code_str)]:
                            is_flag = True
            if is_flag:
                break
        if is_flag:
            return flag, r_end, True, record
        else:
            return flag, -1, False, record

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
                    if "/api/" in code_str[code_str.index("url:") + 4: len(code_str)]:
                        # print("code_str = ", code_str)
                        in_flag = True
                        # print(in_flag)
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
                    if "/api/" in code_str[code_str.index("url:") + 4: len(code_str)]:
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
                    if "=" in code_str[code_str.index("$rules") + 6: len(code_str)]:
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
        flag, endpos, status, line = self.judge_is_api(regex_js, cont) if code_type == "js" else self.judge_is_api(regex_php, cont)
        return flag, endpos, status, line

    def api_judge_out(self, pre_cont, code_type, regex_js, regex_php):    # 判断变更代码是否属于api接口代码
        # 先从pre_cont中倒着找，看能不能找到(看代码长度，可以往前找不超过300行，如果超过忽略)
        length = len(pre_cont)
        start = 0 if length <= 300 else length - 300
        copy_cont = pre_cont[start : length + 1]
        copy_cont.reverse()
        flag, endpos, status, line = self.judge_is_api(regex_js, copy_cont) if code_type == "js" else self.judge_is_api(regex_php, copy_cont)    # 这里判断是否有api接口代码
        # 如果有，则开始判断cont代码是否包含在该api接口代码结构中
        if status:
            copy_cont2 = copy_cont[0 : line + 1]
            copy_cont2.reverse()
            if self.judge_in_api(flag, endpos, copy_cont2):
                return flag, True, line
        return flag, False, line

    def judge_has_msg(self, pre_cont):
        # 往前找30行，如果找到"*/"，则开始往前找一直到找到"/**"为止，往上找的过程中需要进行记录
        # 对于像//这种的话，我们不予记录
        length = len(pre_cont)
        end = 0 if length <= 30 else length - 30
        flag, record, save_list = False, 0, []
        for i in range(length - 1, end - 1, -1):
            if "*/" in pre_cont[i]:
                flag, record = True, i
                break
        if flag:
            end_flag = False
            for j in range(record - 1, -1, -1):
                if not end_flag:
                    temp = pre_cont[j].split("*")[-1].strip()
                    if len(temp) > 0:
                        temp_flag = ""
                        if ":" in temp:
                            temp_flag = ":"
                        elif " " in temp:
                            temp_flag = " "
                        if temp_flag != "":
                            msg_list = temp.split(temp_flag, 1)
                            key, value = msg_list[0], msg_list[-1]
                            save_list.append({key: value})
                    if "/**" in pre_cont[j]:
                        end_flag = True
                else:
                    break
            if len(save_list) > 0:    # 意味着已经注释完成，如果没有":"，即如果是其他，此时save_list仍然为空，这种依然没有意义
                return True, save_list
        return False, save_list     # 没有找到*/ or save_list为空都算是没有意义的

    def params_utl(self, code_str, params, flag="{"):
        if flag == "{":
            first = code_str.split(flag)[-1].strip().split(":")[0]
            if len(first) > 0:
                params.append(first)
        else:
            last = code_str.split(flag)[0].strip().split(":")[0]
            if len(last) > 0:
                params.append(last)

    def produce_msg_interface(self, res_list, data, split_flag, end_flag):
        length = len(res_list)
        if length > 2:
            self.params_utl(res_list[0], data)
            for i in range(1, length - 1):
                other = res_list[i].strip().split(split_flag)[0]
                if len(other) > 0:
                    data.append(other)
            self.params_utl(res_list[-1], data, end_flag)
        elif length == 2:
            self.params_utl(res_list[0], data)
            self.params_utl(res_list[-1], data, end_flag)
        else:
            self.params_utl(res_list[0], data)

    def produce_msg(self, flag, cont):  # 没有就生成，此处的cont为api标志行到变更代码结束行
        save_list = []
        if flag == "api.":
            regex_func = re.compile(r"(?<=api\.)(\w+)")
            regex_param = re.compile(r"\{.*?\}")
            func_name = regex_func.search(cont[0])[0]
            all_code = "".join(cont)
            res = regex_param.search(all_code)[0]
            res_list = res.split(",")
            params = []
            self.produce_msg_interface(res_list, params, ":", "}")
            save_list.append({func_name:params})

        elif flag == "$.ajax":
            # 其内容信息在$.ajax(...)里面，url、data
            # 还是同上，先合并，然后"url:"一定在里面，判断"data:"在不在里面
            url, data = "", []
            for code_str in cont:
                if "url:" in code_str:
                    # print(code_str)
                    temp = code_str.split(":")[-1]
                    split_sign = "'" if "'" in temp else '"'
                    # print("temp = ", temp)
                    url = temp.strip().split(split_sign)[1]
                    break
            all_code = "".join(cont)
            if "data:" in all_code:
                regex_param = re.compile(r"(?<=data:)\s*\{.*?\}")
                res = ""
                res_temp = regex_param.search(all_code)
                if res_temp:
                    res = res_temp[0]
                else:
                    res2_temp = regex_param.search(all_code + "}")
                    if res2_temp:
                        res = res2_temp[0]
                if res != "":
                # res = regex_param.search(all_code)[0]
                    res_list = res.split(",")
                    self.produce_msg_interface(res_list, data, ":", "}")
            if url != 0 or len(data) > 0:
                save_list.append({url: data})

        elif flag == "$http":
            # $http()里面，method、url、params
            url, data = "", []
            for code_str in cont:
                if "url:" in code_str:
                    temp = code_str.split(":")[-1]
                    url = temp.strip().split("'")[1]
                    break
            all_code = "".join(cont)
            if "params:" in all_code:
                regex_param = re.compile(r"(?<=params:)\s*\{.*?\}")
                res = regex_param.search(all_code)[0]
                res_list = res.split(",")
                self.produce_msg_interface(res_list, data, ":", "}")
            save_list.append({url: data})

        else:
            # $rules = [...]里面, "xxx"
            #     "xxx" => "yyy"
            func_name, params = "", []
            regex_func = re.compile(r"\w+\s*\(.*?\)")
            for code_str in cont:
                if "function" in code_str and "public" in code_str:
                    temp = regex_func.search(code_str)[0]
                    func_name = temp.split("(")[0]
                    temp_param = temp.split("(")[-1].split(")")[0].strip()
                    if len(temp_param):
                        params.append(temp_param)
                    break
            regex_param = re.compile(r"(?<=\$rules)\s*=\s*\[.*?\]")
            all_code = "".join(cont)
            if "$rules" in all_code:
                res = ""
                res_temp = regex_param.search(all_code)
                if res_temp:
                    res = res_temp[0].strip().split("=", 1)[-1].strip()
                    # res = regex_param.search(all_code)[0].strip().split("=", 1)[-1].strip()
                else:
                    res2_temp = regex_param.search(all_code + "]")
                    if res2_temp:
                        res = res2_temp[0].strip().split("=", 1)[-1].strip()
                if res != "":
                    res_list = res.split(",")
                    self.produce_msg_interface(res_list, params, "=>", "]")
            if func_name != "" or len(params) > 0:
                save_list.append({func_name: params})
        return save_list

    def get_api_msg(self, flag, pre_cont, cont, line, in_out_flag):  # 确认为api接口代码后，找寻api描述信息---注释，这里pre_cont为api接口代码前一行开始往前的代码段, line是api标志的行号
        # 不同的注释要求信息还不太一样，先分类看看
        # 判断是否有注释信息，我们可以默认如果有注释信息则表明
        # api.标志前的代码段
        save_msg = []
        api_pre_cont = pre_cont[:] + cont[0:line] if in_out_flag == "in" else pre_cont[0:line]
        has_flag, msg_list = self.judge_has_msg(api_pre_cont)   # 看api.标志前的有没有注释信息
        # 以下是自动生成注释代码
        if has_flag:    # 有的话
            save_msg.append(msg_list)   # 保存信息
        else:   # 没有就自动生成
            need_cont = cont[line:len(cont)] if in_out_flag == "in" else pre_cont[line:len(pre_cont)] + cont[:]
            # print("need_cont = ", need_cont)
            temp_list = self.produce_msg(flag, need_cont)
            save_msg.append(temp_list)
        return save_msg

    def judge_code(self, pre_cont, cont, code_type, regex_js, regex_php):   # 这里pre_cont代表的就是ab公共代码
        flag, endpos, status, line = self.api_judge_in(cont, code_type, regex_js, regex_php)
        ans = []
        if not status:  # 注意line2的行号为ab公共代码从后往前数的行号
            pre_len = len(pre_cont)
            if pre_len != 0:
                flag2, status2, line2 = self.api_judge_out(pre_cont, code_type, regex_js, regex_php)    # 变更代码中没有，但被包含在api接口代码中的
                if status2:
                    ans = self.get_api_msg(flag2, pre_cont, cont, pre_len - line2 - 1, "out")
        else:   # 变更代码中有api接口的，直接找注释信息即可
            ans = self.get_api_msg(flag, pre_cont, cont, line, "in")
        return ans

    def cache(self):
        pass

    # def save(self, plink_list):
    #     with open("test.txt", "w", encoding="utf-8") as f:
    #         f.write(json.dumps(plink_list, ensure_ascii=False, indent=2))
    #     print("ok")

    def run(self):
        self.session = self.login() # 登陆
        plink_list, pages = self.get_link_list()  # 获取所有的当前页面链接信息, 默认从第一页开始
        # self.save(plink_list) # 测试
        regex_js = re.compile(r"\bapi\.|(?<!\w)\$\.ajax(?!\w)|^\s*\$http(?!\w)")    # 将正则对象提前准备好，优化时间
        regex_php = re.compile(r"\bpublic\s+function(?!\w)") #
        real_ans, cache = [], []
        # with open("analysis.json", "w", encoding="utf-8") as f:
        #     f.write(json.dumps(plink_list, ensure_ascii=False, indent=4))
        # print(plink_list)
        for i, p in enumerate(plink_list):
            for j in p[i + 1]:
                detail_url = self.detail_url.format(self.proj_name, j["number"])
                print("detail_url === ", detail_url)
                # 获取patch个数
                d_temp, detail = self.parse_url(detail_url), ""
                if d_temp != "":
                    detail = self.deal_json(d_temp)
                    patchs = len(detail["revisions"])
                    for patch in range(1, patchs + 1):  # 遍历每个patch
                        files_url = self.files_url.format(self.proj_name, j["number"], patch)
                        print("files_url === ", files_url)
                        files = self.deal_json(self.parse_url(files_url))
                        files_list = files.keys()
                        for f in files_list:  # 遍历每个文件
                            # print(f)
                            suffix = f.split(".")[-1]
                            if suffix in ["js", "php"]:
                                if self.path_judge(f):
                                    # print(files_url)
                                    diff_url = files_url + "/{}/diff?context=ALL&intraline&whitespace=IGNORE_NONE".format(
                                        quote(f, "utf-8"))
                                    diff_data = self.deal_json(self.parse_url(diff_url))  # 开始获取diff数据
                                    temp, linea, lineb = [], 0, 0
                                    code_type = "js" if suffix == "js" else "php"
                                    for cont in diff_data["content"]:
                                        if "ab" in cont:  # 公共代码, 记录代码行号，同时记录
                                            temp = cont["ab"]
                                            length = len(temp)
                                            linea += length
                                            lineb += length
                                        elif "a" in cont and "b" not in cont:  # 删除, 判断a, 记录代码行号
                                            temp_save = self.judge_code(temp, cont["a"], code_type, regex_js, regex_php)
                                            if len(temp_save) > 0:
                                                real_ans.append(temp_save)
                                            linea += len(cont["a"])
                                        elif "b" in cont and "a" not in cont:  # 新增，判断b，记录代码行号
                                            temp_save = self.judge_code(temp, cont["b"], code_type, regex_js, regex_php)
                                            if len(temp_save) > 0:
                                                real_ans.append(temp_save)
                                            lineb += len(cont["b"])
                                        else:  # 修改，调用删除，新增接口
                                            temp_save = self.judge_code(temp, cont["a"], code_type, regex_js, regex_php)
                                            if len(temp_save) > 0:
                                                real_ans.append(temp_save)
                                            else:
                                                temp_save_two = self.judge_code(temp, cont["b"], code_type, regex_js,
                                                                                regex_php)
                                                if len(temp_save_two) > 0:
                                                    real_ans.append(temp_save_two)
                                            linea += len(cont["a"])
                                            lineb += len(cont["b"])
                else:
                    break
        with open("save.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(real_ans, ensure_ascii=False, indent=4))

        # 关于缓存，我个人的意见是把已经确定的文件链接进行标记（包含patch），然后每次遍历时可以防止重复从而减少时间，弄一个缓存文件

if __name__ == "__main__":
    web_api = Web_api("php_web_api_v0", "111.42.40.137", "8083")
    print("开始运行！")
    web_api.run()
    print("运行结束！")