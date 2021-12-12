########################
# This file is part of BehBOT.
#
# BehBOT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BehBOT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BehBOT. If not, see <https://www.gnu.org/licenses/>.
########################
import json
import requests

class VideoSearchResult:
	def __init__(self, title = "", src = ""):
		self.title = title
		self.videoSource = "https://www.youtube.com/watch?v={0}".format(src)
		
	title = ""
	videoSource = ""
	
# simple parser to extract the search result json
# string
def __getSearchResultJson(search_stream):
	data = ""
	lines = search_stream.readlines()
	for line in lines:
		data += line.decode("utf-8")
	
	start_index = data.find("{\"responseContext\"")
	if start_index == -1:
		start_index = data.find("{ \"responseContext\"")
		if start_index == -1:
			return ""
	
	# do simple backet matching
	open_braces = 1
	end_index = 0
	for i in range(start_index + 1, len(data)):
		if data[i] == '{':
			open_braces += 1
		elif data[i] == '}':
			if open_braces > 0:
				open_braces -= 1
			else:
				return ""
		
		if open_braces == 0:
			if i == len(data):
				return ""
			else:
				end_index = i + 1
			break
			
	new_data = data[start_index:end_index]
	return new_data

def getYoutubeSearchResults(search_value):
	ret = []
	
	# To get youtube search results, first we visit the page
	# https://www.youtube.com/results?search_query={search_value}, where we replace {search_value} to the string we want
	# to search for. Then we load the website, and search for a json string that is the POST response. This can be done simply
	# by searching for the string {"responseContext":. This json value contains the: the video title, and the video
	# url that we need
	search_url = "https://www.youtube.com/results?search_query={0}".format(search_value.replace(' ', '+'))
	with requests.get(search_url, stream=True) as r:
		json_string = __getSearchResultJson(r.raw)
		if len(json_string) == 0:
			return ret
			
		json_o = json.loads(json_string)
		
		try:			
			data_contents_o = json_o["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]
			if len(data_contents_o) == 0:
				return ret
								
			for i in range(0, len(data_contents_o)):
				if "itemSectionRenderer" not in data_contents_o[i]:
					continue
				
				contents_o = data_contents_o[i]["itemSectionRenderer"]["contents"]
				for video_o in contents_o:
					if "videoRenderer" not in video_o:
						continue
						
					ret.append(VideoSearchResult(video_o["videoRenderer"]["title"]["runs"][0]["text"], video_o["videoRenderer"]["videoId"]))
		except:
			return ret
						
	return ret
