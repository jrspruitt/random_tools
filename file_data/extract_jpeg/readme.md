# Extract JPEG #
## Search binary data for JPEG images. ##
June 2011

**Description**

Extract JPEG is a python script that will parse a binary file for JPEG images. I wrote it to extract the files out of a flash memory chip for a photoframe I downloaded. It should work on most JPEG images, as it searches for starting SOI (0xFF 0xD8) and ending EOI (0xFF 0xD9) byte sequences of the images, ignoring any thumbnail data or other header data that may include these tags. The file you are parsing will have to contain a properly structured JPEG image(s) for this to work.

**USAGE:**

Make sure the file has execute permissions

		$ chmod a+x extract_jpeg.py

Then run it

		$ ./extract_jpeg.py &lt;file name&gt;

Where file name is the binary file you want to sift through. You can also use the file as a python module.


		jg = Extract JPEG(&lt;file name&gt;) # create the class with a file to parse
		jg.image_parser() # start parsing the file 


Extract JPEG will output the JPEG files into the directory the script is in named jpeg_&lt;n&gt;.jpg along with a log file, jpeg_grabber.log, which will list the files that were created, and the byte addresses where they started and ended in the binary file.


**CONFIG:**

Its possible to increase the speed, if you happen to know about where the files are located. In the python script change 'self._file_position = 0' to a decimal number before the start of the JPEG data region of the file.


**UPDATE:**

revision 0.2 fixes an issue where the last 2 bytes were being left out of the image file. Also added image length to the log output.


