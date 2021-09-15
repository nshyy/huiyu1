from django.test import TestCase

# Create your tests here.
# import os
# from project_resource import settings
#
# username = 'huiyu'
# aaa = 'hhhh'
# ha = os.path.join(settings.MEDIA_ROOT, username, "th")
# a = settings.MEDIA_ROOT + ha
# print(username)
# print(ha)
#
#
# url = os.path.join(settings.MEDIA_ROOT, username, 'config_files')
#
# print(url)
# gave you color see see
# you can you up, no can no BB
# you can kill me, but you can not fuck me!
# url2 = os.path.join(settings.MEDIA_ROOT, username, "config_files")
# print(url2)


import jwt

aa = jwt.encode({'username':'运维咖啡吧','site':'https://ops-coffee.cn'},'secret_key',algorithm='HS256')