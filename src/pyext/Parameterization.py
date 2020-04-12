import os,pickle,random 
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from gensim import corpora, models
from gensim.models.phrases import Phrases, Phraser
import gensim
from sklearn.metrics import fbeta_score
from sklearn.metrics import f1_score
from gensim.models import CoherenceModel
from scipy.stats import entropy
import logging
import Model

class Validation(Model.Model):
    def __init__(self):
        super().__init__()
        self.df=Model.Model().df_pkl
        self.EC_train,self.EC_test=Model.Model().get_train_and_test(Model.Model().df_pkl)
        self.dictionary,self.corpus=Model.Model().get_dict_corpus(self.EC_train)
        self.model=gensim.models.ldamodel.LdaModel.load('models/lda_train_150topics_100passes.model')
        self.path='../images/'

    def plot_a_distribution(self,listtoplot,xlabel,xlim_tuple,ylabel,title,name):
        plt.figure(figsize=(8,5))
        sns.set_style("whitegrid")
        g=sns.distplot(listplot,kde=True)
        sns.set(font_scale=1.5);
        g.set_xlabel(xlabel,fontsize=20,);
        g.set_ylabel(ylabel,fontsize=20,);
        g.set_title(title,fontsize=20,pad=30)
        g.set_xlim([xlim_tuple[0],xlim_tuple[1]])
        plt.tight_layout()
        plt.savefig(self.path+name,type='png');

    def get_topic_similarity(self,topics,model,distance='jaccard'):
        mdiff, annotation = model.diff(model, distance=distance, num_words=100)
        fig, ax = plt.subplots(figsize=(18, 14))
        data = ax.imshow(mdiff, cmap='RdBu_r', origin='lower')
        plt.title(distance+'distance')
        plt.colorbar(data)
        plt.tight_layout()
        plt.savefig(self.path+name,type='png');
        sim_list=[j for i in mdiff for j in i]
        self.plot_a_distribution(sim_list,xlabel='Similarity',
                                xlim_tuple=(0,1),
                                ylabel='Density',title='Distance similarity between topics',
                                name=topics+'topic_sim')

    def compare_2_lists(self,list_sol,list_true,total_words):
        TP=len([i for i in list_sol if i in list_true])
        FP=len([i for i in list_sol if i not in list_true])
        FN=len([i for i in list_true if i not in list_sol])
        TN=len([i for i in [i for i in total_words if i not in list_true] 
                    if i not in list_sol])
        return (TP,FP,FN,TN)

    def get_specificity(self,input_tuple):
        if (input_tuple[1]+input_tuple[3])>0:
            TPR=input_tuple[3]/(input_tuple[1]+input_tuple[3])
        else:
            TPR=0.0
        return TPR

    def get_recall(self,input_tuple):
        if (input_tuple[0]+input_tuple[2])>0:
            recall=input_tuple[0]/(input_tuple[0]+input_tuple[2])
        else:
            recall=0.0
        return recall

    def get_precision(self,input_tuple):
        if (input_tuple[0]+input_tuple[1])>0:
            precision=(input_tuple[0]/(input_tuple[0]+input_tuple[1]))
        else:
            precision=0.0
        return precision

    def get_accuracy(self,input_tuple):
        accuracy=((input_tuple[0]+input_tuple[3])/
                (input_tuple[0]+input_tuple[1]+input_tuple[2]+input_tuple[3]))
        return accuracy

    def get_total_words(self,df):
        EC_unique=set([j for i in df['EC'].to_list() for j in i])
        return EC_unique

    def convert_list_to_df(self,list_to_df):
        d={'EC': list_to_df}
        df=pd.DataFrame(d)
        return df
        
    def compare_sol_true(self,test,true):
        input_tuple=self.compare_2_lists(test,true,self.get_total_words(self.convert_list_to_df()))
        return input_tuple

    def get_solution(self,bow,model):
        Total_sol_enz_list=[]
        doc_distribution=model.get_document_topics(bow=bow,minimum_probability= 0.01)
        idx=[i[0] for i in sorted(doc_distribution, key = lambda x: x[1])[::-1] ]
        for i in idx:
            topic=model.print_topic(topicno=i,topn=4000)
            #take the entire topic strip and make it readable
            entire_list=topic.strip().split('+')
            #fetch all enzymes from the readable topic list
            enzyme_list=[topic.strip().split('+')[i].split('*')[1].replace("\"","").replace(" ","" )
                        for i in range(0,len(entire_list))]
            #only take enzymes/words that have a greater than zero probability
            prob_list=[topic.strip().split('+')[i].split('*')[0] 
                        for i in range(0,len(entire_list))
                        if float(topic.strip().split('+')[i].split('*')[0]) >0.0]
            Total_sol_enz_list=Total_sol_enz_list+enzyme_list[:len(prob_list)]
        #return unique set of enzymes
        Total_sol_enz_list=list(set(Total_sol_enz_list))
        return Total_sol_enz_list

    def solution_for_one_random_doc(self,corpus):
        random_pathway_index = np.random.randint(len(corpus))
        bow = self.dictionary.doc2bow(corpus.iloc[random_pathway_index,2])
        pathway=corpus.iloc[random_pathway_index,1]
        true= list(set(corpus.iloc[random_pathway_index,2]))
        total_sol_enz_list=self.get_solution(bow)
        return tota_sol_enz_list,true

    def evaluate_one_random_doc(self,corpus):
        Total_sol_enz_list,true=solution_for_one_random_doc(corpus)
        input_tuple=self.compare_sol_true(Total_sol_enz_list,true)
        return input_tuple

    def solution_for_one_df(self,corpus):
        recall_list=[]; precision_list=[];accuracy_list=[];F1_list=[];specificity_list=[]
        for index in range(0,len(corpus)):
            bow = dictionary.doc2bow(corpus.iloc[index,2])
            pathway=corpus.iloc[index,1]
            true= list(set(corpus.iloc[index,2]))
            total_sol_enz_list=self.get_solution(bow)
            input_tuple=self.compare_sol_true(Total_sol_enz_list,true)
            recall_list.append(self.get_recall(input_tuple))
            precision_list.append(self.get_precision(input_tuple))
            accuracy_list.append(self.get_accuracy(input_tuple))
            specificity_list.append(self.get_specificity(input_tuple))
            if (self.get_recall(input_tuple)+self.get_precision(input_tuple))>0:
                F1_list.append((2*self.get_precision(input_tuple)*self.get_recall(input_tuple))/
                        (self.get_recall(input_tuple)+selfget_precision(input_tuple)))
            else:
                F1_list.append(0)
        return (recall_list,precision_list,accuracy_list,F1_list,specificity_list)

    def print_testing_results(self,tuple_of_lists):
        recall_list,precision_list,accuracy_list,F1_list,specificity_list=tuple_of_lists
        print ("Recall mean: {} and median {}".format(np.mean(recall_list),np.median(recall_list)))
        print ("Precision mean: {} and median {}".format(np.mean(precision_list),np.median(precision_list)))
        print ("Accuracy mean: {} and median {}".format(np.mean(accuracy_list),np.median(accuracy_list)))
        print ("F1 mean: {} and median {}".format(np.mean(F1),np.median(F1)))
        print ("specificity mean: {} and median {}".format(np.mean(specificity),np.median(specificity)))

    def nfold_cv(n=1):
        mean_recall=[];mean_precision=[];mean_acc=[];mean_f1=[];mean_specificity=[]
        for i in range(0,n):
            EC_list_train,EC_list_test=Model.Model().get_train_and_test(self.df)
            dictionary,corpus=Model.Model().get_dict_corpus(EC_list_train)
            model=Model.Model().MyLDA(corpus=corpus,
                                     dictionary=dictionary,
                                     num_topics=150,
                                     random_state=np.random.randint(1),
                                     passes=100
                                    )
            test_corpus=Model.Model().get_test_corpus(self.dictionary,EC_list_test) 
            tuple_of_lists=self.solution_for_one_df(test_corpus)
            recall_list,precision_list,accuracy_list,F1,specificity_list=tuple_of_lists
            mean_recall.append(np.mean(recall_list))
            mean_precision.append(np.mean(precision_list))
            mean_acc.append(np.mean(accuracy_list))
            mean_f1.append(np.mean(F1))
            mean_specificity.append(np.mean(specificity_list))
        return (mean_recall,mean_precision,mean_acc,mean_f1,mean_specificity)



if __name__=='__main__':
    Validation()
    print (Validation().corpus)