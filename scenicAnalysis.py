import json, urllib
from urllib import request, parse
from html.parser import HTMLParser
import time
import random

filePath = 'scenicHangZhouInfo_final.json'
nopic = 'http://n4-q.mafengwo.net/s9/M00/73/E4/wKgBs1g8-y-AL_isAAHdRTpMkzU24.jpeg'

def saveAsExcel():
	f = open(filePath, 'r')
	scenics = json.loads(f.read())
	f.close()
	import xlwt

	style = xlwt.XFStyle()
	alignment = xlwt.Alignment()
	alignment.horz = xlwt.Alignment.HORZ_CENTER    #水平居中
	alignment.vert = xlwt.Alignment.VERT_CENTER    #垂直居中
	style.alignment = alignment

	w = xlwt.Workbook(encoding = 'utf-8')
	ws = w.add_sheet('scenicHangZhouInfo')
	keys = ['name', 'id', 'src', 'lng', 'lat', 'location', 'desc', 'commentCount', '用时参考', '网址', '电话', '门票', 'innerScenic', 'nearby']
	row0 = ['名称', 'id', '图片', '经度', '纬度', '位置', '介绍', '评论数量', '用时参考', '网址', '电话', '门票', '内部景区', '附近景区']
	cols = len(row0)
	for i in range(len(row0)):
		if i == cols -2:
			ws.write_merge(0, 0, i, i+1, row0[i], style)
			ws.write(1, i,'名称', style)
			ws.write(1, i+1,'id', style)
		elif i == cols -1:
			ws.write_merge(0, 0, i+1, i+5, row0[i], style)
			ws.write(1, i+1,'名称', style)
			ws.write(1, i+2,'id', style)
			ws.write(1, i+3,'经度', style)
			ws.write(1, i+4,'纬度', style)
			ws.write(1, i+5,'距离', style)
		else:
			ws.write_merge(0, 1, i, i, row0[i], style)
	current_row = 2
	count = 0
	for scenicId in scenics:
		scenic = scenics[scenicId]
		# 保留简介不为空，有图片，评论数多余10条的景点
		if scenic['desc'] != '' and scenic['src'] != nopic and scenic['commentCount'] > 10:
			count = count + 1
			height = max(len(scenic['innerScenic']), len(scenic['nearby']))
			content = [scenic[key] if key in scenic.keys() else '' for key in keys]
			if height != 0:
				for i in range(len(content)):
					if i == cols -2:
						for j in range(len(content[i])):
							ws.write(current_row + j, i, content[i][j]['name'], style)   
							ws.write(current_row + j, i+1, content[i][j]['id'], style)
					elif i == cols -1: 
						for j in range(len(content[i])):
							ws.write(current_row + j, i+1, content[i][j]['name'], style)
							ws.write(current_row + j, i+2, content[i][j]['id'], style)
							ws.write(current_row + j, i+3, content[i][j]['lng'], style)
							ws.write(current_row + j, i+4, content[i][j]['lat'], style)
							ws.write(current_row + j, i+5, content[i][j]['dist'], style)
					else:
						try:
							ws.write_merge(current_row, current_row + height - 1, i, i, content[i], style)
						except:
							print(current_row, current_row + height - 1, i, i, content[i])
				current_row = current_row + height + 1
	w.save('scenicHangZhouInfo.xls')
	print(count)


def getSingleScenic(scenicId, *args):
	f = open(filePath, 'r')
	scenics = json.loads(f.read())
	f.close()

	scenic = scenics[scenicId]

	if len(args) != 0:
		info = {}
		info['id'] = scenicId
		for key in args:
			print(key)
			info[key] = scenic[key]
		return info
	else:
		return scenic


def getScenicByKey(queryKeys, **kwargs):
	f = open(filePath, 'r')
	scenics = json.loads(f.read())
	f.close()
	flag = False

	info = {}
	for scenicId in scenics:
		for query in kwargs:
			if query not in scenics[scenicId].keys():
				flag = False
				break
			elif scenics[scenicId][query] != kwargs[query]:
				flag = False
				break
			flag = True

		if flag:
			info[scenicId] = {}
			if len(queryKeys) > 0:
				for key in queryKeys:
					if key in scenics[scenicId].keys():
						info[scenicId][key] = scenics[scenicId][key]
			else:
				info[scenicId] = scenics[scenicId]
	return info


if __name__ == '__main__':
	# queryKeys = ['src']
	# scenicInfo = getScenicByKey(queryKeys, type=3, name = '花园村')
	# print(scenicInfo)

	# print(getSingleScenic('1093').keys())
	saveAsExcel()
