#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys


# In[19]:


import requests
import json
import pandas as pd
import multiprocessing
import datetime
import time
import matplotlib.pyplot as plt
import yfinance as yf
#import pywhatkit as kit


# In[20]:


def get_data_player(name_card):

    query = '''
    {  

    card(slug: "'''+name_card+'''") {
    name
    slug
    position
    price
    u23Eligible
    grade
    xpNeededForNextGrade
    age
    
    liveSingleSaleOffer{
      price
    }
    
    owners {
      from
      price
    }
    
    player{
      activeClub{
        name
        upcomingGames(first:5){
          status
          date
          competition{
            displayName
          }
          homeTeam{
            ... on Club{
              name
            }
          }
          awayTeam{
            ... on Club{
              name
            }
          }
        }
      }
      
      allSo5Scores{
        nodes{
          playerGameStats{
            gameStarted
          }
          score
          detailedScore{
            totalScore
          }
        				}
      }
      
      cardSupply{
      
        limited
        rare
        superRare
        unique
        season{
          startYear
        }
      }
    }
  }
}'''
    
    url = 'https://api.sorare.com/graphql/'
    r = requests.post(url, json={'query': query})
   # print('request status:', r.status_code)
    data = r.json()
    return data


# In[21]:


'''Get name of card and return the price actualy (if he is sell) and all the price of all time'''

def get_price_player(name_card):

    query = '''
    {  

    cards(slugs: '''+name_card+''') {
    slug
    grade
    liveSingleSaleOffer{
      price
    }
    player{
    cardSupply{
        limited
        rare
        superRare
        unique
      }
      }
    
    owners {
      from
      price
      transferType
    }
    }
}'''
    
    url = 'https://api.sorare.com/graphql/'
    r = requests.post(url, json={'query': query})
    #print('request status:', r.status_code)
    data = r.json()
    return data


# In[22]:


def get_all_price(card):
    position_first = card['slug'][-1::-1].index("-")
    name = card['slug'][:-1*(position_first+1)]
    position_two = name[-1::-1].index("-")
    type_card = name[-1*(position_two):]    
    lst_card_price_all = []
    lst_sale_offer_price_all = []
    lst_direct_offer_all =[]
    lst_auction_all = []

    for year in card['player']['cardSupply']:
        number_all_card = list(year.values())
        card_year = year['season']['startYear']
        number_card = ("limited"==type_card)*number_all_card[0] + ("rare"==type_card)*number_all_card[1] + ("superRare"==type_card)*number_all_card[2] +("unique"==type_card)*number_all_card[3]
        #print(number_all_card,card_year)
        lst_card_price = []
        lst_sale_offer_price = []
        lst_direct_offer =[]
        lst_auction = []
        name_all_player = '['
        for j in range(((number_card)//100)+1):
            name_all_player = '['
            for i in range(1,101):
                if(i+j*100>number_card):
                    break
                    # slug_card ,[grade,price_sell_actually,price_sell,date_sell]
                lst_card_price.append(['',[0,0,0,'']])
                name_all_player=name_all_player+'"'+name[:-1*(position_two+5)]+str(card_year)+"-"+type_card+"-"+str(i+j*100)+'",'
            name_all_player = name_all_player[:-1]+']'
            data_temp = get_price_player(name_all_player)
            for k in range(0,100):
                if(k+j*100>number_card-1):
                    break
                lst_card_price[k+j*100][0]=data_temp['data']['cards'][k]['slug']
                lst_card_price[k+j*100][1][0]=data_temp['data']['cards'][k]['grade']
                if data_temp['data']['cards'][k]['liveSingleSaleOffer'] is None:
                    lst_card_price[k+j*100][1][1]=data_temp['data']['cards'][k]['liveSingleSaleOffer']
                else:
                    lst_card_price[k+j*100][1][1]=int(data_temp['data']['cards'][k]['liveSingleSaleOffer']['price'])
                if (data_temp['data']['cards'][k]['owners'] != []):
                    lst_card_price[k+j*100][1][2]=int(data_temp['data']['cards'][k]['owners'][0]['price'])
                    lst_card_price[k+j*100][1][3]=data_temp['data']['cards'][k]['owners'][0]['from']
                    lst_card_price[k+j*100][1][3]=datetime.date(int(lst_card_price[k+j*100][1][3][0:4]),int(lst_card_price[k+j*100][1][3][5:7]),int(lst_card_price[k+j*100][1][3][8:10]))
                    for l in data_temp['data']['cards'][k]['owners']:
                        if ((l['transferType'] == "single_buy_offer" or l['transferType'] == "single_sale_offer") and (l['from'] is not None)):
                            lst_sale_offer_price.append([int(l['price'])/1000000000000000000,datetime.date(int(l['from'][0:4]),int(l['from'][5:7]),int(l['from'][8:10]))])
                        if ((l['transferType'] == "direct_offer") and (l['from'] is not None)):
                            lst_direct_offer.append([int(l['price'])/1000000000000000000,datetime.date(int(l['from'][0:4]),int(l['from'][5:7]),int(l['from'][8:10]))])
                        if ((l['transferType'] == "auction") and (l['from'] is not None)):
                            lst_auction.append([int(l['price'])/1000000000000000000,datetime.date(int(l['from'][0:4]),int(l['from'][5:7]),int(l['from'][8:10]))])

                else:
                    lst_card_price[k+j*100][1][2] = None
                    lst_card_price[k+j*100][1][3] = None
                lst_card_price_all.extend(lst_card_price)
                lst_sale_offer_price_all.extend(lst_sale_offer_price)
                lst_direct_offer_all.extend(lst_direct_offer)
                lst_auction_all.extend(lst_auction)
                    
                

        
    
    #return get_price_player(name_all_player),lst_card_price
    
    
    #return [lst_card_price,lst_sale_offer_price,lst_direct_offer,lst_auction]
   
    return [lst_card_price_all,lst_sale_offer_price_all,lst_direct_offer_all,lst_auction_all]

    #return name_all_player
    #return number_all_card,name[:-position_two-1-4],(name[:-position_two-1][-4:])


# 
# test1= get_all_price(get_data_player("dong-geon-no-2021-rare-2")['data']['card'])
# print(test1)

# In[23]:


def get_small_price_actually(lst_card_price,xp=0):
    small_price, name = None, ""
    for i in lst_card_price:
        if (i[1][1] is not None and i[1][0]>=xp):
            if  (small_price == None):
                small_price = i[1][1]
                name = i[0]
            elif i[1][1]<small_price :
                small_price = i[1][1]
                name = i[0]
    return small_price,name


# In[24]:


def get_small_price_period(lst_card_price,xp=0,last_day=7):
    small_price, name = None, ""
    for i in lst_card_price:
        if (i[1][2] is not None and i[1][0]>=xp) and i[1][2] != 0 and int((datetime.date.today() - i[1][3]).days)<=last_day:
            if  (small_price == None):
                small_price = i[1][2]
                name = i[0]
            elif i[1][2]<small_price :
                small_price = i[1][2]
                name = i[0]
    return small_price,name
    


# In[25]:


def send_message(player,price_went=20,number_phone = "+972533301998",last_send=""):
    data_player = get_price_player('["'+player+'"]')['data']['cards'][0]
    all_price = get_all_price(data_player)[0]
    last_send = ""
    price_online,name_price_online = get_small_price_actually(all_price)
    price_online /=1000000000000000000
    price_eur = round((price_online)*get_value_eth_euro(price_online,datetime.date.today()),2)
    url = 'https://sorare.com/cards/'+name_price_online
    if price_online is not None :
        if price_online<=price_went and last_send!=url:
            last_send = url
            second = datetime.datetime.now().second
            second = (second>40)
            kit.sendwhatmsg(number_phone,url,datetime.datetime.now().hour,datetime.datetime.now().minute+1+second)
    return last_send


# In[26]:


def verif_all_player_message(number_phone="+972533301998"):
    p = open('acheter.txt','r')
    players = p.read().split("\n")
    for i in range(len(players)):
        print(players[i],"\nPrice you went, in ETH (0 if is not important)")
        temp_price = float(input())
        players[i] = [players[i],temp_price*(temp_price>0)+20*(temp_price<=0),""]
    while(True):
        for j in range(len(players)):
            players[j][2]=send_message(players[j][0],players[j][1],number_phone,players[j][2])


# In[27]:


def get_score_data(data_player):
    all_score = []
    for i in data_player['player']['allSo5Scores']['nodes']:
        if i['playerGameStats']['gameStarted'] == 1:
            start = True
        else:
            start = False
        if i['score'] is not None:
            score_temp = round(i['score'])
        else:
            score_temp = 0
        if i['detailedScore'][0]['totalScore'] is not None:
            decisif_score = round(i['detailedScore'][0]['totalScore'])
        else:
            decisif_score = 0
        complet_score = (score_temp - decisif_score)*((score_temp - decisif_score >0))
        all_score.append([start,score_temp,decisif_score,complet_score])
    return all_score


# In[28]:


def get_average(score_list):
    average5,average15,average40 = 0,0,0
    count5,count15,count40 = 0,0,0
    for count, value in enumerate(score_list):
        if count < 5 :
            count5 += (value[1]>0)
            average5+= value[1]
        if count < 15 :
            count15 += (value[1]>0)
            average15+= value[1]
        if count < 40 :
            count40 += (value[1]>0)
            average40+= value[1]
    return average5/((count5)*(count5!=0)+(count5==0)),average15/((count15)*(count15!=0)+(count15==0)),average40/((count40)*(count40!=0)+(count40==0))
    


# In[29]:


def get_value_eth_euro(eth,date):
    date_txt = str(date.year)+"-"+str(date.month)+"-"+str(date.day)
    eth_value = yf.download(tickers='ETH-EUR',start = date_txt,time_interval = "hourly", progress = False)
    return eth_value['Open'][0]


# In[30]:


def sort_list(lst):
    l = len(lst) 
    for i in range(0, l): 
        for j in range(0, l-i-1): 
            if (lst[j][1] > lst[j + 1][1]): 
                tempo = lst[j] 
                lst[j]= lst[j + 1] 
                lst[j + 1]= tempo
    price = [i[0] for i in lst]
    date = [i[1] for i in lst]
    return [price,date]


# In[31]:


def graph_price(all_price):
    lst_sale_offer_price = sort_list(all_price[1])
    lst_direct_offer =sort_list(all_price[2])
    lst_auction = sort_list(all_price[3])
    plt.rcParams["figure.figsize"] = (20,5)
    sale_offer = plt.scatter(lst_sale_offer_price[1],lst_sale_offer_price[0], c='red')
    direct_offer = plt.scatter(lst_direct_offer[1],lst_direct_offer[0], c='blue')
    auction = plt.scatter(lst_auction[1],lst_auction[0], c='green')
    plt.legend((sale_offer,direct_offer,auction),('Sale Offer','Direct Offer', 'Auction'))
    #,figsize=(4,4)
    plt.title('Price of the player')
    plt.xlabel('Date')
    plt.ylabel('ETH')
    #plt.savefig('ScatterPlot_01.png')
    plt.show()


# In[32]:


def graph_grade(all_grade):
    lst_decisive = [i[3] for i in all_grade]
    lst_Full =[i[2] for i in all_grade]
    lst_total = [i[1] for i in all_grade]
    lst_last_game = [i for i in range(len(all_grade))]
    plt.rcParams["figure.figsize"] = (20,5)
    sale_offer = plt.scatter(lst_last_game,lst_decisive, c='red')
    direct_offer = plt.scatter(lst_last_game,lst_Full, c='blue')
    auction = plt.scatter(lst_last_game,lst_total, c='green')
    plt.legend((sale_offer,direct_offer,auction),('All Around','Decisive', 'Total'))
    plt.title('Score of the player')
    plt.xlabel('Last X Game')
    plt.ylabel('Score')
    plt.show()


# In[33]:


def get_slug(user,type_card):
    query = '''
    { user(slug: "'''+user+'''"){
  cards{
    slug
    rarity
  }
}
}'''
    
    url = 'https://api.sorare.com/graphql/'
    r = requests.post(url, json={'query': query})
    #print('request status:', r.status_code)
    data = r.json()
    lst_player = []
    for i in data['data']['user']['cards']:
        if i['rarity'] == type_card:
            lst_player.append(i['slug'])
    return lst_player


# In[34]:


def get_all_data(player,last_day_score=5,xp=0,last_day_buy=7):
    data_player = get_data_player(player)['data']['card']
    all_score = get_score_data(data_player)
    av5,av15,av40 = get_average(all_score)
    every_price = get_all_price(data_player)
    all_price = every_price[0]
    price_online,name_price_online = get_small_price_actually(all_price,xp)
    price_last,name_price_last = get_small_price_period(all_price,xp,last_day_buy)
    date_buy = datetime.date(int(data_player['owners'][0]['from'][0:4]),int(data_player['owners'][0]['from'][5:7]),int(data_player['owners'][0]['from'][8:10]))
        
    print("Name: \t\t",data_player['name'])
    print("Squad: \t\t",data_player['player']['activeClub']['name'])
    print("Grade: \t\t",data_player['grade'])
    print("Age: \t\t",data_player['age'])
    print("Position: \t",data_player['position'])
    print("Next 5 games: ")
    for i in data_player['player']['activeClub']['upcomingGames']:
        print("\t\t Competition:\t",i['competition']['displayName'])
        print("\t\t Match:\t\t",i['homeTeam']['name']," - ",i['awayTeam']['name'])
        print("\t\t Date:\t\t",i['date'][8:10]+i['date'][4:8]+i['date'][0:4],"on :",i['date'][11:16])
        print("\t\t Status:\t\t",i['status'],"\n")
    print("Av 5 games: \t",av5)
    print("Av 15 games: \t",round(av15))
    print("Av 40 games: \t",round(av40))
    print("Score: \t\t")
    for count, j in enumerate(all_score):
        if count >=last_day_score:
            break
        print("\t\t Holder:\t",j[0])
        print("\t\t Decisive:\t",j[3])
        print("\t\t Full:\t\t",j[2])
        print("\t\t Total:\t\t",j[1])
        print()
    graph_grade(all_score)
    print()
    print("Price:")
    print("\t\t We buy:\t\t",int(data_player['price'])/1000000000000000000,"ETH,",round((int(data_player['price'])/1000000000000000000)*get_value_eth_euro(int(data_player['price'])/1000000000000000000,datetime.date.today()),2),"EURO (current rate),",round((int(data_player['price'])/1000000000000000000)*get_value_eth_euro(int(data_player['price'])/1000000000000000000,date_buy),2),"EURO (On Buy)")
    if price_online is not None:
        print("\t\t Actualy on sell:\t",price_online/1000000000000000000,"ETH,",round((price_online/1000000000000000000)*get_value_eth_euro(price_online/1000000000000000000,datetime.date.today()),2),"EURO,",name_price_online)
    if price_last is not None:
        print("\t\t Last",last_day_buy,"on sell:\t",price_last/1000000000000000000,"ETH,",round((price_last/1000000000000000000)*get_value_eth_euro(price_last/1000000000000000000,datetime.date.today()),2),"EURO",name_price_last)
    else:
        price_last = 0
    graph_price(every_price)
    return int(data_player['price']),price_last


# In[37]:


def allPlayerPrint(players,last_day_score=5,xp=0,last_day_buy=7):
    value_squad_buy,value_squad_today = 0,0
    for count, play in enumerate(players):
        value_squad_buy_t,value_squad_today_t=(get_all_data(play,last_day_score,xp,last_day_buy))
        value_squad_buy+=value_squad_buy_t
        value_squad_today+=value_squad_today_t
        print("\n\n______________________________________________________________________________________________________________________\n\n")
        if (count%10==9):
            time.sleep(30)
    value_squad_buy/=1000000000000000000
    value_squad_today/=1000000000000000000
    print("Value Squad when buy:\t\t",value_squad_buy,"ETH,",round(value_squad_buy*get_value_eth_euro(value_squad_buy,datetime.date.today()),2),"EURO")
    print("Value Squad minimum today:\t",value_squad_today,"ETH,",round(value_squad_today*get_value_eth_euro(value_squad_today,datetime.date.today()),2),"EURO")


# # 
# 

# # 

# # 

# 
# 
# 
# 
# 
# # Lancer simplement la fonction ci-dessous
# 
# 
# ## Parametre optionelle :
# 
# ### last_day_score=x, afficher les derniers x notes du joueurs (par defaut 5)
# ### xp=x, afficher le prix des joueurs ayant un xp superieur ou egal a x, (par defaut 0)
# ### last_day_buy=x, afficher le prix le plus bas dans les x dernier jours, (par defaut 7)

# # 

# #### verif_all_player_message() send message automaticaly
# #####  number_phone = "+xxxxxxxxx"

# # 

# In[ ]:


players = get_slug(user="sotech",type_card="limited")
allPlayerPrint(players)


# In[ ]:




