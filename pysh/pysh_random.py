# -*- coding: utf-8 -*-
"""
Created on Sun Jun 6 2016

@author: Eddie
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import random
import numpy.random as rand

from . import utils as u
from . import pysh_globals as g
from . import instruction
from . import pysh_plush_translation
from . import plush_gene as pl

#################################
# random plush genome generator

close_probabilities = None
def random_closes(close_parens_probabilities):
	'''
	Returns a random number of closes based on close_parens_probabilities, which
	defaults to [0.772, 0.206, 0.021, 0.001]. This is roughly equivalent to each selection
	coming from  a binomial distribution with n=4 and p=1/16.
		(see http://www.wolframalpha.com/input/?i=binomial+distribution+4+0.0625)
	This results in the following probabilities:
		p(0) = 0.772
		p(1) = 0.206
		p(2) = 0.021
		p(3) = 0.001
	'''
	prob = random.random()
	global close_probabilities
	if close_probabilities == None:
		close_probabilities = u.reductions(lambda i, j: i + j, close_parens_probabilities) + [1.0]
	parens = 0

	while prob > close_probabilities[1]:
		parens += 1
		del close_probabilities[0]
	return parens


def atom_to_plush_gene(atom_name, evo_params):
	'''
	'''
	instruction = None
	is_literal = False
	closes = None
	silent = None

	markers = evo_params["epigenetic_markers"][:]
	markers.append('_instruction')

	for m in markers:
		if m == '_instruction':
			atom = evo_params['atom_generators'][atom_name]
			if callable(atom): # It's a function
				fn_element = atom() 
				if callable(fn_element): # It's another function!
					instruction = fn_element()
				else:
					instruction = fn_element 
				is_literal = True
			else:
				instruction = atom_name
				#raise Exception("Encountered strange _instruction epigenetic marker: " + str(atom))
		elif m == '_close':
			closes = random_closes(evo_params['close_parens_probabilities'])
		elif m == '_silent':
			if random.random() > evo_params['silent_instruction_probability']:
				silent = True
			else:
			 	silent = False
		else:
			raise Exception("Unknown epigenetic marker type: " + str(m))
	return pl.make_plush_gene(instruction, is_literal, closes, silent)


def random_plush_instruction(evo_params):
	'''
	Returns a random Plush_Instruction object given the atom_generators 
	and the required epigenetic-markers.
	'''
	atom = random.choice(list(evo_params["atom_generators"].keys()))
	return atom_to_plush_gene(atom, evo_params)


def random_plush_genome_with_size(genome_size, evo_params):
	'''
	'''
	atoms = rand.choice(list(evo_params["atom_generators"].keys()), size=genome_size)
	return [atom_to_plush_gene(atom, evo_params) for atom in atoms]


def random_plush_genome(evo_params):
	'''
	Returns a random Plush genome with size limited by max_genome_size.
	'''
	genome_size = random.randint(1, evo_params["max_genome_initial_size"])
	return random_plush_genome_with_size(genome_size, evo_params)



#################################
# random push code generator


def random_push_code(max_points, evo_params):
	'''
	Returns a random Push expression with size limited by max_points.
	'''
	max_genome_size = max(int(max_points /  2), 1)
	return pysh_plush_translation.translate_plush_genome_to_push_program(random_plush_genome(max_genome_size, evo_params))
	