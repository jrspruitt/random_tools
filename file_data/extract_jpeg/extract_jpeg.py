#!/usr/bin/env python
#############################################################
# Copyright 2011 Jason Pruitt <jrspruitt@gmail.com>

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#############################################################

import os
import sys
import struct

class jpeg_grabber:
	def __init__(self, bfile):

		self._image = None

		self._soi_tag = '\xFF\xD8' 
		self._jfif_tag = 'JFIF'
		self._eoi_tag = '\xFF\xD9' 

		self._file_position = 1000000

		self._bfile_name = bfile
		self._bfile_handle = None
		self._bfile_read = ''
		self._bfile_size = 0

		self._ifile_name = 'jpeg_'
		self._ifile_name_current = None
		self._ifile_handle = None
		self._ifile_index = 0

		self._script_header = 'JPEG Grabber v0.1 \n(c)2011 Jason Pruitt\njrspruitt@gmail.com'

		self._lfile_name = 'jpeg_grabber.log'
		self._lfile_handle = None

	def set_file_position(self, fp):
		self._file_position = fp

	def get_file_position(self):
		return self._file_position

	fp = property(get_file_position, set_file_position)

	def bfile_open(self):
		try:
			self._bfile_handle = open(self._bfile_name, 'r')
			self._bfile_size = os.path.getsize(self._bfile_name)
			print 'Parsing: %s  size: %i' % (self._bfile_name, self._bfile_size)
			self._bfile_read = self._bfile_handle.read()
		except Exception, e:
			print 'Couldn\'t open binary file because: %s' % str(e)


	def bfile_close(self):
		self._bfile_handle.close()


	def ifile_open(self):
		try:
			file_name = self._ifile_name + str(self._ifile_index) + '.jpg'
			self._ifile_name_current = file_name
			self._ifile_handle = open(file_name, 'w')
			self._ifile_index += 1
		except Exception, e:
			print 'Couldn\'t create image file because: %s' % str(e)

	def ifile_close(self):
		self._ifile_handle.close()
		file_name = self._ifile_name_current
		print 'Wrote file: %s > %i kb' % (file_name, (os.path.getsize(file_name)/1024))

	def lfile_open(self):
		try:
			self._lfile_handle = open(self._lfile_name, 'w')
			self._lfile_handle.write(self._script_header)
			self._lfile_handle.write('\n*********************************************\n')
		except Exception, e:
			print 'Couldn\'t open log file because: %s ' % str(e)

	def lfile_close(self):
		self._lfile_handle.close()

	def lfile_log(self):
			log = '\n++++++++++++++++++++++++\n'
			log += 'file: %s \n' % self._ifile_name_current
			log += 'soi: 0x%x \n' % self._image[0][0]
			log += 'eoi: 0x%x \n' % self._image[0][1]
			log += 'length 0x%x \n' % (self._image[0][1] - self._image[0][0])
			self._lfile_handle.write(log)

	def image_tag_finder(self, tag):
		position = self._bfile_read.find(tag, self.fp)
		if position == -1:
			return False
		else:
			return position	
		

	def image_tag_parser(self):
		soi0 = self.find_soi_tag()
		self.fp = soi0 + 1
		self._image = [(soi0, 0)]
		last_soi = False
		last_eoi = False
		if soi0 != False:
			while 1: 

				if last_soi == False:
					soix = self.find_soi_tag()
					
					if soix == False:
						soix = self._bfile_size
						last_soi = True

				if last_eoi == False :
					eoix = self.find_eoi_tag()

					if eoix == False:
						last_eoi = True
					
				if soix < eoix:
					self._image.append((soix,eoix+2))
					self.fp = eoix+1

				elif eoix < soix: 
					self._image[0] = (soi0, eoix+2)
					return True 

		return False


	def find_soi_tag(self):
		while 1:
			marker = self.image_tag_finder(self._soi_tag)
			if marker == False:
				return False
			elif marker != False:
				self._bfile_handle.seek(marker + 6)
				if self._bfile_handle.read(4) == self._jfif_tag:
					return marker
			self.fp += 1


	def find_eoi_tag(self):
		while 1:
			marker = self.image_tag_finder(self._eoi_tag)
			if marker == False:
				return False
			if marker != False:
				return marker
			self.fp += 1
		

	def image_parser(self):
		self.bfile_open()
		self.lfile_open()

		while self.image_tag_parser():
			soi = self._image[0][0]
			eoi = self._image[0][1]
			self.ifile_open()
			self._bfile_handle.seek(soi)
			data = self._bfile_handle.read(eoi-soi)
			self._ifile_handle.write(data)
			self.ifile_close()
			self.lfile_log()
			
		self.bfile_close()
		self.lfile_close()
		print 'Finished parsing %s' % self._bfile_name
		

if __name__=="__main__":
	jg = jpeg_grabber(sys.argv[1])
	jg.image_parser()				
	sys.exit()

