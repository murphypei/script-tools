
import re
import urllib.request

# url = r'http://www.vision.caltech.edu.s3-us-west-2.amazonaws.com/Image_Datasets/CaltechPedestrians/datasets/USA/res'

# with urllib.request.urlopen(r'http://www.vision.caltech.edu/Image_Datasets/CaltechPedestrians/datasets/USA/res/') as response:
#     html = response.read()
#     print(html)

# exit()

url = r'http://www.vision.caltech.edu/Image_Datasets/CaltechPedestrians/datasets/ETH/res/'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64)'
headers = {'User-Agent': user_agent}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as response:
    the_page = response.read()
    print(the_page)
# zip_pattern = r'^[\w%]+\.zip'
# url_pattern = re.compile(url + zip_pattern)

# for line in urllib.request.urlopen(url):
#     line = line.decode('utf-8')
#     link = url_pattern.findall(line)
#     if link:
#         print(link)


