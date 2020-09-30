# import json
#
# with open("deal_file2.json", "r", encoding="utf-8") as f:
#     r = json.loads(f.read().split(")]}'")[-1])
#     print(r)
#     print(type(r))

# import re
#
# r = re.compile(r"\bapi\.|(?<!\w)\$\.ajax(?!\w)|(?<!\w)\$http(?!\w)")
#
# string = "dasjfi $.ajax({   $.ajax   url: '/api/  url: '/api/statistic/getChartoOrTrendTime',     $http $ http  $httppp              url：后接接口名 \n"
#
# # print(r1.findall(string))
# # print(r2.findall(string))
# a = r.search(string)
# print(a.end())
# print(a[0])

# def test(type, a, b):
#     print(a) if type == "js" else print(b)
#
# test("php", 1, 2)

# a = "             * parameter1: driverId,description:驾驶员Id                 "
# msg_list = a.split("*")[-1].strip()
# print(msg_list)
# print(":" in msg_list)
# # i = msg_list.index(":")
# # print(i)
# list = msg_list.split(":", 1)
# # length = len(list)
# print(list)
# print(list[0])
# print(list[-1])
# key = msg_list[0].split("*")[-1].strip()
# print(key)
# print(value)
import re
# regex = re.compile(r"(?<=api\.)(\w+)")
# regex = re.compile(r"\{.*?\}")
# test = ["            api.editUserSetting({",
#         "                setting: JSON.stringify(vm.vehicleBaseField)",
#         # "                google: adjfiaodjfia.dfjaio,",
#         # "                vehicleId: vm.selectedVehicle.vehicleId,",
#         "                }).then(() => {",
#         "                if (data.data) {",
#         "                alert('修改成功');",
#         "            initializationHomePage(vm.selectedVehicle.vehicleId);",
#         "vm.showLiveDataComponentInfoSort(1);",
#         "} else {",
#         "alert('修改失败')",
#         "}",
#         "});"]
# string = "".join(test)
# # print(regex.search(string)[0])
# res = regex.search(string)[0]
# # print(len(res))
# result = res.split(",")
# # print(res)
# print(result[0])
# print(result[0].split("{")[-1].strip().split(":")[0])
# print(len(result))
# # print(len(result[1].split("}")[0].strip().split(":")[0]))
# print(result[1].strip().split(":")[0])

# test = [
# "   $.ajax({",
# "   url: '/api/dataManagement/queryDriverDetailInfoByCard',",
# "   data: {",
# "       'driverCard': driverNo,",
# "       'well': jujuju,",
# "       'ccc': bbbbbb",
# "   },",
# "   async: false,",
# "   dataType: 'json',",
# "   type: 'get',",
# "   success: function (data) {",
# "      console.log(data);",
# "      if (data.retcode == 1) {",
# "   let driver = data.data;"
# "   vm.liveData.dashboard.baseField.driverid.val = driver[0].driverid;"
# "   vm.liveData.dashboard.baseField.drivername.val = driver[0].drivername;"
# "   vm.liveData.basicInfos.drivername = driver[0].drivername;"
# "   } else {"
# "   console.warn('没有司机基本信息')"
# "   }"
# "   },"
# "   error: function () {"
# "   console.warn('司机信息查询失败')"
# "   }"
# "   });"]

# test = " $rules      =      [    'dept_id' => 'required',                   ]        ;        $this->apiParamVerify($rules);        $ret = (new BStatDrivingConfig())->getConfig($this->params);        return $this->setJsonResponse(SUCCESS, $ret);    }"
#
# regex = re.compile(r"(?<=\$rules)\s*=\s*\[.*?\]")
# print(regex.search(test).end())
# a = " $rules      =      [    'dept_id' => 'required',                   ]"

# print(len(a))

# for code_str in test:
#     if "url:" in code_str:
#         res = code_str.split(":")[-1]
# regex_param = re.compile(r"\w+\(.*?\)")
# # print(res)
# # print(res.strip().split("'")[1])
# # res = "".join(test)
# # print(res)
# # if "data:" in res:
# #     print(regex_param.search(res)[0].strip().split(":")[0].split("'")[1])
# res = regex_param.search(test)[0]
# print(res)
# func_name = res.split("(")[0]
# print(func_name)
# params = res.split("(")[-1].split(")")[0].strip()
# print(len(params))
# print(params)

# import json
# test = [{"a":[1,2,3,4,5]}, {"b":[5,6,76,7,8,9]}, {"c":[11,23,33,44,55]}]
# with open("jjj.txt", "w") as f:
#     f.write(json.dumps(test))
# regex_param = re.compile(r"(?<=\$rules)\s*=\s*\[.*?\]")
# allcode = "public function editViolationType()    {        $rules = [            'deptId' => 'required',            'vehicleType' => 'required',            'damageType' => 'required',            'dangerType' => 'required',            'badServiceType' => 'required',            'damageTypeCh' => 'required',            'dangerTypeCh' => 'required',            'badServiceTypeCh' => 'required',"
# res = regex_param.search(allcode)[0].strip().split("=", 1)[-1].strip()
# print(regex_param.search(allcode)[0].strip())

import requests

r = requests.get("http://111.42.40.137:8083/changes/php_web_api_v0~548/detail?O=516714")
print(r.status_code)