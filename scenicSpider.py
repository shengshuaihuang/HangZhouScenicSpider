# -*- coding: utf-8 -*-
import json, urllib
from urllib import request, parse

from html.parser import HTMLParser
import time

import os
import random

header1 = {'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}
header2 = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'}
header3 = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}
header4 = {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'}
header5 = {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'}
header6 = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'}
header7 = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'}
header8 = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)'}
headers = [header1, header2, header3, header4, header5, header6, header7, header8]

def _attr(attrlist, attrname):
	for attr in attrlist:
		if attr[0] == attrname:
			return attr[1]
	return None


class ScenicParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.in_div = False
		self.in_subdiv = False
		self.in_innerScenicdiv = False
		self.in_ul = False
		self.in_dl = False
		self.in_dt = False
		self.in_dd = False
		self.in_locationP = False
		self.in_locationDiv = False
		self.baseinfoIndex = ''
		self.baseinfoItem = ''
		self.flag = False
		self.scenic = {}
		self.scenic['desc'] = ''
		self.scenic['location'] = ''
		self.scenic['innerScenic'] = []

	def handle_starttag(self, tag, attrs):
		if tag == 'div' and _attr(attrs, 'class') == 'mod mod-detail':
			self.in_div = True

		if tag == 'div' and _attr(attrs, 'class') == 'mbd':
			self.in_innerScenicdiv = True

		if tag == 'div' and _attr(attrs, 'data-anchor') == 'commentlist':
			self.in_innerScenicdiv = False

		if tag == 'div' and _attr(attrs, 'class') == 'mod mod-location':
			self.in_div = False
			self.in_locationDiv = True

		if tag == 'div' and _attr(attrs, 'class') == 'mbd clearfix':
			self.in_locationDiv = False

		if tag == 'div' and _attr(attrs, 'class') == 'summary':
			# print('into subdiv')
			self.in_subdiv = True

		if tag == 'ul' and _attr(attrs, 'class') == 'baseinfo clearfix':
			# print('into ul')
			self.in_ul = True

		if tag == 'dl' and self.in_div:
			# print('into dl')
			self.in_dl = True

		if tag == 'dt' and self.in_dl:
			self.in_dt = True

		if tag == 'dd' and self.in_dl:
			self.in_dd = True

		if tag == 'p' and self.in_locationDiv:
			self.in_locationP = True



		if tag == 'a' and self.in_innerScenicdiv:
			innerScenic = {}
			innerScenic['id'] = attrs[0][1].split('.')[0].split('/')[-1]
			innerScenic['name'] = attrs[2][1]
			self.scenic['innerScenic'].append(innerScenic)

	def handle_endtag(self, tag):
		if tag == 'div' and self.in_subdiv:
			# print('leave subdiv')
			self.in_subdiv = False

		if tag == 'ul' and self.in_ul:
			# print('leave ul')
			self.in_ul = False

		if tag == 'dl' and self.in_div:
			# print('leave dl')
			self.in_dl = False

		if tag == 'dt' and self.in_dl:
			self.in_dt = False

		if tag == 'dd' and self.in_dl:
			self.in_dd = False

	def handle_data(self, data):
		if self.in_subdiv:
			# print(data.strip())
			self.scenic['desc'] = self.scenic['desc'] + data.strip() + '\n'

		if self.in_ul:
			if len(data.strip())>0:
				if len(self.baseinfoIndex) == 0:
					self.baseinfoIndex = data.strip()
				else:
					self.scenic[self.baseinfoIndex] = data.strip()
					self.baseinfoIndex = ''

		if self.in_dl and self.in_dt:
			if len(self.baseinfoItem)>0:
				self.scenic[self.baseinfoIndex] = self.baseinfoItem
				self.baseinfoItem = ''
			self.baseinfoIndex = data.strip()

		if self.in_dl and self.in_dd:
			if len(data.strip())>0:
				self.baseinfoItem = self.baseinfoItem + data.strip() + '\n'

		if self.in_locationP and self.in_locationDiv:
			if len(data.strip())>0:
				self.scenic['location'] =data.strip()


class ScenicUrlParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.data = []
		self.url = ''
		self.src = ''

	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			self.url = 'http://www.mafengwo.cn' + attrs[0][1]
		if tag == 'img':
			self.src = attrs[0][1]
			self.data.append({'url': self.url, 'src': self.src})
			self.url = ''
			self.src = ''


class ScenicLocationParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.NearbyScenicInfoList = []
		self.NearbyScenicInfo = {}
		self.in_span = False
		self.in_p = False

	def handle_starttag(self, tag, attrs):
		if tag == 'li':
			for attr in attrs:
				key = attr[0].split('-')[-1]
				item = attr[1]
				self.NearbyScenicInfo[key] = item
		if tag == 'span':
			self.in_span = True

		if tag == 'p':
			self.in_p = True
			print('encounter p')

	def handle_endtag(self, tag):
		if tag == 'span':
			self.in_span = False
		if tag == 'p':
			self.in_p = False

	def handle_data(self, data):
		if self.in_p:
			self.NearbyScenicInfo['location'] = data.strip()
		if self.in_span:
			self.NearbyScenicInfo['dist'] = data.strip()
			self.NearbyScenicInfoList.append(self.NearbyScenicInfo)
			self.NearbyScenicInfo = {}



def getAllScenicUrl():
	url_base = 'http://www.mafengwo.cn/ajax/router.php'
	sAct = 'KMdd_StructWebAjax%7CGetPoisByTag'
	iMddid = '10156'
	iTagId = '0'

	scenicUrl = []

	for i in range(1,46,1):
		iPage = str(i)
		url = url_base + '?sAct=' + sAct + '&iMddid=' +  iMddid + '&iTagId=' +  iTagId + '&iPage=' + iPage
		try:
			header = headers[random.randint(0,7)]
			req = request.Request(url=url,headers = header)
			res = request.urlopen(req, timeout = 3)
			result = res.read().decode('utf-8')
			result_json = json.loads(result)
			parser = ScenicUrlParser()
			parser.feed(result_json['data']['list'])
			scenicUrl.extend(parser.data)
		except:
			print('[ERROR] getAllScenicUrl failed!')

	with open('scenicHangZhouUrls.json', 'w') as f:
		json.dump(scenicUrl, f)
	return scenicUrl

# 通过json获取id为scenicId景区的经纬度信息、名称及附近景点和距离
def getScenicLocation(scenicId):
	locationUrlPrefix = 'http://pagelet.mafengwo.cn/poi/pagelet/poiLocationApi'
	params = '%7B%22poi_id%22%3A%22' + scenicId + '%22%7D' 
	timeFlag = str(int(time.time())*1000)
	locationUrl = locationUrlPrefix + '?params=' + params + '&_=' + timeFlag

	try:
		header = headers[random.randint(0,7)]
		req = request.Request(url = locationUrl, headers = header)
		res = request.urlopen(req, timeout = 3)
		result = res.read().decode('utf-8')
		result_json = json.loads(result)

		scenicInfo = result_json['data']['controller_data']['poi']

		scenicInfo_nearby = result_json['data']['html']
		parser = ScenicLocationParser()
		parser.feed(scenicInfo_nearby)
		scenicInfo['nearby'] = parser.NearbyScenicInfoList
	except Exception as e:
		scenicInfo = {}
		print(scenicId, 'getScenicLocation except:', e)
	finally:
		return scenicInfo

def getScenicCommentsCount(scenicId):
	url = 'http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi?params={"poi_id":"' + scenicId + '"}'
	header = headers[random.randint(0,7)]
	req = request.Request(url = url, headers = header)
	res = request.urlopen(req, timeout = 3)
	result = res.read().decode('utf-8')
	result_json = json.loads(result)
	commentCount = result_json['data']['controller_data']['comment_count']
	return commentCount

def getScenicInfo(url):
	try:
		header = headers[random.randint(0,7)]
		req = request.Request(url = url)
		res = request.urlopen(req, timeout = 3)
		result = res.read().decode('utf-8')
		parser = ScenicParser()
		parser.feed(result)
	except Exception as e:
		parser.scenic = {}
		print(url, 'getScenicInfo except:', e)
	finally:
		return parser.scenic


def main():
	if os.path.exists('scenicHangZhouUrls.json')
		f = open('scenicHangZhouUrls.json', 'r')
		content = f.read()
		scenicUrls_temp = json.loads(content)
		scenicUrls = scenicUrls_temp
		f.close()
	else:
		scenicUrls = getAllScenicUrl()

	scenicInfo = {}
	errorList = []
	for index, item in enumerate(scenicUrls):
		url = item['url']
		src = item['src']
		print('[', time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()), ']', index)
		scenicId = url.split('.')[-2].split('/')[-1]
		getScenicInfoResult = getScenicInfo(url)
		getScenicLocationResult = getScenicLocation(scenicId)
		getCommentCount = getScenicCommentsCount(scenicId)

		if len(getScenicInfoResult) !=0 and len(getScenicLocationResult) !=0:
			scenicInfo[scenicId] = dict(getScenicInfoResult, **getScenicLocationResult)
			scenicInfo[scenicId]['src'] = src
			scenicInfo[scenicId]['commentCount'] = getCommentCount
		else:
			print('a new error occurred!')
			errorList.append(url)
		time.sleep(3)
		if index%10==0:
			with open('scenicHangZhouInfo'+ str(index) +'.json', 'w') as outfile:
				json.dump(scenicInfo, outfile)

	with open('scenicErrorList.json', 'w') as outfile:
		json.dump({"list": errorList}, outfile)
	with open('scenicHangZhouInfo_final.json', 'w') as outfile:
				json.dump(scenicInfo, outfile)
	print('[', time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()), '] saved successfully!')


if __name__ == '__main__':
	main()
	# getAllScenicUrl()
	# getScenicCommentsCount('1093')
