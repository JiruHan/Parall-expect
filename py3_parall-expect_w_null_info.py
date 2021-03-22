#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 17:25:30 2020

@author: lwoo0005
"""

#Import relevant modules
import csv
from collections import Counter
from numpy.random import choice
import pandas
import os, errno
import scipy.stats as st
from numpy import std, average, unique
from Bio import SeqIO
from Bio.SeqFeature import SeqFeature
from Bio.SeqFeature import FeatureLocation
import matplotlib
import matplotlib.pyplot as plt

#Input and output definitions
"""
ref_seq = str(raw_input("Input the path to the genome reference file.\n"))
num_muts = int(raw_input("How many mutations?\n"))
num_reps = float(raw_input("How many simulations should be run?\n"))
observed1 = str(raw_input("Please input the path to the first observation CSV file in which genes are in row 1 and frequencies in row 2.\n"))
out_folder = str(raw_input("Where do you want results to go? Enter a path.\n"))
"""

#num_reps = float(raw_input("How many simulations should be run?\n"))
num_reps=100
#ref_seq="/Users/lwoo0005/Documents/Laura_stuff/H_py_An/P12_reference.gb"
ref_seq="/Users/lwoo0005/Documents/Jake_stuff/TEST_YJM978_chm_mito_micron_for_parall-expect.gb"
#observed1=str("/Users/lwoo0005/Documents/Laura_stuff/H_py_An/denovo_filtered_evolved_NODNA_NON.csv")
observed1="/Users/lwoo0005/Documents/Jake_stuff/test_yeast_obs.csv"
out_folder="/Users/lwoo0005/Documents/Jake_stuff/parall-test_2/"
#out_folder="/Users/lwoo0005/Documents/Laura_stuff/H_py_An/parall-expect/24-7-20/"
in_mutvar_genes=["SWH1","YAT1","MST28","PRM9","UIP3"]
in_mutvar_rates=["1.3","1.25","1.2","1.15","1.1"]
#in_mutvar_genes=[]
#in_mutvar_rates=[]

if not os.path.exists(out_folder):
    try:
        os.makedirs(out_folder)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
            
#Collect identities and information for genes of interest
with open(observed1, 'r') as obs:
    ob_data1=(pandas.read_csv(obs, encoding='utf-8',header = 0, names=['gene','freq'],usecols=[1,0])).dropna()
    #ob_data1=(pandas.read_csv(obs, header = 0, names=['gene','freq'],usecols=[1,0])).dropna()
    obs.close()              
#ob_genes1 = [((x.encode('utf-8')).replace('\xe2\x80\x91', '-')) for x in ob_data1['gene'].tolist()]
ob_genes1 = [x for x in ob_data1['gene'].tolist()]
exp_freqs=ob_data1['freq'].tolist()
num_muts=sum(exp_freqs)
ob_gene_freq_dic1 = dict(zip(ob_genes1,exp_freqs))

records = [rec for rec in SeqIO.parse(ref_seq, "genbank")]

#aa redundancy table (generic)
"""
NS_muts_codon_generic_dic={'F':8, 'L':4, 'I':7, 'M': 9, 'V': 6,
                       'S': 4, 'P': 6, 'T':6, 'A': 6, 'Y': 8,
                       'H': 8, 'Q': 8, 'N': 8, 'K': 8, 'D': 8,
                       'E': 8, 'C': 8, 'W': 9, 'R': 4, 'G':6}
"""

aas='FLIMVSPTAYHQNKDECWRG'
NSvals='84796466688888888946'

#NS_muts_codon_generic=
lengths=[]
true_lengths=[]
genes=[]
gois=[]
lois=[]
true_lois=[]
ordered_exp_freqs=[]
mods=[]
for record in records:
    for feature in record.features:
        if feature.type=="CDS":
            try:
                gene_name=str(feature.qualifiers['gene'][0])
            except KeyError:
                gene_name=str(feature.qualifiers['locus_tag'][0])
            start=int(feature.location.start)
            end=int(feature.location.end)
            length= abs(start-end)
            modifier=1
            aa_seq=str(feature.qualifiers['translation'][0])
            table = aa_seq.maketrans(aas,NSvals)
            trans_aa_seq=aa_seq.translate(table)
            NS_total=0
            for aa in trans_aa_seq:
                NS_total+=int(aa)
            all_muts=float(3)*float(length)
            modifier=float(NS_total)/float(all_muts)
            print(modifier)
            genes.append(gene_name)
            underscore_gene_name=gene_name.replace('-','_')
            print(gene_name)
            for in_mod_gene, in_mod_rate in zip(in_mutvar_genes, in_mutvar_rates):
                if gene_name == in_mod_gene or underscore_gene_name == in_mod_gene:
                    modifier=float(modifier)*float(in_mod_rate)
            mod_length=float(modifier)*float(length)
            print(length)
            print(mod_length)
            lengths.append(mod_length)
            true_lengths.append(length)
            mods.append(modifier)
            for ob_gene, exp_freq in zip(ob_genes1, exp_freqs):
                if gene_name == ob_gene or underscore_gene_name == ob_gene:
                    ordered_exp_freqs.append(exp_freq)
                    gois.append(gene_name)
                    true_lois.append(length)
                    lois.append(mod_length)
            #gene_name=""
            #underscore_gene_name=""
            #start=""
            #end=""
            #length=""
            #mod_length=""
            #all_muts=""
            
         
with open(str(out_folder)+"/LWTEST_lengths_of_observed_genes.csv","w") as results:
    wtr = csv.writer(results)
    wtr.writerow(("Gene", "Gene Length"))
    for g, l in zip(gois,true_lois):
        wtr.writerow((g,l))
    results.close()

with open(str(out_folder)+"/LWTEST_lengths_of_all_genes.csv","w") as results:
    wtr = csv.writer(results)
    wtr.writerow(("Gene", "Gene Length"))
    for g, l in zip(genes, true_lengths):
        wtr.writerow((g,l))
    results.close()
                  
#Output file to show overall frequency distribution of gene lengths     
gene_freq_dic = {}
for k,v in Counter(true_lengths).items():
                gene_freq_dic[k]=v
with open(out_folder+"/LWTEST_gene_length_distribution.csv","w") as results2:
        wtr = csv.writer(results2)
        wtr.writerow(("Gene Size", "Frequency"))
        for key in sorted(gene_freq_dic.keys()):
                wtr.writerow((key,gene_freq_dic[key]))

total_genes = len(genes)
weights=[float(l)/float(sum(lengths)) for l in lengths]
wois=[float(l)/float(sum(lengths)) for l in lois]

from matplotlib import rcParams
from matplotlib.ticker import FormatStrFormatter
from matplotlib import cm

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Avenir']
#rcParams['font.family'] = 'sans-serif'
#rcParams['font.sans-serif'] = ['Ariel']

min_mod=min(mods)
max_mod=max(mods)
scaled_mods=[(mod-min_mod)/(max_mod-min_mod) for mod in mods]


polar=[cm.coolwarm(mod) for mod in scaled_mods]
#color=['#B08FF4','red']

just_size_weights=[float(l)/float(sum(true_lengths)) for l in true_lengths]
fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar(genes, weights, lw=0.5, color=polar, ec='black')
ax.bar(genes, just_size_weights, lw=0.5, ec='black', fc='None')
ax.tick_params(axis='y', labelsize=10)
ax.set_xticklabels([])
ax.tick_params(axis='x', labelsize=4)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.xticks(rotation=45)
plt.xlabel('Coding sequence', fontsize=12)
plt.ylabel('Probability', fontsize=12)
plt.savefig(out_folder+'/probability_dist_dif.png',format='png', dpi=600)
plt.show()

#Choosing given number of target genes by probability density fucntion defined by gene size
#This is repeated for the selected number of simulations

def mut_simulator(genes, num_muts, weights):
    end_muts = {}
    sim_muts=choice(genes, size=num_muts, replace =True, p=weights)
    for mut in sim_muts:
        if mut in end_muts.keys():
            end_muts[(mut)]+=1
        else:
            end_muts[str(mut)]=1
    return end_muts

sims=[mut_simulator(genes, num_muts, weights) for i in range(int(num_reps))]

#Same as Bernouilli distribution
all_ob_sims=[]
genome='rest'
for g, w in zip(gois, wois):
    two_things=[g,genome]
    two_weights=[w,1-w]
    ob_sims=[mut_simulator(two_things, num_muts, two_weights) for i in range(int(num_reps))]
    all_ob_sims.append(ob_sims)

max_pops=0
for g, sim in zip(gois, all_ob_sims):
    vals=[]
    for dic in sim:
        for k,v in dic.items():
            if k==g:
                vals.append(v)
            else:
                vals.append(0)
    max_of_vals=max(vals)
    if (max_of_vals) > max_pops:
        max_pops = max_of_vals

headers=["Gene", "Times never hit"]
for i in range(1,max_pops+1):
    a=str("Times hit in " +str(i) +" pops")
    headers.append(a)
headers.append("Experimental hits") 
    
with open(str(out_folder)+"/LWTEST_counts_for_observed_genes.csv","w") as max_count_file:
    wtr = csv.writer(max_count_file, delimiter=',')
    wtr.writerow(headers)
    for g, sim, f in zip(gois, all_ob_sims, ordered_exp_freqs):
        row_data=[g]
        print(g)
        sub_zero=0
        n_collect=[]
        for i in range(1,(max_pops+1)):
            print("For pops hit = " +str(i))
            n=0
            for dic in sim:
                for k,v in dic.items():
                    if k==g:
                        if v==i:
                            n+=1
            n_collect.append(n)
            sub_zero+=n            
            print(n)
        row_data.append(int(num_reps-sub_zero))
        row_data.extend(n_collect)
        row_data.append(f)
        wtr.writerow(row_data)

"""
with open(str(out_folder)+"/LWTEST_counts_for_all_genes.csv","w") as max_count_file:
    wtr = csv.writer(max_count_file, delimiter=',')
    wtr.writerow(headers)
    for g, sim in zip(genes, sims):
        row_data=[g]
        print g
        sub_zero=0
        n_collect=[]
        for i in range(1,(current_max+1)):
            print "For pops hit = " +str(i)
            n=0
            for dic in sim:
                for k,v in dic.items():
                    if k==g:
                        if v==i:
                            n+=1
            n_collect.append(n)
            sub_zero+=n            
            print n
        row_data.append(int(num_reps-sub_zero))
        row_data.extend(n_collect)
        row_data.append(f)
        wtr.writerow(row_data)
"""
#Update headers for null data

current_max=0
for sim in sims:
    for k,v in sim.items():
        if v>current_max:
            current_max=v

null_headers=["Gene", "Times never hit"]
for i in range(1,current_max+1):
    a=str("Times hit in " +str(i) +" pops")
    null_headers.append(a)

with open(str(out_folder)+"/LWTEST_ALL-GENES_simulation_genes-"+str(num_muts)+"_reps-"+str(int(num_reps))+".csv", 'w') as results3:
    wtr=csv.writer(results3)
    wtr.writerow(null_headers)
    for gene in genes:
        row_data=[gene]
        sub_zero=0
        n_collect=[]
        mut_sum_dic = {}
        mut_sum = []
        mut_counter=[]
        for i in range(1,(current_max+1)):
            n=0
            for dic in sims:
                if gene in dic:
                   if dic[gene]==i:
                       n+=1
            n_collect.append(n)
            sub_zero+=n
        row_data.append(int(num_reps-sub_zero))
        row_data.extend(n_collect)
        wtr.writerow(row_data)
results3.close()


with open(str(out_folder)+"/LWTEST_ALL-GENES_simulation_genes-"+str(num_muts)+"_reps-"+str(int(num_reps))+"_multis_by_run.csv", 'w') as results4:
    wtr=csv.writer(results4)
    wtr.writerow(("Run_number", "Gene", "Times_hit"))
    i=0
    for sim in sims:
        i+=1
        for k, v in sim.items():
            if v >=2:
                wtr.writerow((i,k,v))
    results4.close()
#return 

#Collecting count stats. Add more count categories if desired
#Here, multihit genes are not expected to exceed 5 hits
CI_z=st.norm.ppf((1-(float(1)/2)/(num_reps)))
#Count_0 is a list of number of genes of total not picked in a dic
count_0 = [(len(genes)-len(dic)) for dic in sims]
counter_list=[count_0]
for i in range(1,(current_max+1)):
    i_counter=[list(dic.values()).count(i) for dic in sims]
    counter_list.append(i_counter)
max_picks = []
min_picks = []
averages = []
pos_CIs = []
neg_CIs = []
y_err_bars = []
for count_list in counter_list:
    max_picks.append(max(count_list))
    min_picks.append(min(count_list))
    averages.append(average(count_list))
    #y_err_bar = (st.norm.ppf(1-float(1)/num_reps))*std(count_list)/(float(num_reps))**0.5
    y_err_bar = CI_z*(std(count_list,ddof=num_reps-1))/(float(num_reps)**0.5)
    y_err_bars.append(y_err_bar)
    pos_CIs.append(average(count_list)+y_err_bar)
    neg_CIs.append(average(count_list)-y_err_bar)
with open(str(out_folder)+"/LWTEST_STATSb_"+str(num_muts)+"_reps-"+str(int(num_reps))+".csv", 'w') as out:
    stats = csv.writer(out)
    stats.writerow(("Times picked","Max","Min","Average","CI"))
    for i in range(len(counter_list)):
        stats.writerow((i,max_picks[i],min_picks[i],averages[i],str(neg_CIs[i])+", "+str(pos_CIs[i])))
    out.close()
