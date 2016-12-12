#!/usr/bin/env python3
# A simple example of using the Pokemon IV computer class
###############################################################################
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

from pokemon import pokemon

# first make a pokemon with the stats from the game
#			Name,        CP, HP, Dust, Powered?,  TrainerLevel
pk = pokemon('Pidgeotto', 14, 13,  200, False,     23)
# next compute the combinations
ivSet = pk.computeIVs()
# we can pull a specific example from this array and examine it if we want
minIVPct=min(ivSet)
iv=minIVPct.ivs
print('#%d %s worst case percentage is %.2f%%' % (iv.pk, pk.name, 100*iv.pct))
print('   implies IVs: Atk %2d,  Def %2d,  Sta %2d' % (iv.a, iv.d, iv.s))
print('   Percent range is %s in %d possible results\n' % (pk.getRange(asString=True), len(ivSet)))

# now we can start powering up, inputing new stats and getting results.
#    cp, hp, dust
pk.up(29, 19, 200)
ivSet=pk.c() # c is a shorthand alias for computeIVs()
minIVPct=min(ivSet)
iv=minIVPct.ivs

print('#%d %s worst case percentage is %.2f%%' % (iv.pk, pk.name, 100*iv.pct))
print('   implies IVs: Atk %2d,  Def %2d,  Sta %2d' % (iv.a, iv.d, iv.s))
print('   Percent range is %s in %d possible results\n' % (pk.getRange(asString=True), len(ivSet)))

# And do that a few more times.
pk.up(44, 23, 200) # power up data 1
pk.c() # this will automatically be called on power-up if we fail to do so manually
# this allows you to modify internal results before a powerup if needed, but will automatically
# commit old power-ups if you go on to add a second one without computing the first.
pk.up(59, 27, 200) # power up 2
pk.up(74, 30, 400)
pk.up(89, 33, 400)
pk.up(104, 36, 400)
pk.up(119, 38, 400)
pk.up(134, 40, 600)
pk.up(149, 43, 600)
pk.up(164, 45, 600)
pk.up(179, 47, 600)
pk.up(195, 49, 800) # power up data 11
pk.up(210, 51, 800)
# at this point we have computed the power up for #11, and have loaded (but
# not computed) IVs including the data in #12

ivSet=pk.c() # only two results at this point (I checked)

tstIVPct=min(ivSet)
iv=tstIVPct.ivs
print('#%d %s worst case percentage is %.2f%%' % (iv.pk, pk.name, 100*iv.pct))
print('   implies IVs: Atk %2d,  Def %2d,  Sta %2d' % (iv.a, iv.d, iv.s))
tstIVPct=max(ivSet)
iv=tstIVPct.ivs
print('#%d %s best case percentage is %.2f%%' % (iv.pk, pk.name, 100*iv.pct))
print('   implies IVs: Atk %2d,  Def %2d,  Sta %2d' % (iv.a, iv.d, iv.s))

# Enjoy
#  -Luke
