#!/usr/bin/env python3
# This script depends upon pyoo in python3, available through pip
# 	> pip3 install pyoo
# First launch LibreOffice as a slave
# 	> soffice --accept="socket,host=localhost,port=2002;urp;" --norestore --nodefault > /dev/null 2>&1 &

sourceFilePathName = u"/home/luke/Dropbox/Projects/PkmnGoIVComp/NewSheet.ods"

import pyoo
from math import floor, sqrt
import re

from pokemon import pokemon
desktop = pyoo.Desktop('localhost', 2002)
doc=desktop.open_spreadsheet(sourceFilePathName)

myPk=doc.sheets[0];
gameDatSht=doc.sheets[1];
datBaseStats={};
datCPMult={};
datStardustLvl={};
myTrainerLvl=25;
myPokemonUIDs={};

if True:
	cUID	= 0
	cPk		= 1/home/luke/Dropbox/Projects/PkmnGoIVComp
	cCP		= 2
	cHP		= 3
	cDst	= 4
	cPwr	= 5
	cLVL	= 6
	cATK	= 7
	cDEF	= 8
	cSTA	= 9
	cPct	= 10
	cCPperf	= 11
	cCPpwr	= 12
	cCPmax	= 14

ivDatColor=0xCFE2F3
baseDataBGColor=0xFFF2CC

uidReg = re.compile("^([^ ]+) ([0-9]+)$")

###################################################################
def computeRow(row):
	global myPk, myTrainerLvl
	myPk[row,cPk:(cPwr+1)].background_color	= baseDataBGColor
	
	try:
		species = str(myPk[row,cPk].value)
		hp = int(myPk[row,cHP].value)
		cp = int(myPk[row,cCP].value)
		dust = int(myPk[row,cDst].value)
		poweredCell = str(myPk[row,cPwr].value)
		if (poweredCell == 'true' or 
			poweredCell == 'True' or 
			poweredCell == 'TRUE' or 
			poweredCell == 'yes' or 
			poweredCell == 'YES' or 
			poweredCell == 'Yes' or 
			poweredCell == '1' or 
			poweredCell == '1.0'):
			poweredUp=True
		else:
			poweredUp=False


		pk = pokemon(species, cp, hp, dust, poweredUp, myTrainerLvl)
		ivSet = pk.computeIVs()
		if (len(ivSet) == 0):
			return False

		pctColor = colorGradient(min(ivSet).ivs.pct)
		pctStr = pk.getRange(True)
		comboStr = ("%d possible" % len(ivSet))

		if (len(ivSet) == 1):
			iv=ivSet[0].ivs
			fillDatCells(row, iv.l, iv.a, iv.d, iv.s, pctStr, pctColor)
		elif (len(ivSet) > 1):
			fillDatCells(row, '', comboStr, '', '', pctStr, pctColor)

		return ivSet

	except:
		return False

if False:
	def computeDependants(row):
		v_list=[]
		rowList=[]
		global myPk
		global myPokemonUIDs
	
		# Find all valid rows
		rowUID_src = str(myPk[row,cUID].value);
		if (rowUID_src != ''):
			rowUID_match = re.match(uidReg, str(rowUID_src))
			if (rowUID_match != None):
				rowUID_name = rowUID_match.group(1)
			else:
				rowUID_name = rowUID_src
			rowList=myPokemonUIDs[rowUID_name]

		if (len(rowList) == 0):
			return False
	
		# And compute them all in order.
		v_prev=computeReturnDat_t(None,None,None)
		for r in range(len(rowList)):
			v_prev=computeRow(rowList[r], v_prev.l);
			if (v_prev == False):
				break
			v_list.append(v_prev)
	
		return v_list

def colorGradient(x):
	aR = 230
	aG = 124
	aB = 115
	bR = 255
	bG = 255
	bB = 255
	cR = 87
	cG = 187
	cB = 138
	if (x < 0.5):
		color = round(aR * ( 0.5 - x ) / 0.5 + bR * x / 0.5)
		color = round(aG * ( 0.5 - x ) / 0.5 + bG * x / 0.5) + (0x100 * color);
		color = round(aB * ( 0.5 - x ) / 0.5 + bB * x / 0.5) + (0x100 * color);
	else:
		x-=0.5
		color = round(bR * ( 0.5 - x ) / 0.5 + cR * x / 0.5)
		color = round(bG * ( 0.5 - x ) / 0.5 + cG * x / 0.5) + (0x100 * color);
		color = round(bB * ( 0.5 - x ) / 0.5 + cB * x / 0.5) + (0x100 * color);
		
	return color

def fillDatCells(r, l='', a='', d='', s='', pct='', color=None):
	# Add color formating
	myPk[r,cLVL].value = l
	myPk[r,cATK].value = a
	myPk[r,cDEF].value = d
	myPk[r,cSTA].value = s
	myPk[r,cPct].value = pct
	myPk[r,cPct].background_color=color
	if (type(a)==str or type(d)==str or type(s)==str):
		myPk[r,cLVL:(cSTA+1)].background_color = ivDatColor
	else:
		myPk[r,cLVL].background_color = ivDatColor
		myPk[r,cATK].background_color = colorGradient(a/15)
		myPk[r,cDEF].background_color = colorGradient(d/15)
		myPk[r,cSTA].background_color = colorGradient(s/15)

def fillPushCells(r, p=None, l='', a='', d='', s=''):
	myPk[r,cCPperf:(cCPmax+1)].background_color = 0xEEEEEE
	if (p==None):
		perfectCP = ''
		poweredCP = ''
		maxCP = ''
	else:
		perfectCP = p.getCP(15,15,15)
		p.level=myTrainerLvl
		poweredCP = p.getCP(a,d,s)
		maxCP = ''
	
	myPk[r,cCPperf].value = perfectCP
	myPk[r,cCPpwr].value = poweredCP
	myPk[r,cCPmax].value = maxCP;

def computeAndFill(startRow, endRow, debug=False):
	rows = [r for r in range(startRow, endRow+1)]
	solved = []
	for r in rows:
		if (debug):
			print("Computing row %3d of %3d" % (1+r-startRow, 1+endRow-startRow))
		if (r in solved):
			#print("Skipping %d" % r)
			continue
		
		ivs=computeRow(r)


def GO(stopRow, verbose=True):
	computeAndFill(1,stopRow,verbose)

def GOALL(verbose=True):
	GO(1002, verbose)
	
	
####################################################

print("Loading Data...")
#loadBaseStats()
#loadCPMultipliers()
#loadStardustLevels()
#loadPokemonUIDs()
#myTrainerLvl=myPk[1,0].value
#computeAndFill(2,256)
print("To use, type GO(###) to compute all rows from the start to ####.")
print("type GOALL() to compute out to 1000.")
print("For specific ranges use computeAndFill(<start>,<stop>)")
print("    note that the \"first\" row is 1.")
print("")

