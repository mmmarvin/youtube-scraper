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
from urllib.parse import unquote, urlparse

import string_utils
import youtube_decipher

class VideoMetaDataException(Exception):
	pass
	
class VideoInformation:
	def __init__(self, title = "", src = "", osrc = ""):
		self.title = title
		self.videoSource = src
		self.originalVideoSource = osrc
		
	title = ""
	videoSource = ""
	originalVideoSource=""

def __separateResponseToLines(response_stream):
	data = []
	lines = response_stream.readlines()
	
	# TODO: Refactor this
	for line in lines:
		line = unquote(line)
		
		new_line = ""
		for i in range(0, len(line)):
			if line[i] == '&':
				data.append(new_line)
				new_line = ""
			else:
				new_line += line[i]
				
		if len(new_line) > 0:
			data.append(new_line)
		
	return data

def __categorizeResponse(response_stream):
	ret = {}
	lines = __separateResponseToLines(response_stream)
	for line in lines:
		(key, value) = string_utils.tokenizeKeyValue(line, '=')
		ret[key] = value
		
	return ret
	
def __getVideoURLFromJson(json_object):
	if "streamingData" not in json_object:
		raise VideoMetaDataException()
		
	streaming_data = json_object["streamingData"]
	
	if "formats" not in streaming_data:
		raise VideoMetaDataException()
				
	streaming_formats = streaming_data["formats"]
	
	if len(streaming_formats) == 0:
		raise VideoMetaDataException()
	
	if "url" not in streaming_formats[0]:
		# if "url" is not on streaming_formats[0], it is because the
		# video is protected, so we must decipher the video url
		data = streaming_formats[0]["signatureCipher"]
		
		# TODO: Refactor this
		# separate the data to lines
		data_lines = data.split('&')
						
		# categorize the lines
		data_category = {}
		for line in data_lines:
			(key, value) = string_utils.tokenizeKeyValue(unquote(line), '=')
			data_category[key] = value
		
		# Call the decipher
		return youtube_decipher.Gz(data_category)
			
	return streaming_formats[0]["url"]
	
def __getVideoNameFromJson(json_object):
	if "videoDetails" not in json_object:
		raise VideoMetaDataException()
		
	video_detail = json_object["videoDetails"]
	
	if "title" not in video_detail:
		raise VideoMetaDataException()
		
	return video_detail["title"]
	
def __removePHPVariables(url):
	end_index = url.find('&')
	if end_index == -1:
		return url
		
	return url[0:end_index]
	
def __removeLeadingSlash(url):
	if len(url) > 0 and url[0] == '/':
		url = url[1:len(url)]
	
	return url
		
def getYoutubeVideoInformation(video_id):
	# YouTube video information scrapper based on
	# https://tyrrrz.me/blog/reverse-engineering-youtube/
	info_url = "https://www.youtube.com/get_video_info?video_id={0}".format(video_id)
	with requests.get(info_url, stream=True) as r:		
		# categorize the response
		response_category = __categorizeResponse(r.raw)
		if not "player_response" in response_category:
			raise VideoMetaDataException()
			
		# load the player response json value
		json_o = json.loads(response_category["player_response"])
		if json_o == None:
			raise VideoMetaDataException()
			
		# get video URL from json value
		title = __getVideoNameFromJson(json_o)
		url = __getVideoURLFromJson(json_o)
		return VideoInformation(title.replace('+', ' '), url)
		
	return None
	
def getYoutubeVideoID(url):
	# Youtube URLs can appear in 4 different formats:
	# * https://www.youtube.com -> default
	# * https://m.youtube.com -> mobile website
	# * https://www.youtube.com/embed/ -> embeded video
	# * https://youtu.be/* -> shortended video url
	# Account for all possibilities
	
	# TODO: Use regular expressions to simplify?
	url_components = urlparse(url)
	if url_components.netloc == "www.youtube.com" or url_components.netloc == "m.youtube.com":
		if len(url_components.path) > 0:
			url_id = __removeLeadingSlash(url_components.path)
			if url_id[:len("embed/")] == "embed/":
				# for embeded format: *.youtube.com/embed/*
				video_id = url_id[len("embed/"):len(url_id)]
				video_id = __removePHPVariables(video_id)
				return video_id
			else:			
				# for base format: *.youtube.com/watch?v=*"
				index = url.find("watch?v=")
				if index != -1:
					index = index + len("watch?v=")
					video_id = url[index: len(url)]
					return __removePHPVariables(video_id)
	elif url_components.netloc == "youtu.be" and len(url_components.path) > 0:
		# for shortened format: youtu.be/*
		video_id = __removeLeadingSlash(url_components.path)
		return __removePHPVariables(video_id)
		
	return ""
