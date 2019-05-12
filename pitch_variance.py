import urllib.request, pickle, time, csv, math
from bs4 import BeautifulSoup, SoupStrainer
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


#Format for selecting player to analyze should be obvious. Putting the right URL in is a bit tricky but follow the examples

#player = 'Clayton_Kershaw'
#url = 'https://www.brooksbaseball.net/tabs.php?player=477132&p_hand=-1&ppos=-1&cn=200&compType=none&risp=0&1b=0&2b=0&3b=0&rType=perc&balls=-1&strikes=-1&b_hand=-1&time=month&minmax=ci&var=gl&s_type=2&gFilt=&startDate=&endDate='
    
#player = 'Chris_Sale'
#url = 'http://www.brooksbaseball.net/tabs.php?player=519242&p_hand=-1&ppos=-1&cn=200&compType=none&gFilt=&time=month&minmax=ci&var=gl&s_type=2&startDate=03/30/2007&endDate=11/04/2018&balls=-1&strikes=-1&b_hand=-1'

#player = "Felix_Hernandez"
#url = 'http://www.brooksbaseball.net/tabs.php?player=433587&p_hand=-1&ppos=-1&cn=200&compType=none&gFilt=&time=month&minmax=ci&var=gl&s_type=2&startDate=03/30/2007&endDate=11/04/2018&balls=-1&strikes=-1&b_hand=-1'

#player = "James_Paxton"
#url = 'http://www.brooksbaseball.net/tabs.php?player=572020&p_hand=-1&ppos=-1&cn=200&compType=none&gFilt=&time=month&minmax=ci&var=gl&s_type=2&startDate=03/30/2007&endDate=05/06/2019&balls=-1&strikes=-1&b_hand=-1'

#player = "Wade_LeBlanc"
#url = 'http://www.brooksbaseball.net/tabs.php?player=453281&p_hand=-1&ppos=-1&cn=200&compType=none&gFilt=&time=month&minmax=ci&var=gl&s_type=2&startDate=03/30/2007&endDate=05/06/2019&balls=-1&strikes=-1&b_hand=-1'

#player = "Greg_Maddux"
#url = 'http://www.brooksbaseball.net/tabs.php?player=118120&p_hand=-1&ppos=-1&cn=200&compType=none&gFilt=&time=month&minmax=ci&var=gl&s_type=2&startDate=03/30/2007&endDate=05/07/2019&balls=-1&strikes=-1&b_hand=-1'

player = "Mariano_Rivera"
url = 'http://www.brooksbaseball.net/tabs.php?player=121250&p_hand=-1&ppos=-1&cn=200&compType=none&gFilt=&time=month&minmax=ci&var=gl&s_type=2&startDate=03/30/2007&endDate=05/07/2019&balls=-1&strikes=-1&b_hand=-1'

#player = 'Jonathan_Papelbon'
#url = 'http://www.brooksbaseball.net/tabs.php?player=449097&p_hand=-1&ppos=-1&cn=200&compType=none&gFilt=&time=month&minmax=ci&var=gl&s_type=2&startDate=03/30/2007&endDate=05/07/2019&balls=-1&strikes=-1&b_hand=-1'


def strain_data():

    with open('./results/'+player + ".csv","w") as my_csv:
        csvWriter = csv.writer(my_csv)
        csvWriter.writerow(['dateStamp','park_sv_id','play_guid','ab_total','ab_count','pitcher_id','batter_id','ab_id','des','type','id','sz_top','sz_bot','pfx_xDataFile','pfx_zDataFile','mlbam_pitch_name','zone_location','pitch_con','stand','strikes','balls','p_throws','gid','pdes','spin','norm_ht','inning','pitcher_team','tstart','vystart','ftime','pfx_x','pfx_z','uncorrected_pfx_x','uncorrected_pfx_z','x0','y0','z0','vx0','vy0','vz0','ax','ay','az','start_speed','px','pz','pxold','pzold','tm_spin','sb'])

    response = urllib.request.urlopen(url)

    for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
        if link.has_attr('href') and str(link).find("pfxVB") >= 0:
            strain_data_2(link['href'])
            time.sleep(0.1) #its good practice to put a sleep in so you don't destroy their servers but you do you
            
def strain_data_2(link):
    response = urllib.request.urlopen(link)

    for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
        if link.has_attr('href') and str(link).find("size=500") >= 0:
            scrape_data("https://www.brooksbaseball.net/pfxVB/" + link['href'])
            time.sleep(0.1)
            
def scrape_data(link):
    page = urllib.request.urlopen(link)
    time.sleep(0.1) #its good practice to put a sleep in so you don't destroy their servers but you do you
    soup = BeautifulSoup(page, 'html.parser')

    all_data = []

    #Trim data, append
    for c in soup.find_all("td"):
        data = str(c).replace('<td>','').replace('</td>','')
        all_data.append(data)

    #Save data
    with open('./results/'+player + ".csv","a", newline='') as my_csv:
        print(len(all_data))
        csvWriter = csv.writer(my_csv)
        for i in range(int(len(all_data)/51)):
            csvWriter.writerow(all_data[51*i:51*(i+1)])            

 
def panda_time():
    
    # Getting back the objects:
    data = pd.read_csv('./results/'+player + '.csv')

    #filter down to just the stuff we want    
    filtered_df = data[['batter_id','mlbam_pitch_name']]
    filtered_df.to_csv('./results/'+player + "_filtered.csv",index=False)

    return filtered_df



def work_with_data_pitch_var(filtered_df,cutoffs):

    #Find out types of pitches thrown
    pitch_types = filtered_df.mlbam_pitch_name.unique()

    #total # of pitches thrown
    num_to_player = filtered_df['batter_id'].value_counts()

    total_pitches_by_type = [[0 for i in range(len(pitch_types))] for j in range(len(cutoffs))]


    #goes through each pitch, figures out which cutoff bracket it goes in and which pitch it is and places it in the right bucket
    #really inefficient but couldn't think of any better way for now
    for i in range(len(filtered_df)):        
        pitch = filtered_df[i:i+1]
        batter = pitch['batter_id']
        pitch_type = pitch['mlbam_pitch_name']
        
        num_to_batter = num_to_player.at[int(batter)]

        grt_cutoff = [num_to_batter > cutoffs[i] for i in range(len(cutoffs))]

        cutoff_col = sum(grt_cutoff)-1

        pitch_ind = np.where(pitch_types == pitch_type[i])
        
        total_pitches_by_type[cutoff_col][pitch_ind[0][0]] += 1

    for i in range(len(total_pitches_by_type)):
        line_sum = sum(total_pitches_by_type[i])
        for k in range(len(total_pitches_by_type[i])):
            total_pitches_by_type[i][k] = (total_pitches_by_type[i][k])/(line_sum+1)

    #return the data struct and types of pitches thrown
    return [total_pitches_by_type, pitch_types]


def plot_data(total_pitches_by_type,pitch_types,cutoffs):
    bar_colors = ["#FCE4EC",  
                  "#F8BBD0",
                  "#F48FB1",
                  "#F06292",
                  "#E91E63",
                  "#D81B60",
                  "#AD1457",
                  "#880E4F"]
    len(pitch_types)
    X = np.arange(len(pitch_types))
    print(1/(len(cutoffs)*len(pitch_types)))
    print(X)

    plots = []
    
    for i in range(len(cutoffs)):
        c = plt.bar(X + i/(len(cutoffs)+1)-math.floor(len(cutoffs)/2)/len(cutoffs), total_pitches_by_type[i], color = bar_colors[i+2], width = 4/(len(cutoffs)*len(pitch_types)))
        plots.append(c)
    plt.title("Types of pitches thrown by " + player + " compared to frequency of facing batter")
    plt.xlabel("Pitch Type")
    plt.xticks(X, pitch_types)
    plt.ylabel("Frequency Thrown")
    plt.legend(plots, ['data < 25', '25 < data < 50', '50 < data < 75', '75 < data < 125', '125 < data < 200', '200 < data'])
    plt.savefig('./results/'+player+'_figure.png')
    plt.show()
    plt.close()
####################

all_data = []
cutoffs = [0,25,50,75,125,200]
strain_data()
filtered_df = panda_time()
[big_data,types] = work_with_data_pitch_var(filtered_df,cutoffs)
plot_data(big_data,types,cutoffs)
