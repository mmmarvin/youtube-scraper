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
from urllib.parse import quote, unquote

import string_utils

# reversed-engineered from the decipher function on youtube's html5 video player at
# https://www.youtube.com/s/player/38c5f870/player_ias.vflset/en_US/base.js
# works as of March 2021
def __Uu_Zo(a, b):
	# var c = a[0];
	# a[0] = a[b % a.length];
	# a[b % a.length] = c
	r = a
	
	c = a[0]
	r[0] = a[b % len(a)]
	r[b % len(a)] = c
	
	return r

def __Uu_Sq(a, b):
	# a.reverse()
	r = []
	for c in reversed(a):
		r.append(c)
	
	return r

def __Uu_ke(a, b):
	# a.splice(0,b)
	r = a
	for i in range(0, b):
		r.pop(0)
	
	return r

def __Vu(d):
	# a = a.split("");
	a = []
	for c in d:
		a.append(c)
	
	# Uu.Zo(a,51);
	# Uu.Sq(a,22);
	# Uu.ke(a,3);
	a = __Uu_Zo(a, 51)
	a = __Uu_Sq(a, 22)
	a = __Uu_ke(a, 3)
		
	# Uu.Zo(a,11);
	# Uu.Sq(a,76);
	# Uu.ke(a,2);
	# Uu.Sq(a,3);
	a = __Uu_Zo(a, 11)
	a = __Uu_Sq(a, 76)
	a = __Uu_ke(a, 2)
	a = __Uu_Sq(a, 3)
	
	return "".join(a)

def __appendValue(a, b, c):
	return a + "&" + b + "=" + c

def Cp(a):
	b = string_utils.tokenize(a, '&') 
			
	c = {}
	for d in range(0, len(b)):
		f = b[d].split('=')
		if (len(f) == 1 and len(f[0]) > 0) or len(f) == 2:
			h = unquote(f[0] if len(f[0]) > 0 else "")
			l = unquote(f[1] if len(f[1]) > 0 else "")
			c[h] = l
	
	return c

def Gz(di):
	a = di["url"]
	b = di["sp"]
	c = di["s"]
	
	if len(a) > 0 and a[len(a) - 1] == '\n':
		a = a[0:len(a) - 2]
	
	a = __appendValue(a, "alr", "yes")
# 	if len(c) > 0:
	c = __Vu(unquote(c))
	a = __appendValue(a, b, quote(c))
	
	return a
