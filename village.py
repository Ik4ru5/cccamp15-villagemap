#!/usr/env/python
# coding: utf-8

from PIL import Image, ImageDraw, ImageFont
import urllib
import math
import csv

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False
		
def is_int(s):
	try:
		int(s)
		return True
	except ValueError:
		return False
		
def getRadius(area):
	return math.sqrt(area / math.pi)


villages = "http://events.ccc.de/camp/2015/wiki/index.php?title=Special%3AAsk&q=%5B%5BHas+x-coordinate%3A%3A%210%5D%5D+OR+%5B%5BHas+y-coordinate%3A%3A%210%5D%5D&po=%3FHas+x-coordinate%0D%0A%3FHas+y-coordinate%0D%0A%3FSize+needed+min%0D%0A%3FSize+needed+max%0D%0A&eq=yes&p%5Bformat%5D=csv&sort%5B0%5D=Has+x-coordinate&order%5B0%5D=ASC&sort_num=&order_num=ASC&p%5Blimit%5D=100&p%5Boffset%5D=&p%5Blink%5D=all&p%5Bsort%5D=Has+x-coordinate&p%5Border%5D%5Basc%5D=1&p%5Bheaders%5D=show&p%5Bmainlabel%5D=&p%5Bintro%5D=&p%5Boutro%5D=&p%5Bsearchlabel%5D=%E2%80%A6+further+results&p%5Bdefault%5D=&p%5Bsep%5D=%2C&p%5Bfilename%5D=result.csv&eq=yes"
radius = 1
meterX = 893 # the width in meters of the backgroundimage
meterY = 612 # the height in meters of the backgroundimage
font = ImageFont.truetype("/Library/Fonts/Arial.ttf",12) # path to a font you fancy

url = urllib.urlopen(villages)
data = url.read()

mapOnlyVillages = Image.open("map.png") # http://events.ccc.de/camp/2015/wiki/extensions/EventMap/map.png
mapWithSizes = Image.open("map.png") # http://events.ccc.de/camp/2015/wiki/extensions/EventMap/map.png
drawOnlyVillages = ImageDraw.Draw(mapOnlyVillages, "RGBA")
drawWithSizes = ImageDraw.Draw(mapWithSizes, "RGBA")

width, height = mapOnlyVillages.size
pixelPerMeterX = width / 893.0
pixelPerMeterY = height / 612.0

print pixelPerMeterX, pixelPerMeterY

for line in data.splitlines():
	minRadius = 0
	maxRadius = 0
	values = line.split(",")
	if is_number(values[1]) and is_number(values[2]):
		villageName = values[0]
		villageName = villageName.strip('"') # strip unnecessary stuff
		villageName = villageName.strip("Village:") # strip unnecessary
		villageX = float(values[1])
		villageY = float(values[2])
		
		#correct for mapOnlyVillages being from 100,100 to 200,200
		xPos = (villageX - 100) * (width / 100.0)
		yPos = (villageY - 100) * (height / 100.0)
		
		#skip invalid locations
		if villageX < 100 or villageY < 100 or villageX > 200 or villageY > 200:
			continue
		
		# if size ist above 1000 the data conatins 1,000 and since splitting by "," need to merge the data back together
		if len(values) > 5:
			counter = 0
			for value in values:
				if value.startswith('"') and values[counter + 1].endswith('"') and counter > 2:
					values[counter] = "%s%s" % (values[counter].strip('"'), values[counter + 1].strip('"'))
				counter = counter + 1
			
			values[4] = values[5]

		# valid sizes
		if is_int(values[3]) and is_int(values[4]):
			villageMinSize = int(values[3])
			villageMaxSize = int(values[4])
		
			if villageMaxSize < villageMinSize:
				tmp = villageMinSize
				villageMinSize = villageMaxSize
				villageMaxSize = tmp
			
			minRadius = getRadius(villageMinSize)
			maxRadius = getRadius(villageMaxSize)
			
			# draw max area	
			drawWithSizes.ellipse(((xPos - (maxRadius * pixelPerMeterX)), (yPos - (maxRadius * pixelPerMeterY)), (xPos + (maxRadius * pixelPerMeterX)), (yPos + (maxRadius * pixelPerMeterY))), fill=(255, 0, 0, 128))
			# draw min area
			drawWithSizes.ellipse(((xPos - (minRadius * pixelPerMeterX)), (yPos - (minRadius * pixelPerMeterY)), (xPos + (minRadius * pixelPerMeterX)), (yPos + (minRadius * pixelPerMeterY))), fill=(0, 255, 0, 128))
		

			
	
		drawOnlyVillages.ellipse(((xPos - radius), (yPos - radius), (xPos + radius), (yPos + radius)), fill=(0, 0, 0))
		drawWithSizes.ellipse(((xPos - radius), (yPos - radius), (xPos + radius), (yPos + radius)), fill=(0, 0, 0))
		
		#draw text
		textWidth, textHeight = font.getsize(villageName)
		drawWithSizes.text(((xPos - (textWidth / 2)), (yPos - 20)), villageName.decode("utf8"), (0,0,0), font=font)
		drawOnlyVillages.text(((xPos - (textWidth / 2)), (yPos - 20)), villageName.decode("utf8"), (0,0,0), font=font)

del drawOnlyVillages

# Save data
mapOnlyVillages.save("villages.png", "PNG")
mapWithSizes.save("villages_size.png", "PNG")
