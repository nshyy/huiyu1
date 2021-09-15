import sys

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, request
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
# from tkinter import filedialog
# import tkinter as tk
# from mttkinter import mtTkinter as tk
import json, re, os, uuid, time, io, shutil

from resource.fileCheck import *
from resource.models import User


class SaveJsonView(APIView):
    @csrf_exempt
    def post(self, request):
        response = {}
        try:
            data = request.data['saveData']
            if not data:
                response['code'] = 2
                response['msg'] = 'There is no data to save . '
                return Response(response)
            version = VersionListViewSet.list(self, request)
            if not version.data:
                response['code'] = 2
                response['msg'] = 'Please import the configuration file.'
                return Response(response)
            versionList = version.data["VERSION"].split(".")
            data = saveReviewData(self, data)
            save_datas = {
                "PLATFORM": request.data['platform'],
                "FAN TABLE VERSION": request.data['fanVersion'],
                "RELEASE DATE": request.data['releaseDate'],
                "VERSION": {
                    "SCHEMA_MAJOR": versionList[0],
                    "SCHEMA_MINOR": versionList[1],
                    "SCHEMA_AUX": versionList[2]
                },
                "THERMAL_ALGS": data
            }

            response['code'] = 200
            response['data'] = save_datas
            response['msg'] = 'Save the file successfully . '

            # root.mainloop()

        except Exception as e:
            response['msg'] = 'Server internal error : {}'.format(e)
            response['code'] = 1
        return Response(response)


# class SaveAsJsonView(APIView):
#     @csrf_exempt
#     def post(self, request):
#         response = {}
#         try:
#             data = request.data['saveData']
#             file_name = request.data['fileName']
#             if not data:
#                 response['code'] = 2
#                 response['msg'] = 'There is no data to save . '
#                 return Response(response)
#             root = tk.Tk()
#             root.title(string="Save As")
#             root.withdraw()
#             root.wm_attributes('-topmost', 1)
#             file_path = filedialog.asksaveasfile(initialfile=file_name,defaultextension=".json",filetypes=[("JSON FILE","json")])
#             if file_path == None:
#                 response['code'] = 4
#                 # response['msg'] = 'Cancel Save as . '
#                 return Response(response)
#             print(file_path, file_path.name, file_path.encoding)
#
#             version = VersionListViewSet.list(self, request)
#             if not version.data:
#                 response['code'] = 2
#                 response['msg'] = 'Please import the configuration file.'
#                 return Response(response)
#             versionList = version.data["VERSION"].split(".")
#             data = saveReviewData(self, data)
#             save_datas = {
#                 "VERSION":{
#                     "SCHEMA_MAJOR": versionList[0],
#                     "SCHEMA_MINOR": versionList[1],
#                     "SCHEMA_AUX": versionList[2]
#                 },
#                 "THERMAL_ALGS":data
#             }
#
#             with open(file_path.name, "w", encoding="UTF-8") as f:
#                 f.write(json.dumps(save_datas))
#                 f.close()
#             response['msg'] = 'Save the file {} successfully . '.format(file_path.name)
#             response['code'] = 200
#             # root.mainloop()
#         except Exception as e:
#             response['msg'] = 'Server internal error : {}'.format(e)
#             response['code'] = 1
#         return Response(response)


class ImportConView(APIView):
    '''导入配置文件接口'''

    @csrf_exempt
    def post(self, request):
        response = {}
        try:
            file = request.data.get('file')
            if file == "undefined":
                response['code'] = 2
                response['msg'] = 'Please select file . '
                return Response(response)
            file_type = re.match(r'.*\.(json)', file.name)
            if not file_type:
                response['code'] = 2
                response['msg'] = 'The file type is not match. Please import the json file again'
                return Response(response)
            file_url = self.save_file(file).data
            if is_json(file_url) is not True:
                os.remove(file_url)
                response['code'] = 2
                response['msg'] = "The FORMAT of the JSON file is incorrect. Please upload the json file again"
                return Response(response)
            with open(file_url, encoding='utf-8') as f:
                check_datas = json.loads(f.read())
                f.close()
            if "common_thermal_device" not in check_datas.keys() or "common_thermal_algorithm" not in check_datas.keys():
                response['code'] = 2
                response['msg'] = 'The file is not a schema file. Import failed . '
                return Response(response)

            response['code'] = 200
            response['msg'] = "The configuration file {} was imported successfully".format(file.name)
            response['file'] = file_url
        except Exception as e:
            response['msg'] = 'Server internal error : {}'.format(e)
            response['code'] = 1
        return Response(response)

    def save_file(self, file):
        filename = file.name
        # url = settings.MEDIA_ROOT + "/config_files"
        url = os.path.join(settings.MEDIA_ROOT, username, "config_files")

        if os.path.isdir(url) is False:
            os.mkdir(url)
        shutil.rmtree(url)
        os.mkdir(url)

        filepath = os.path.join(url, filename)
        with open(filepath, 'wb') as fp:
            for chunk in file:
                fp.write(chunk)
            fp.close()
        return Response(filepath)


class LoadJsonView(APIView):
    '''上传load文件接口'''

    @csrf_exempt
    def post(self, request):
        response = {}
        try:
            file = request.data.get('file')
            if file == "undefined":
                response['code'] = 2
                response['msg'] = 'Please select file . '
                return Response(response)
            file_type = re.match(r'.*\.(json)', file.name)
            if not file_type:
                response['code'] = 2
                response['msg'] = 'The file type is not json. Please upload the json file again'
                return Response(response)
            file_url = self.save_file(file).data
            if is_json(file_url) is not True:
                os.remove(file_url)
                response['code'] = 2
                response['msg'] = "The FORMAT of the JSON file is incorrect. Please upload the json file again"
                return Response(response)
            with open(file_url, encoding='utf-8') as f:
                check_datas = json.loads(f.read())
                f.close()
            if "THERMAL_ALGS" not in check_datas.keys():
                response['code'] = 2
                response['msg'] = 'The file is not a load file. Load failed . '
                return Response(response)

            file_name = file.name
            if "PLATFORM" in check_datas.keys():
                file_name = file_name.replace("_" + check_datas["PLATFORM"], '')
            if "FAN TABLE VERSION" in check_datas.keys():
                file_name = file_name.replace("_" + check_datas["FAN TABLE VERSION"], "")
            if "RELEASE DATE" in check_datas.keys():
                file_name = file_name.replace(
                    "_" + check_datas["RELEASE DATE"].replace("-", "").replace(" ", "").replace(":", ""), "")

            check_version = checkVersion(self, request, check_datas)
            if check_version is not True:
                response['code'] = 3
                response[
                    'msg'] = "The version of json file ({}) is inconsistent with schema. The json file's version is {}, schema version is {}. Do you want to continue? ".format(
                    file.name, check_version['load_version'], check_version['import_version'])
                response['fileName'] = file_name.replace(".json", "")
                return Response(response)
            '''
            校验device/algorithm是否合法
            check_device = checkDevice(self, request, check_datas)
            # if check_device:
            #     response['code'] = 2
            #     response['msg'] = "以下device不被支持：{}".format(check_device)
            #     return Response(response)
            check_algorithm = checkAlgorithm(self, request, check_datas)
            # if check_algorithm:
            #     response['code'] = 2
            #     response['msg'] = "以下algorithm不被支持：{}".format(check_device)
            #     return Response(response)
            '''
            response['code'] = 200
            response['msg'] = "Load file {} successfully".format(file.name)
            response['fileName'] = file_name.replace(".json", "")
        except Exception as e:
            response['msg'] = 'Server internal error : {}'.format(e)
            response['code'] = 1
        return Response(response)

    def save_file(self, file):
        filename = file.name
        # url = settings.MEDIA_ROOT + "/load_files"

        url = os.path.join(settings.MEDIA_ROOT, username, 'load_files')

        if os.path.isdir(url) is False:
            os.mkdir(url)
        shutil.rmtree(url)
        os.mkdir(url)

        filepath = os.path.join(url, filename)
        with open(filepath, 'wb') as fp:
            for chunk in file:
                fp.write(chunk)
            fp.close()
        return Response(filepath)


class ConfigFilesListViewSet(viewsets.ViewSet):
    '''获取 导入配置 文件'''

    def list(self, request):
        files = []
        # for i in os.listdir(settings.MEDIA_ROOT + "/config_files"):
        for i in os.listdir(os.path.join(settings.MEDIA_ROOT, username, "config_files")):
            files.append(i)
        return Response(files)


class LoadFilesListViewSet(viewsets.ViewSet):
    '''获取 load实例 文件'''

    def list(self, request):
        files = []
        # for i in os.listdir(settings.MEDIA_ROOT + "/load_files"):
        for i in os.listdir(os.path.join(settings.MEDIA_ROOT, username, "load_files")):
            files.append(i)
        return Response(files)


class DeviceListViewSet(viewsets.ViewSet):
    def list(self, request):
        '''获取 device 数据'''
        response = {}
        try:
            files = ConfigFilesListViewSet.list(self, request)
            for file_name in files.data:
                # path = settings.MEDIA_ROOT + "/config_files/" + file_name
                path = os.path.join(settings.MEDIA_ROOT, username, "config_files", file_name)
                with open(path, encoding='utf-8') as f:
                    datas = json.loads(f.read())
                    f.close()
                if "common_thermal_device" in datas:
                    return Response(datas['common_thermal_device'])

            response['msg'] = "Import the configuration file"
            return Response(Response)
        except Exception as e:
            response['msg'] = 'Server internal error : {}'.format(e)
            return Response(response)


class AlgorithmListViewSet(viewsets.ViewSet):
    def list(self, request):
        '''获取 algorithm 数据'''
        response = {}
        try:
            files = ConfigFilesListViewSet.list(self, request)
            for file_name in files.data:
                # path = settings.MEDIA_ROOT + "/config_files/" + file_name
                path = os.path.join(settings.MEDIA_ROOT, username, "config_files", file_name)
                with open(path, encoding='utf-8') as f:
                    datas = json.loads(f.read())
                    f.close()
                if "common_thermal_algorithm" in datas:
                    return Response(datas['common_thermal_algorithm'])

            response['msg'] = "Import the configuration file"
            return Response(Response)
        except Exception as e:
            response['msg'] = 'Server internal error : {}'.format(e)
            return Response(response)


class VersionListViewSet(viewsets.ViewSet):
    def list(self, request):
        '''获取 version 数据'''
        response = {}
        try:
            files = ConfigFilesListViewSet.list(self, request)
            for file_name in files.data:
                # path = settings.MEDIA_ROOT + "/config_files/" + file_name
                path = os.path.join(settings.MEDIA_ROOT, username, "config_files", file_name)

                with open(path, encoding='utf-8') as f:
                    datas = json.loads(f.read())
                    f.close()
                if "version" in datas:
                    if "SCHEMA_MAJOR" in datas["version"] and "SCHEMA_MINOR" in datas["version"] and "SCHEMA_AUX" in \
                            datas["version"]:
                        response_data = {
                            "VERSION": "{}.{}.{}".format(datas["version"]['SCHEMA_MAJOR'],
                                                         datas["version"]['SCHEMA_MINOR'],
                                                         datas["version"]['SCHEMA_AUX']),
                        }
                        return Response(response_data)

            response['msg'] = "Import the configuration file"
            return Response(response)
        except Exception as e:
            response['msg'] = 'Server internal error : {}'.format(e)
            return Response(response)


class PolicyListViewSet(viewsets.ViewSet):
    def list(self, request):
        '''获取 policy 数据'''
        response = {}

        try:
            files = LoadFilesListViewSet.list(self, request)
            for file_name in files.data:
                # path = settings.MEDIA_ROOT + "/load_files/" + file_name
                path = os.path.join(settings.MEDIA_ROOT, username, "load_files", file_name)
                with open(path, encoding='utf-8') as f:
                    datas = json.loads(f.read())
                    f.close()
                checkDevice(self, request, datas)
                checkAlgorithm(self, request, datas)
                if "THERMAL_ALGS" in datas:
                    for policy in datas["THERMAL_ALGS"]:
                        if "CATEGORY" not in policy.keys():
                            policy["CATEGORY"] = ""

                    response_data = {
                        "FILENAME": "",
                        "PLATFORM": "",
                        "FAN TABLE VERSION": "",
                        "RELEASE DATE": ""
                    }
                    if "PLATFORM" in datas.keys():
                        response_data['PLATFORM'] = datas["PLATFORM"]
                        file_name = file_name.replace("_" + datas["PLATFORM"], '')
                    if "FAN TABLE VERSION" in datas.keys():
                        response_data['FAN TABLE VERSION'] = datas["FAN TABLE VERSION"]
                        file_name = file_name.replace("_" + datas["FAN TABLE VERSION"], "")
                    if "RELEASE DATE" in datas.keys():
                        response_data['RELEASE DATE'] = datas["RELEASE DATE"]
                        file_name = file_name.replace(
                            "_" + datas["RELEASE DATE"].replace("-", "").replace(" ", "").replace(":", ""), "")
                    response_data['FILENAME'] = file_name
                    response_data['THERMAL_ALGS'] = datas['THERMAL_ALGS']
                    return Response(response_data)

            response['msg'] = "Please upload the load file"
            return Response(response)
        except Exception as e:
            response['msg'] = 'Server internal error : {}'.format(e)
            return Response(response)


class CategoryListViewSet(viewsets.ViewSet):
    def list(self, request):
        '''获取 Category 数据'''
        response = {}
        # "All",
        try:
            category_all = [
                "Amb_Open_Loop", "PCI_Tier", "CPU_PID", "CPU_Power_Band", "DIMM", "GPU_Close_Loop",
                "GPU_Open_Loop", "Thermal_Sensor", "Power_Cap", "Fan_Weight", "Fan_Fail", "SDR"
            ]
            return Response(category_all)
            # response['msg'] = "Please upload the category file"
        except Exception as e:
            response['msg'] = 'Server internal error : {}'.format(e)
            return Response(response)


class LoginView(APIView):
    '''登录'''

    def post(self, request):
        global username
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username, password=password).first()
        if user:
            path = os.path.join(settings.MEDIA_ROOT, username)
            isExists = os.path.exists(path)
            if not isExists:
                os.makedirs(path)
            else:
                pass
            return Response({'msg': 'ok', 'code': 200, 'uid': user.id})
        return Response({'msg': 'no', 'code': 500})

    '''修改密码'''

    def put(self, request):
        username = request.data.get('username')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')
        if User.objects.filter(username=username):
            if password2 == password1:
                User.objects.filter(username=username).update(password=password1)
                return Response({'msg': 'ok', 'code': 200})
            else:
                return Response({'msg': '两次密码不一致', 'code': 500})
        else:
            return Response({'msg': '用户不存在', 'code': 500})


class RegisterView(APIView):
    '''注册'''

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if len(username) > 30 or len(password) > 30 or len(username) < 1 or len(password) < 1:
            return Response({'msg': '请输入1-30个字符', 'code': 500})
        if User.objects.filter(username=username):
            return Response({'msg': '该用户已存在', 'code': '500'})
        else:
            User.objects.create(username=username, password=password)
            return Response({'msg': 'ok', 'code': 200})


'''

'''
