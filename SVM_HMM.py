import array
import re
from collections import deque
import random
import datetime
from random import shuffle
num_api_features = 155
time_feature = 169
import numpy as np

import matplotlib
matplotlib.use('Agg') 

import matplotlib.pyplot as plt
def get_time_diff_seconds(start, current):
	time1 = datetime.datetime.fromtimestamp(start)
	time2 = datetime.datetime.fromtimestamp(current)
	delta = time2 - time1
	return delta.seconds

#2 = beneign
#1 = malicious
def generate_training_set(infile,outfile,class_type,mapping, categories):
	qid = 1
	previous =""
	starttime = 0
	state = 1
	window = []
	for line in open(infile, "r"):
		label = line.strip('\n').split(',')
		integer_label=mapping[str(label[4])]
		category = categories[str(label[3])]
		#initialize
		if previous=="":
			previous = str(label[0])
		if state == 1:
			starttime = int(float(label[2]))
			state = 0
		if previous == str(label[0]):
			time_diff = get_time_diff_seconds(starttime, int(float(label[2])))
			
			window.append("%d qid:%d %d:1 %d:1 %d:%d # %s_%s\n" % (class_type,qid,integer_label, category,time_feature,time_diff, str(label[4]), str(label[0])))
		elif previous != str(label[0]):
			previous = str(label[0])
			with open(outfile,"a") as file_map:
				for w in window:
					file_map.write(w)
			window = []
			
			state = 1
			qid +=1
			window.append("%d qid:%d %d:1 %d:1 %d:%d # %s\n" % (class_type,qid,integer_label, category,time_feature,0, str(label[4])))
	return


def print_update(count, line):
	final_line = "%s qid:%d %s %s %s %s\n" % (str(line[0]),count,line[2],line[3],line[5],line[6])
	
	return final_line

def get_array(target, _type, size):
	array = {}
	previous =""
	window = []
	count =0
	for line in open(target, "r"):
		label = line.strip('\n').split(' ')
		if previous=="":
			previous = str(label[1])
		if previous == str(label[1]):
			window.append(line)
		if count > size-1:
			break;
		elif previous != str(label[1]):
			count +=1
			array["%s%s" %(_type,previous)] = window
			previous = str(label[1])
			window = []
			window.append(line)
	return array

def get_array_classify(target):
        array = []
        previous =""
        window = []
        count =0
        for line in open(target, "r"):
                label = line.strip('\n').split(' ')
                if previous=="":
                        previous = str(label[1])
                if previous == str(label[1]):
                        window.append(line)
                elif previous != str(label[1]):
                        count +=1
                        array.append(window)
                        previous = str(label[1])
                        window = []
                        window.append(line)
        return array

def get_array_plot(target):
        array = []
	array2 =[]
        previous =""
        window = []
	window2 = []
        count =0
        for line in open(target, "r"):
                label = line.strip('\n').split(' ')
                if previous=="":
                        previous = str(label[1])
                if previous == str(label[1]):
                        window.append(int(label[3].split(':')[0]))
                        window2.append(int(label[4].split(':')[1]))
                elif previous != str(label[1]):
                        count +=1
                        array.append(window)
                        array2.append(window2)
                        previous = str(label[1])
                        window = []
			window2 = []
                        window.append(int(label[3].split(':')[0]))
                        window2.append(int(label[4].split(':')[1]))
        return array,array2


def k_fold_cross_validation(items, k, randomize=False):

    if randomize:
        items = list(items)
        shuffle(items)

    slices = [items[i::k] for i in xrange(k)]

    for i in xrange(k):
        validation = slices[i]
        training = [item
                    for s in slices if s is not validation
                    for item in s]
        yield training, validation


def generate_10_fold_CV(file1,file2,size1,size2,runid):
	set1 = get_array(file1, 1, size1)
	set2 = get_array(file2, 2, size2)
	combined = dict(set1.items() + set2.items())
	list_of_samples = []
	for key, value in combined.iteritems():
    		temp = [key,value]
    		list_of_samples.append(temp)
	k_fold = 1
	for training, validation in k_fold_cross_validation(list_of_samples, 10):
		train_c = 1
		val_c = 1
		for items in list_of_samples:
			assert (items in training) ^ (items in validation)
			if items in training:
				with open("%s_%s_training.txt"%(runid, k_fold), 'a') as train:
					for line in items[1]:
						train.write(print_update(train_c, line.strip('\n').split(' ')))
				train_c+=1
			if items in validation:
				with open("%s_%s_validation.txt"%(runid, k_fold), 'a') as val:
					for line in items[1]:
						val.write(print_update(val_c, line.strip('\n').split(' ')))
				val_c+=1
		k_fold+=1
	return

def load_categories():
	MAPPING = {}
	count = num_api_features+1
	for line in open("categories.txt", "r"):
		label = line.strip('\n')
		MAPPING[label] = count
		count+=1
	return MAPPING

def load_mapping():
	MAPPING = {}
	count = 1
	for line in open("mapping_all.txt", "r"):
		label = line.strip('\n')
		MAPPING[label] = count
		count+=1
	return MAPPING
def load_output(outfile):
	array  = []
	for line in open(outfile, 'r'):
		array.append(line.strip('\n'))
	return array
	
def generate_final_labeling(outputfile,valfile):
	val_array = get_array_classify(valfile)
	#print val_array
	out_array = load_output(outputfile)
	#print len(out_array)
	position = 0
	correctly_classified = []
	TP = 0
	FN  = 0
	FP = 0
	TN = 0
	print len(val_array)
	for sample in val_array:
		total_2 = 0
		total_1 = 0
		sample_class = 0
		sample_id = ""
		final_score = 2
		for i in range(len(sample)):
			sample_class = int(sample[0].split(' ')[0])
			try:
				sample_id = sample[1].split(' ')[5]
			except:
				pass
			#print out_array[position]
			if int(out_array[position]) == 1:
				total_1+=1
			if int(out_array[position]) == 2:
				total_2+=1
			position+=1
		ratio = float(total_1/float(total_2+total_1))	
		with open("%s_out.txt"%(valfile),"a") as final:
			if sample_class == 1:
				final.write("%s %s\n" % (1, ratio))
			else:
				
				final.write("%s %s\n" % (0, ratio))
	return
	

def calculate_scores(outputfile,valfile, threshold):
	val_array = get_array_classify(valfile)
	#print val_array
	out_array = load_output(outputfile)
	#print len(out_array)
	position = 0
	correctly_classified = []
	print len(val_array)
	for sample in val_array:
		total_2 = 0
		total_1 = 0
		sample_class = 0
		sample_id = ""
		final_score = 2
		for i in range(len(sample)):
			sample_class = int(sample[0].split(' ')[0])
			try:
				sample_id = sample[1].split(' ')[5]
			except:
				pass
			#print out_array[position]
			if int(out_array[position]) == 1:
				total_1+=1
			if int(out_array[position]) == 2:
				total_2+=1
			position+=1
		ratio = float(total_1/float(total_2+total_1))
		if ratio >= threshold:
		with open("%s_out.txt"%(valfile),"a") as final:
			if sample_class == 1:
				final.write("%s %s\n" % (1, ratio))
			else:
				
				final.write("%s %s\n" % (0, ratio))
	
	return

def pot_all(infile):
	#mapping = load_mapping()
	#categories = load_categories()
	sample,array2 = get_array_plot(infile)
	#plt.plot([0],[0])
	count = 0
	for k in range(len(sample)):
		if count > 1999:
			break;
		#plt.plot(array2[k],sample[k],'r-', alpha=0.3)
		plt.plot([i for i in xrange(len(sample[k]))],sample[k],'b-', alpha=0.05)
		count+=1
	plt.axis([0,100,155,169])
	fig = matplotlib.pyplot.gcf()
	fig.set_size_inches(18,2.5)
	plt.savefig('%s.png'%infile, format='png')
	
	return

def clean_dedupe_data(infile,db_file,outfile):
	sample = []
	uptare = []
	agent = []
	zbot = []
	for line in open(db_file, "r"):
		db = line.split(',')
		sample.append(db[0])
		if re.search("[Aa][gG][eE][Nn][Tt]",db[2]):
			agent.append(db[0])
		elif re.search("[Zz][bB][Oo][tT]",db[2]):
			zbot.append(db[0])
		else:
			uptare.append(db[0])
	for line in open(infile,"r"):
		data = line.split(',')
		if data[0] in sample:
			with open(outfile, "a") as sfile:
				sfile.write(line)
		if data[0] in uptare:
			with open("Mal/uptare_data.txt", "a") as ufile:
                                ufile.write(line) 
		if data[0] in agent:
			with open("Mal/agent_data.txt", "a") as afile:
                                afile.write(line) 
		if data[0] in zbot:
			with open("Mal/zbot_data.txt", "a") as zfile:
                                zfile.write(line) 
	
	
def main():
    	#mapping = load_mapping()
	#categories = load_categories()
	#generate_training_set("Mal/family_only_data.txt","Testing3/mal_all_data.txt", 1, mapping, categories)
	#generate_training_set("Mal/uptare_data.txt","Testing3/mal_uptare_data.txt", 1, mapping, categories)
	#generate_training_set("Mal/zbot_data.txt","Testing3/mal_agent_data.txt", 1, mapping, categories)
	#generate_training_set("Mal/agent_data.txt","Testing3/mal_zbot_data.txt", 1, mapping, categories)
	# plot the behavior
	#pot_all("Testing3/mal_all_data.txt")
	#pot_all("Testing3/mal_zbot_data.txt")
	#pot_all("Testing3/mal_agent_data.txt")
	#pot_all("Testing3/mal_uptare_data.txt")
	#pot_all("Testing3/benign_training.txt")
	
	#generate_10_fold_CV("mal_all_data.txt","ben_all_data.txt",1000,2000, 1)
	#generate_10_fold_CV("mal_uptare_data.txt","ben_all_data.txt",1000,2000, 2)
	#generate_10_fold_CV("mal_agent_data.txt","ben_all_data.txt",1000,2000, 3)
	#generate_10_fold_CV("mal_zbot_data.txt","ben_all_data.txt",1000,2000, 4)
	for i in range(1,11):
		generate_final_labeling("Testing3/1_%d.out"% i,"Testing3/1_%d_validation.txt"%i)
	# Get the families:
	#clean_dedupe_data("Mal/mal_data_dedup.txt","results_families.csv","Mal/family_only_data.txt")
	
    	return  

	
		
		
if __name__ == '__main__':
    #unittest.main()
	main()
