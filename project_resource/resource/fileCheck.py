import json
from resource import views

def is_json(url):
    '''检测json文件格式'''
    try:
        json.loads(open(url).read())
    except Exception as e:
        return e
    return True


def checkVersion(self, request, params):
    '''校验 import && load 文件的version'''
    import_version = views.VersionListViewSet.list(self, request).data['VERSION']
    load_version = 0
    if "VERSION" in params:
        if "SCHEMA_MAJOR" in params["VERSION"] and "SCHEMA_MINOR" in params["VERSION"] and "SCHEMA_AUX" in params["VERSION"]:
            load_version = "{}.{}.{}".format(params["VERSION"]['SCHEMA_MAJOR'], params["VERSION"]['SCHEMA_MINOR'],
                                             params["VERSION"]['SCHEMA_AUX'])
    if load_version is None or import_version != load_version:
        return {"load_version":load_version, "import_version":import_version}
    else:
        return True


def checkDevice(self, request, params):
    '''校验 import && load 文件的device'''
    import_device_all = []
    load_deivce_inexist = []
    for i in views.DeviceListViewSet.list(self, request).data:
        import_device_all.append(i)
    if "THERMAL_ALGS" in params:
        for i in params["THERMAL_ALGS"]:
            for j in i["CONDITIONS"]:
                if "DAO" in j.keys():
                    device = j["DAO"].split(".")[0]
                    if device not in import_device_all:
                        i["CONDITIONS"].remove(j)
                        j.clear()
                        load_deivce_inexist.append(device)

    return load_deivce_inexist


def checkAlgorithm(self, request, params):
    import_algorithm_all = []
    load_algorithm_inexist = []
    for i in views.AlgorithmListViewSet.list(self, request).data:
        import_algorithm_all.append(i)
    if "THERMAL_ALGS" in params:
        for i in params["THERMAL_ALGS"]:
            if i["TYPE"] not in import_algorithm_all:
                load_algorithm_inexist.append(i["TYPE"])
                params["THERMAL_ALGS"].remove(i)

    return load_algorithm_inexist


def saveReviewData(self, params):
    new_params = []
    for i in params:
        new_i = {}
        for dict_key,dict_value in i.items():
            if ((dict_key == "index") or (dict_key == "internalIndex")):
                continue 
            if dict_key == "action":
                action_list = i["action"]
                action_list_new = []
                for j in action_list:
                    action_list_new.append(int(j.split("FAN")[-1]))
                dict_value = action_list_new
            new_i[dict_key.upper()] = dict_value
        new_params.append(new_i)
    return new_params



