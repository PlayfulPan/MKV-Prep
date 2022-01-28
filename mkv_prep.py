import os
import sys
import subprocess
import json

class mkvFile:

	def __init__(self, fileName):
		self.fileName = fileName
		load_file = subprocess.run(['mkvmerge', '-J', self.fileName], capture_output=True, text=True)
		data = json.loads(load_file.stdout)

		self.tracks = []

		for temp_Track in data['tracks']:
			temp = self.track(temp_Track)
			self.tracks.append(temp)

		self.vTracks = []
		self.aTracks = []
		self.sTracks = []

		for i in self.tracks:
			t_type = i.trackType
			if t_type == 'video':
				self.vTracks.append(i)
			if t_type == 'audio':
				self.aTracks.append(i)
			if t_type == 'subtitles':
				self.sTracks.append(i)
	
	def processFile(self, outputName, folderName):
		tagCommandArray = ['mkvpropedit', self.fileName]
		mergeCommandArray = ['mkvmerge', '-o', folderName+'/'+outputName]
		
		keepVTracks = []
		keepATracks = []
		keepSTracks = []

		tags = ['--delete', 'title']

		for t in self.tracks:
			t.printTrackInfo()
			tlang = t.lang
			tdefault = '1'
			tforced = '0'
			keeptrack = False
			tagcmd = ['--edit', 'track:'+str(t.trackId+1), '--delete', 'name']

			print('--------------------------------')
			trackCmd = input('Enter actions for above track: ')
			print()
			trackCmd = list(trackCmd.lower())
		
			if 'x' in trackCmd:
				print('Skipping this track.')
			elif 'k' in trackCmd:
				keeptrack = True

				if 'l' in trackCmd:
					tlang = input("Enter track language: ")
					print()

				if 'f' in trackCmd:
					tforced = '1'
					tdefault = '0'

				if 'd' in trackCmd:
					tdefault = '0'
				
			if keeptrack:
				if t.trackType == 'video':
					keepVTracks.append(t.trackId)
				if t.trackType == 'audio':
					keepATracks.append(t.trackId)
				if t.trackType == 'subtitles':
					keepSTracks.append(t.trackId)

				tlang = tlang.lower()
				
				if tlang in ['en', 'eng']:
					tlang = 'en'
				if tlang in ['ja', 'jpn']:
					tlang = 'ja'
			
				tagcmd = tagcmd+['--set', 'language='+tlang]

				tagcmd = tagcmd+['--set', 'flag-default='+tdefault]
				tagcmd = tagcmd+['--set', 'flag-forced='+tforced]

				tags = tags+tagcmd

		subprocess.run(tagCommandArray+tags)

		vTrackList = str(keepVTracks[0])
		aTrackList = str(keepATracks[0])
		

		for i in keepVTracks[1:]:
			vTrackList = vTrackList+','+str(i)
		for i in keepATracks[1:]:
			aTrackList = aTrackList+','+str(i)
		
		mergeCommandArray = mergeCommandArray + ['--video-tracks', vTrackList, '--audio-tracks', aTrackList]

		if keepSTracks == []:
			mergeCommandArray = mergeCommandArray+['--no-subtitles']
		else:
			sTrackList = str(keepSTracks[0])
			for i in keepSTracks[1:]:
				sTrackList = sTrackList+','+str(i)

			mergeCommandArray = mergeCommandArray+['--subtitle-tracks', sTrackList]
		
		mergeCommandArray.append(self.fileName)

		subprocess.run(mergeCommandArray)

	class track:
		def __init__(self, track_data):
			
			self.trackType = track_data['type']
			self.trackId = track_data['id']
			self.codec = track_data['codec']

			self.lang = 'und'
			self.default = False
			self.enabled = False
			self.forced = False
			self.name = ''

			track_props = track_data['properties']
			if 'language' in track_props:
				self.lang = track_props['language']

			if 'default_track' in track_props:
				self.default = track_props['default_track']

			if 'forced_track' in track_props:
				self.forced = track_props['forced_track']

			if 'enabled_track' in track_props:
				self.enabled = track_props['enabled_track']

			if 'track_name' in track_props:
				self.name = track_props['track_name']

		def printTrackInfo(self):
			print('================================')
			print('Track ID: '+str(self.trackId))
			print('Type: '+self.trackType)
			print('Codec: '+self.codec)
			print('Track Name: '+self.name)
			print('Language: '+self.lang)
			print('Enabled Track: '+str(self.enabled))
			print('Default Track: '+str(self.default))
			print('Forced Track: '+str(self.forced))






inputPrefix = 'Monogatari - s02e'
inputSuffix = '.mkv'

outputPrefix = "Monogatari - s02e"
outputSuffix = '.mkv'

folderName = 'Season 02'

for i in range(1, 16):
	inputName = inputPrefix+f'{i:02}'+inputSuffix
	outputName = outputPrefix+f'{i:02}'+outputSuffix

	vidFile = mkvFile(inputName)
	vidFile.processFile(outputName, folderName)