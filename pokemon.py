#!/usr/bin/env python3
###############################################################################
# Pokemon GO IV Calculator Core Class
#       this class is used to compute the IV of a given pokemon given it's
#       name and various powerup data as needed. It is not without bugs,
#       and is intended to enable more advanced projects.
#
#   Copyright (C) 2016 Luke Renaud <luke@dabblee.com>
#
###############################################################################
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################

import json
from math import floor, sqrt
from copy import deepcopy

PokemonData_fn = 'BaseStatData_v0p2b.json' # Updated stats in November 2016
PokemonNames_fn = 'PokemonNames_v0p2.json'
PowerUpData_fn = 'PowerUpData_v0p2.json'
PokemonData = None
PowerUpData = None
PokemonNames = None
# Constants to avoid magic numbers
# min/max IV values
pkmn__MIN_IV = 0
pkmn__MAX_IV = 15
# constant "fudge factor" to compute CP
pkmn__CP_MULT = 0.1
# Minimum CP/HP displayed
pkmn__MIN_HP = 10
pkmn__MIN_CP = 10

# Classes used to help pass data combinations
class ivs:
	def __init__(self, a, d, s, lvl, pk):
		self.a=a		# attack
		self.d=d		# defense
		self.s=s		# stamina
		self.l = lvl	# level
		self.pk = pk	# pokemon name string
	
	# helper function used to sort results based upon percent perfect
	def __lt__(self, other):
		return self.pct < other.pct
	
	# automatically compute percentage perfect IV combination when requested
	@property
	def pct(self):
		global pkmn__MAX_IV
		return (self.a+self.d+self.s)/(3.0*pkmn__MAX_IV)

class pDat:
	def __init__(self, hp, cp, dustPrice):
		self.hp = hp
		self.cp = cp
		self.dp = dustPrice

class ivsCP:
	def __init__(self, ivs, cp):
		self.ivs = ivs
		self.cp = cp
	
	# pass the sorting function for the dependant data so we can sort
	# this class by percent perfect too.
	def __lt__(self, other):
		return self.ivs.pct < other.ivs.pct

# Describes a given pokemon, and all of the combinations of IVs that lead up to that pokemon.
# This object also should encapsulate combinations of possible IVs for non-singular solutions.
class pokemon:
	def __init__(self, name, cp, hp, dustPrice, poweredUp, trainerLevel, prevData=[]):
		pokemon.chkLoad()
		self.pkId = pokemon.getIDbyName(name.lower()) # TODO: fix the Mr. Mime name bug
		self.name = name.lower()
		
		# if you power up a pokemon, we use the results of previous searches to refine
		# the possible combinations of IVs and levels. Currently there is no way to handle
		# mixes of power-up data for power-ups before/after the base-stat changes in Nov '16.
		self.prev = prevData
		self.vc = None
		self.dat = pDat(hp,cp,dustPrice)
		self.poweredUp = poweredUp # if you never powered it up then the level will be a whole number
		self.found = False # set to true when the search eventually has a single result
		self.trainerLevel = trainerLevel # this is the maximum level of any pokemon you have
		
		# find the maximum level based upon the dust price lookup table.
		dpIndex = [ind for ind, val in enumerate(PowerUpData['stardust']) if val == self.dat.dp]
		self.levelMin = min(dpIndex)
		self.levelMax = max(dpIndex)+0.5

	###########################
	### object methods
	###########################
	# powerUp(cp,hp,dp)
	# This routine saves you from having to manage passing data around, and will directly
	# compute the new pokemon based upon old data and the new CP/HP/DP data.
	def up(self, cp, hp, dustPrice):
		self.powerUp(cp, hp, dustPrice)
	def powerUp(self, cp, hp, dustPrice):
		if (self.vc == None):
			self.computeIVs()
		
		self.prev = self.vc
		self.vc = None
		self.dat = pDat(hp,cp,dustPrice)
		self.poweredUp = True
		
		dpIndex = [ind for ind, val in enumerate(PowerUpData['stardust']) if val == self.dat.dp]
		self.levelMin = min(dpIndex)
		self.levelMax = max(dpIndex)+0.5

	# computeIVs
	# This function simply acts upon a given pokemon. We take a specific pokemon (and any input
	# data gained from previous power ups) and run the computation to find valid IV combos.
	#
	# When paired with the logic in the testLevel method, this script will test each half level
	# in the valid range, and compute CP given an exhaustive combination of the IVs. This is
	# further limited later on by using the HP to limit the valid stamina value.
	# The results are then filtered against previous valid combinations of IVs if such data
	# exists and was passed in on initalization of the pokemon.
	def c(self): # shorthand
		return self.computeIVs()
	def computeIVs(self):
		if (self.poweredUp):
			maxLevel = min(self.levelMax, self.trainerLevel)
		else:
			maxLevel = self.levelMax
		
		validCombos=[]
		lvl = self.levelMin
		while (lvl <= maxLevel):
			testedIVcombos = self.testLevel(lvl)
			if (testedIVcombos != False):
				for indv_iv in testedIVcombos:
					cp = pokemon.compCP(indv_iv)
					validCombos.append(ivsCP(indv_iv, cp))
			
			if self.poweredUp:
				lvl = lvl + 0.5;
			else:
				lvl = lvl + 1.0;
		
		# If we only have one solution, save it!
		# and compute the perfect CP and powered up CP
		if (len(validCombos) == 1):
			global pkmn__MAX_IV
			self.found = True
			self.ivs = validCombos[0].ivs
			self.cp = validCombos[0].cp
			
			# When we find it, compute the limits to CP
			# Perfect for this level
			tmpIV = ivs(pkmn__MAX_IV, pkmn__MAX_IV, pkmn__MAX_IV, self.ivs.l, self.pkId)
			self.cp_perfect = pokemon.compCP(tmpIV)
			# And this pokemon at max level
			tmpIV = deepcopy(self.ivs)
			tmpIV.l = self.trainerLevel
			self.cp_powered = pokemon.compCP(tmpIV)
		
		self.vc = validCombos
		return validCombos
	
	# testLevel(lvl)
	# compute the list of possible IVs given a particular level for this pokemon.
	def testLevel(self, lvl):
		global pkmn__MIN_IV
		global pkmn__MAX_IV
		# compute the range of HP for the current pokemon
		minHP = self.compHP(pkmn__MIN_IV, lvl, self.pkId)
		maxHP = self.compHP(pkmn__MAX_IV+1, lvl, self.pkId)
		
		if (self.dat.hp < minHP or self.dat.hp > maxHP):
			return False
		
		# Find any stamina value that would match our current HP
		possibleStaminaIV=[]
		for i in range(16): # loop from 0-15
			if ( self.compHP(i, lvl, self.pkId) == self.dat.hp ):
				possibleStaminaIV.append(i)
		
		possibleIVs=[]
		# Then generate all pairs of data that would match our CP value
		for iSta in range(len(possibleStaminaIV)):
			cSta = possibleStaminaIV[iSta]
			for cDef in range(pkmn__MAX_IV+1):
				for cAtk in range(pkmn__MAX_IV+1):
					# first compute the assumed IV
					ivSet = ivs(cAtk, cDef, cSta, lvl, self.pkId)
					cp = pokemon.compCP(ivSet)
					# and also make sure it's consistant with any old combinations
					if cp == self.dat.cp and self.checkPrevDat(ivSet):
						possibleIVs.append(ivSet)
		
		return possibleIVs		
	
	# test a given set of IV data against the historic data for this pokemon.
	def checkPrevDat(self, ivSet):
		if len(self.prev) == 0:
			return True
	
		for i in range(len(self.prev)):
			pd_wCp = self.prev[i]
			pd = pd_wCp.ivs
			# TODO: Properly handle the non-level up for evolutions
			if (pd.l + 0.5) == ivSet.l and ivSet.a == pd.a and ivSet.d == pd.d and ivSet.s == pd.s:
				return True
				
		return False
		
	# returnRange
	def getRange(self, asString = True):
		minPct = min(self.vc).ivs.pct
		maxPct = max(self.vc).ivs.pct
		
		if asString:
			if (minPct == maxPct):
				return ("%.1f%% to %.1f%%" % (100.0*minPct, 100.0*maxPct))
			else:
				return ("%.1f%%" % (100.0*maxPct))
		else:
			return [minPct, maxPct]
	
	###########################
	### class methods
	###########################
	def getIDbyName(name):
		global PokemonNames
		pokemon.chkLoad()
		try:
			pid = PokemonNames[name]
		except:
			pid = -1
			
		return pid
		
	# Given a pokemon level, return the CP multiplier.
	def getCPMult(lvl):
		global PowerUpData
		pokemon.chkLoad()
		index = int(lvl*2)
		if index > len(PowerUpData['cpm']):
			index = len(PowerUpData['cpm'][-1])
		return PowerUpData['cpm'][index]

	
	# These routines will compute a given combined stat based upon a given IV value, and level
	# for the current pokemon.
	def compSta(s, lvl, pkId):
		global PokemonData
		pokemon.chkLoad()
		return (s + PokemonData[pkId-1]['bSta'])*pokemon.getCPMult(lvl)
	def compDef(d, lvl, pkId):
		global PokemonData
		pokemon.chkLoad()
		return (d + PokemonData[pkId-1]['bDef'])*pokemon.getCPMult(lvl)
	def compAta(a, lvl, pkId):
		global PokemonData
		pokemon.chkLoad()
		return (a + PokemonData[pkId-1]['bAtk'])*pokemon.getCPMult(lvl)

	# Compute the CP for a given IV combo set.
	def compCP(ivSet):
		global pkmn__CP_MULT
		global pkmn__MIN_CP
		computedCP = pkmn__CP_MULT * \
			pokemon.compAta(ivSet.a, ivSet.l, ivSet.pk) * \
			sqrt(pokemon.compSta(ivSet.s, ivSet.l, ivSet.pk)) * \
			sqrt(pokemon.compDef(ivSet.d, ivSet.l, ivSet.pk))
		return max(pkmn__MIN_CP, int(floor(computedCP)))

	def compHP(self, sta, lvl, pkId):
		global pkmn__MIN_HP
		return max(pkmn__MIN_HP, int(floor(pokemon.compSta(sta, lvl, pkId))))

	###########################
	### Single run methods
	###########################
	def chkLoad():
		global PokemonData
		global PowerUpData
		global PokemonNames
		if PokemonData == None or PowerUpData == None or PokemonNames == None:
			pokemon.load_gameData()
	
	def load_gameData():
		global PokemonData
		global PowerUpData
		global PokemonNames
		if PokemonData == None:
			PokemonData = json.load(open(PokemonData_fn))
		if PowerUpData == None:
			PowerUpData = json.load(open(PowerUpData_fn))
		if PokemonNames == None:
			PokemonNames = json.load(open(PokemonNames_fn))
			

