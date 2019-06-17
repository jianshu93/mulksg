#!/usr/bin/python -O

############################################################################
# Copyright (c) 2015 Saint Petersburg State University
# Copyright (c) 2011-2014 Saint Petersburg Academic University
# All Rights Reserved
# See file LICENSE for details.
############################################################################


import argparse
import sys
import os
import matplotlib.patches
import matplotlib.pyplot
import matplotlib.lines
import math

DELTA = 1200
ENOUGH_FOR_SIMILARITY = 0
MIN_CONTIG = 2000.0



def similarThreshold(total):
	return total  / 2 + total % 2 


class Visualizer:
	def __init__(self, assemblies, covHist):
		self.assemblies = assemblies[0]
		self.covHist = covHist[0]

		self.assemblyWidth = 800.0
		self.scale = self.assemblyWidth / assemblies[1] 
		self.plotXScale = self.assemblyWidth / (covHist[1] + 1)
		self.lastMargin = 20.0

		self.plotHeight = 80.0
		self.plotMargin = 20.0
		self.dotLength = self.plotXScale
		
		self.maxCov = math.floor(math.log10(covHist[2]))
		self.plotYScale = self.plotHeight / self.maxCov

		self.xTics = 1000000
		self.yTics = 2.0
		self.genomeLength = assemblies[1]
		self.genomeAnnotationScale = 1000000.0

		self.dashLines = True
		self.dashLineWeight = 0.2
		self.ticLength = 6
		self.axisWeight = 0.5

		self.assemblyStep = 70
		self.similarStep = 7
		self.oddStep = 4
		self.contigHeight = 30
		self.xOffset = 85.0

		self.nameAnnotationXStep = 15
		self.nameAnnotationYStep = 15
		self.xticsStep = 3
		self.yticsStep = self.ticLength + 3
		self.xLabelStep = self.xticsStep + 13
		self.yLabelStep = self.yticsStep + 60

		self.totalHeight = self.plotHeight + self.plotMargin + len(self.assemblies.keys()) * self.assemblyStep + self.lastMargin
		self.totalWidth = self.xOffset + self.assemblyWidth

		self.similarOdd = 0
		self.differentOdd = 0

		self.figure = matplotlib.pyplot.figure()
		self.subplot = self.figure.add_subplot(111)

	def __del__(self):
		pass

	def show(self):
		self.subplot.axis("equal")
		self.subplot.axis("off")
		matplotlib.pyplot.show()

	def save(self, fileName):
		self.subplot.axis("equal")
		self.subplot.axis("off")
		self.figure.savefig(fileName + ".svg", format='svg')


	def plot_coverage(self, covHist, offset):
		self.subplot.add_line(matplotlib.lines.Line2D((offset[0], offset[0] + self.assemblyWidth), (offset[1], offset[1]), c="black", lw=self.axisWeight))
		self.subplot.add_line(matplotlib.lines.Line2D((offset[0], offset[0]), (offset[1], offset[1] + self.plotHeight), c="black", lw=self.axisWeight))

		for i in range(0, self.genomeLength, self.xTics):
			x = offset[0] + self.assemblyWidth * float(i) / float(self.genomeLength)
			if self.dashLines:
				self.subplot.add_line(matplotlib.lines.Line2D((x, x), (offset[1] + self.plotHeight , self.lastMargin), c="grey", ls=':', lw=self.dashLineWeight))
			self.subplot.add_line(matplotlib.lines.Line2D((x, x), (offset[1], offset[1] - self.ticLength), c="black", lw=self.axisWeight))

			self.subplot.annotate(str(round(float(i) / self.genomeAnnotationScale ,1)), (x + self.xticsStep, offset[1] - self.xticsStep), fontsize=6, horizontalalignment='left', verticalalignment='top')
		
		x = offset[0] + self.assemblyWidth	
		if self.dashLines:
			self.subplot.add_line(matplotlib.lines.Line2D((x, x), (offset[1] + self.plotHeight , self.lastMargin), c="grey", ls=':', lw=self.dashLineWeight))
		self.subplot.add_line(matplotlib.lines.Line2D((x, x), (offset[1], offset[1] - self.ticLength), c="black", lw=self.axisWeight))

		self.subplot.annotate(str(round(float(self.genomeLength) / self.genomeAnnotationScale ,2)), (x + self.xticsStep, offset[1] - self.xticsStep), fontsize=6, horizontalalignment='left', verticalalignment='top')

		self.subplot.annotate("Genome, Mbp", (offset[0] + self.assemblyWidth / 2.0, offset[1] - self.xLabelStep), fontsize=8, horizontalalignment='center', verticalalignment='top')


		cov = 0.0
		while (cov <= self.maxCov):
			y = offset[1] + cov * self.plotYScale
			self.subplot.add_line(matplotlib.lines.Line2D((offset[0] - self.ticLength, offset[0]), (y, y), c="black", lw=self.axisWeight))
			self.subplot.annotate(str(int(round(math.pow(10,cov)))), (offset[0] - self.yticsStep, y), fontsize=6, horizontalalignment='right', verticalalignment='center')
			cov += self.yTics

		self.subplot.annotate("Coverage", (offset[0] - self.yLabelStep, offset[1] + self.plotYScale * self.maxCov / 2.0), fontsize=8, horizontalalignment='center', verticalalignment='center', rotation = "vertical")

		for pos in covHist:
			x = offset[0] + pos * self.plotXScale
			y = offset[1] + -0.2 * self.plotYScale
			color = "blue"
			if covHist[pos] != 0:
				color = "red"
				y = offset[1] + math.log10(covHist[pos]) * self.plotYScale
		        self.subplot.add_line(matplotlib.lines.Line2D((x, x + self.dotLength), (y, y), c=color, lw=0.7))


	def plot_assembly(self, assembly, offset):
		for coord in assembly:

			width = coord[1] - coord[0]

			x = offset[0] + coord[0] * self.scale
			y = offset[1] 

			fillColor = ""		
			if coord[2] == 0:
				y += self.similarStep
				if self.differentOdd == 0:
					fillColor = "#e41a1c"
					y += self.oddStep
				else:
					fillColor = "#ff7f00"
										
				self.differentOdd = (self.differentOdd + 1) % 2

			else:
				if self.similarOdd == 0:
					y -= self.oddStep
										
				self.similarOdd = (self.similarOdd + 1) % 2

				if  coord[2] == 1:
					fillColor = "#377eb8"
				else:
					fillColor = "#4daf4a"

				
			width *=  self.scale
			self.subplot.add_patch(matplotlib.patches.Rectangle((x,y), width, self.contigHeight,  ec="black", color=fillColor, fill=True, lw=0.05))

	def visualize(self):
		self.subplot.add_patch(matplotlib.patches.Rectangle((0,0), self.totalWidth + self.lastMargin, self.totalHeight, color="white", fill=True, lw=0))

		self.plot_coverage(self.covHist, (self.xOffset, self.totalHeight - self.plotHeight) )
		
		offset = self.plotHeight + self.plotMargin + self.assemblyStep
		names = self.assemblies.keys()
		names.sort()
		print (names)
		for name in names:
			self.similarOdd = 0
			self.differentOdd = 0
			self.subplot.annotate(name, (self.xOffset - self.nameAnnotationXStep, self.totalHeight - offset + self.nameAnnotationYStep), fontsize=12, horizontalalignment='right', verticalalignment='bottom')
			self.plot_assembly(self.assemblies[name], (self.xOffset, self.totalHeight - offset))
			offset += self.assemblyStep




def readAssemblies(fileName):
	inFile = open(fileName, 'r')

	assemblies = {}
	maxPos = 0

	for line in inFile:
		fName, ext = os.path.splitext(line)
	
		assFile = open(line.strip())
		assemblies[fName] = []

		for coord in assFile:
			pos = coord.strip().split(' ')
			assemblies[fName].append((int(pos[0]),int(pos[1]),0))

			if maxPos < int(pos[1]):
				maxPos = int(pos[1])

		assFile.close()
	
	inFile.close()
	return assemblies, maxPos



def findSimilar(assemblies):
	global COORD_DELTA
	global ENOUGH_FOR_SIMILARITY

	contigs = {}
	total = 0
	
	color = 0
	for name in assemblies:
		total += 1
		for coord in assemblies[name]:
			width = coord[1] - coord[0]
			found = False
			if (width >= MIN_CONTIG):
				for i in range(-DELTA, DELTA + 1):
					start = coord[0] + i
					if start in contigs:
						for i in range(0, len(contigs[start])):
							end = contigs[start][i][0]
							count = contigs[start][i][1]
							curColor = contigs[start][i][2]
							if end >= coord[1] - DELTA and end <= coord[1] + DELTA:
								contigs[start][i] = (end, count + 1, curColor)
								found = True
								break
						if found:
							break

			if not found:
				if coord[0] in contigs:
					contigs[coord[0]].append((coord[1], 1, color))
				else:
					contigs[coord[0]] = [(coord[1], 1, color)]
				color = (color + 1) % 2

	for name in assemblies:
		for k in range(0, len(assemblies[name])):
			coord = assemblies[name][k]
			found = False
			for i in range(-DELTA, DELTA + 1):
				start = coord[0] + i
				if start in contigs:
					for i in range(0, len(contigs[start])):
						end = contigs[start][i][0]
						count = contigs[start][i][1]
						curColor = contigs[start][i][2]
						if end >= coord[1] - DELTA and end <= coord[1] + DELTA:
							found = True
							if (count >= similarThreshold(total)):
								assemblies[name][k] = (coord[0], coord[1], curColor + 1)
								break
					if found:
						break


			if not found:
				print("Contig not found")

def readCoverage(fileName):
	inFile = open(fileName, 'r')

	hist = {}
	maxPos = 0
	maxCov = 0

	for line in inFile:
		pos = line.strip().split(' ')
		hist[int(pos[0])] = int(pos[1])
		if maxPos < int(pos[0]):
			maxPos = int(pos[0])
		if maxCov < int(pos[1]):
			maxCov = int(pos[1])

	inFile.close()
	return hist, maxPos, maxCov



if len(sys.argv) != 3:
	print("Usage: " + sys.argv[0] + " <files with assemblies files> <file with coverage histogram>")	
	sys.exit()

inFileName = sys.argv[1]
covFileName = sys.argv[2]

assemblies = readAssemblies(inFileName)
findSimilar(assemblies[0])
covHist = readCoverage(covFileName)

v = Visualizer(assemblies, covHist)
v.visualize()
#v.show()
outFileName, ext = os.path.splitext(inFileName)
v.save(outFileName)




		




