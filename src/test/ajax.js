$.ajax({
    url: '/api/dataManagement/queryDriverDetailInfoByCard',
    data: {
        'driverCard': driverNo
    },
    async: false,
    dataType: 'json',
    type: 'get',
    success: function (data) {
        console.log(data);
        if (data.retcode == 1) {
            let driver = data.data;
            vm.liveData.dashboard.baseField.driverid.val = driver[0].driverid;
            vm.liveData.dashboard.baseField.drivername.val = driver[0].drivername;
            vm.liveData.basicInfos.drivername = driver[0].drivername;
        } else {
            console.warn("没有司机基本信息")
        }
    },
    error: function () {
        console.warn("司机信息查询失败")
    }
});

api.getUserSetting({
    vehicleId: vehicleId
}).then((data) => {
    let Transformation = null;
    try {
        Transformation = JSON.parse(data);
    } catch (e) {
        console.log("数据非json格式:", e)
    } finally {
        //VTF-825 对于不同配置文件,停留在整车监控字段页面时切换的问题
        if (Transformation) {
            vm.vehicleBaseField = Transformation;
            vm.homePageSysClass = vm.tool.generateSysClassData(Transformation);
            if (vm.liveData.infoSortData) {
                console.log("缓存的系统键:", vm.liveData.infoSortData.key);
                if (Transformation[vm.liveData.infoSortData.key]) {
                    if (Transformation[vm.liveData.infoSortData.key].show) {
                        vm.showLvieData(vm.liveData.infoSortData.key);
                    } else {
                        console.log("新的配置文件中这个大类是隐藏的");
                        vm.showIndex();
                    }
                } else {
                    console.log("新的配置文件没有这个大类");
                    vm.showIndex();
                }
            }
        } else {
            console.log("获取到的用户配置JSON有问题")
        }
        return;
    }

});

$http({
    method: 'post',
    url: '/api/statistic/getAllVehicleSystems',
    params: {
        vehicleNo: vm.vehicleNo,
        vehicleId: vm.vehicleId
    }

}).then(function (response) {
    vm.dates = [];
    let arrr = 0;
    sysData = response.data.data;
    if (sysData.length != 0) {
        for (let skey in sysData) {
            vm.dates.push({key: skey, label: sysData[skey].cn, value: arrr++})
        }
        vm.subcomponentKey = sysData['activeSafety'].sun;
        vm.status = true;
    } else {
        vm.dates = [];
        vm.status = false;
    }
    // 获取状态信息
    getSatateData();
});

api.function().then()
$.ajax()
$http().then()



$.ajax({
                            url: '/api/dataManagement/queryVehicleList',
                            data: {
                                count: 10,
                                findKey: 'deviceId',
                                findVal: deviceId,
                                page: 1
                            },
                            success: function (response) {
                                $scope.businfo.sbh = deviceId;
                                $scope.businfo.cph = response.data.body.data[0].vehicleNo;
                                $scope.businfo.gs = response.data.body.data[0].companyName;
                                $scope.businfo.cllx = response.data.body.data[0].motorType;
                                $scope.businfo.cx = response.data.body.data[0].vehicleType;
                                offset(response.data.body.data[0].vehicleId, function (offsetting) {
                                    vm.Offset = offsetting;
                                });

                                driverDataApi($scope.businfo);
                                gpsStomerManager($scope.businfo, deviceId);
                            }
                        });