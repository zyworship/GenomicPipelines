##########################################################################################
#About this script: 
#	Version : 20180330/001
#	Author  : Dahu Zou & Hengwu Jiao
##########################################################################################


import sys,os,glob,re
import numpy as np
from optparse import OptionParser
import multiprocessing

paml_path = sys.argv[1]
#paml_path = '/home/zdh/Projects/Scavenge/01orthologFind/BGI/dateset5_selection/run_paml'

if not os.path.exists('./01_NodeSeq'):
	os.mkdir('01_NodeSeq')
if not os.path.exists('./02_Trees'):
	os.mkdir('02_Trees')
if not os.path.exists('./03_rate'):
	os.mkdir('03_rate')
if not os.path.exists('./04_siteFreq'):
	os.mkdir('04_siteFreq')


aaL = ["A","R","N","D","C","Q","E","G","H","I","L","K","M","F","P","S","T","W","Y","V"]
genelist = open('genelist.txt','w')
genes = os.listdir(paml_path)
for gene in genes:
	tree_flag = 0
	tree = ''
	node_tree_flag = 0
	node_tree = ''
	ancestor = 0
	end = 0
	end1 = 0
	rate = 0
	ancestor_seq = ''
	final_tree = ''
	tail = ''
	dicta = {}
	if not gene.endswith('phy'):
		continue
	with open('%s/%s/Model01ratio/rst' %(paml_path,gene)) as RST:
		for line in RST:
			line = line.strip()
			if line:
				if line == "Ancestral reconstruction by AAML.":
					tree_flag = 1
					continue
				if tree_flag == 1:
					#print (line)
					tree = line
					tree_flag = 0

				if line == "tree with node labels for Rod Page's TreeView":
					node_tree_flag = 1
					continue
				if node_tree_flag == 1:
					node_tree = line
					#print (node_tree)
					node_tree_flag = 0

				if line == 'List of extant and reconstructed sequences':
					ancestor += 1
					continue
				if line.startswith("Overall accuracy of the"):
                                        end = 1
                                        continue
				if ancestor == 1 and end == 0:
					ancestor_seq += '%s\n'%line
	if tree and node_tree:
		trees = tree.split(')')
		node_trees = node_tree.split(')')
		for i in range(len(node_trees)):
			value = trees[i].strip()
			if value.startswith(':'):
				trees[i] = node_trees[i].split(',')[0] + value
		for j in range(len(trees)):
			if j < len(trees)-1:
				final_tree += trees[j] + ')'
			else:
				tail = ':'.join([node_trees[j].strip(';'),'0.000000;'])
				final_tree += tail
	final_tree = final_tree.replace(' ','')
	TREE = open('./02_Trees/%s.ntree' %gene,'w')
	TREE.write(final_tree)
	TREE.close()
	
	SEQ = open('./01_NodeSeq/%s.nodes' %gene,'w')
	ancestor_seq = ancestor_seq.strip()
	ancestor_seqs = ancestor_seq.split('\n')
 	#print (len(ancestor_seqs))	
	if len(ancestor_seqs) == 1:
		continue
	else:
		#print (len(ancestor_seqs))
		#print (ancestor_seqs)
		#N = len(ancestor_seqs)/2
		genelist.write('%s\n' %gene)
	for i in range(len(ancestor_seqs)):
		#print(i)
		ancestor_seqs[i] = ancestor_seqs[i].strip()
		if i == 0:
			#print (ancestor_seqs[i])
			#print (gene)
			#filter(None,line.split(' '))
			num_len= filter(None,ancestor_seqs[i].split(' '))
			num = num_len[0]
			seq_length = num_len[-1]
		if i > 0:
			#ancestor_seqs[i] = ancestor_seqs[i].strip()
			if ancestor_seqs[i]:
				(seq_name,sequence) = ancestor_seqs[i].split('  ',1)
				seq_name = seq_name.replace(' ','')
				seq_name = seq_name.replace('#','')
				sequence = sequence.replace(' ','')
				if not seq_name.startswith('node'):
					dicta[seq_name] = sequence
				#print (seq_name)
				#print (sequence)
				#aas = ''.join([CODE['standard'][sequence[x:x+3]] for x in range(0,len(sequence),3)])
				#SEQ.write ("%s\t%s\n" %(seq_name,aas))
				SEQ.write ("%s\t%s\n" %(seq_name,sequence))
	N = len(dicta)
	FREQ = open('./04_siteFreq/%s.freq' %gene,'w')
	for i in range(int(seq_length)):
		#good = [dicta[j][i:i+1] for j in dicta]
		#print (good)
		site_seq = ''.join([dicta[j][i:i+1] for j in dicta]) # for i in range(int(seq_length))])
		print (site_seq)
		count = np.array([site_seq.count(aaL[k]) for k in range(20)]).astype(np.int32)
		print (count)
		print (N)
		#count = np.around([site_seq.count(aaL[k]) for k in range(20)],decimals=8)
		np.set_printoptions(precision=7)
		count = count/float(N)
		print (count)
		for l in range(20):
			FREQ.write('%f\t' %np.float64(count[l]))
		FREQ.write('\n')
			
	SEQ.close()
#	with open('%s/%s/Model01ratio/rates' %paml_path,gene)) as RATE:
	OUTRATE = open('./03_rate/%s.rat' %gene,'w')
	with open('%s/%s/Model01ratio/rates' %(paml_path,gene)) as RATE:
		for line in RATE:
			line = line.strip()
			#print (line)
			if line:
				if line.startswith('Site'):
					rate = 1
					continue
				if line.startswith('lnL'):
					end1 = 1
					continue
				if rate == 1 and end1 == 0:
					lines = filter(None,line.split(' '))
					OUTRATE.write('%s\n' %lines[3])
	OUTRATE.close()
			
