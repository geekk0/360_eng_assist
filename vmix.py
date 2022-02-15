import traceback

import requests


headers = {'User-agent':'Mozilla/5.0','Referer':'http://www.python.org/'}
session = requests.Session()
"""adapter = requests.adapters.HTTPAdapter(max_retries=10)
session.mount('http://', adapter)"""

url = 'http://185.18.202.220:8088/api/?Function=OpenPreset&Value=C:/Users/Admin/Desktop/VMIX-PROJECTS/testpreset.vmix'
# url = 'http://185.18.202.220:8088/api/?Function=StartPlayList'

# url = 'http://185.18.202.220:8088/api/?Function=AddInput&Value='

req = requests.get(url)
print(req.text)


