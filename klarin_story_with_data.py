#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 13:37:02 2022

@author: jayklarin
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import usaddress
import seaborn as sns




st.write("""
## Reading info on our dataset
""")
st.write("""
#### head of data
""")
rest_data=pd.read_csv('/Users/jayklarin/Documents/practicum_local/10_telling_story_with_data/rest_data_us.csv')
st.table(rest_data.head())

# There are three records missing 'chain' data.  Let's look closer
no_chain_info = rest_data[rest_data['chain']!= True]
no_chain_info = no_chain_info[no_chain_info['chain']!= False]
rest_data['chain'] = rest_data['chain'].fillna(False)

st.write("""
## Step 2a
""")
st.write("""
#### Investigate the proportions of the various types of establishments. Plot a graph.
""")
establishment_type = rest_data.groupby(rest_data['object_type'])['id'].count().reset_index()
establishment_type = establishment_type.rename(columns = {'object_type': 'establishment_type','id': 'establishment_count'})
fig_est_type = px.pie(establishment_type, values='establishment_count', names='establishment_type', title='Proportion of Types of Establishments')
st.plotly_chart(fig_est_type)

st.write("""
## Step 2b
""")
st.write("""
#### Investigate the proportions of the various types of chain and nonchain establishments. Plot a graph.
""")

chain_proportions = rest_data.groupby(rest_data['chain'])['id'].count().reset_index()
chain_proportions = chain_proportions.rename(columns = {'chain': 'is_chain','id': 'is_chain_count'})
fig_chain_proportions = px.pie(chain_proportions, values='is_chain_count', names='is_chain', title='Proportion of Chains')
st.plotly_chart(fig_chain_proportions)

st.write("""
## Step 2c
""")
st.write("""
#### Which type of establishment is typically a chain?
""")

rest_chain = rest_data.groupby(['object_type','chain'])['id'].count() #sum function
rest_chain = rest_chain.reset_index(name='count') 
rest_chain = rest_chain.rename(columns = {'object_type': 'rest_type','chain': 'is_chain'})

fig_rest_chain = px.bar(rest_chain, x="rest_type", y="count", color="is_chain",barmode='group', title="Restaurant Type: Chain vs Non-Chain")
fig_rest_chain.update_layout(autosize=False,width=800,height=600,)
st.plotly_chart(fig_rest_chain)

st.write("""
## Step 2c Conclusion
""")
st.write("""
#### The 'Cafe' and 'Fast Food' categories are slightly more likely to be chain restaurants. The 'Bakery' category is exclusive to chain restaurants. The 'Pizza' category is evenly split. The 'Restaruant' and 'Bar' category favors non-chain restaurants 2:1 or more!
""")

st.write("""
## Step 2d
""")
st.write("""
#### What characterizes chains: many establishments with a small number of seats or a few establishments with a lot of seats?
""")
rest_all_count = rest_data.groupby([rest_data['object_name'],rest_data['chain']])['id'].count().reset_index(name='rest_count')
rest_all_seat_avg = rest_data.groupby([rest_data['object_name']])['number'].mean().reset_index(name='avg_seats')
rest_all_data = rest_all_count.merge(rest_all_seat_avg,on=['object_name'])
rest_all_data = rest_all_data.sort_values(by='avg_seats', ascending=False)
fig_rest_all_data = px.histogram(rest_all_data, x="rest_count", color="chain",log_y=True,title='Distrubution of Restaurants by Number of Locations')
fig_rest_all_data.update_traces(opacity=0.75)
st.plotly_chart(fig_rest_all_data)

fig_seats_rest_all_data = px.histogram(rest_all_data, x="avg_seats", color="chain",title='Distrubution of Restaurants by Average Number of Seats')
fig_seats_rest_all_data.update_traces(opacity=0.75)
st.plotly_chart(fig_seats_rest_all_data)

st.write("""
## Step 2d Conclusion
""")
st.write("""
#### The average number of seats for establishment has similar distributions between chain and non-chain restaurants.
""")
st.write("""
#### The restaurant count for chain restaurants have a much wider distribution thank non-chain restaurants, and are much more likely to have multiple restaurants.
""")

st.write("""
## Step 2e
""")
st.write("""
#### Determine the average number of seats for each type of restaurant. On average, which type of restaurant has the greatest number of seats? Plot graphs.
""")

rest_type_count = rest_data.groupby([rest_data['object_type']])['id'].count().reset_index(name='rest_count')
rest_type_seat_avg = rest_data.groupby([rest_data['object_type']])['number'].mean().reset_index(name='avg_seats')

fig_rest_type_seat_avg = px.bar(rest_type_seat_avg, x="avg_seats", y="avg_seats", color="object_type", title="Average Seats Per Category")
fig_rest_type_seat_avg.update_layout(autosize=False,width=800,height=600,)
st.plotly_chart(fig_rest_type_seat_avg)


st.write("""
## Step 2f
""")
st.write("""
#### Put the data on street names from the address column in a separate column.
""")

def clean_address(raw):
    if raw.startswith('OLVERA'):
        clean_address='OLVERA,Los Angeles,USA'
    elif raw.startswith('1033 1/2 LOS ANGELES'):
        clean_address='1033 1/2 LOS ANGELES ST,Los Angeles,USA'
    else:
        raw_address=usaddress.parse(raw)
        dict_address={}
        for i in raw_address:
            dict_address.update({i[1]:i[0]})
        clean_address=dict_address['AddressNumber']+" "+str(dict_address['StreetName'])+str(', Los Angeles,USA')
    return clean_address
    
def extract_street_name(raw):
    if raw.startswith('OLVERA'):
        street_name='OLVERA'
    elif raw.startswith('1033 1/2 LOS ANGELES'):
        street_name='LOS ANGELES ST'
    else:
        raw_address=usaddress.parse(raw)
        dict_address={}
        for i in raw_address:
            dict_address.update({i[1]:i[0]})
        street_name=str(dict_address['StreetName'])
    return street_name

rest_data['street_name']=rest_data.address.apply(extract_street_name)
rest_data['clean_address']=rest_data.address.apply(clean_address)
st.table(rest_data.head())

st.write("""
## Step 2g
""")
st.write("""
#### Plot a graph of the top ten streets by number of restaurants.
""")
street_count = rest_data.groupby(rest_data['street_name'])['id'].count().reset_index()
street_count.columns=['street_name','rest_count']
street_count = street_count.sort_values(by='rest_count', ascending=False)
street_count_top_ten = street_count.head(10)
fig_street_count_top_ten = px.bar(street_count_top_ten, x="street_name", y="rest_count",title="Top Ten Streets with Most Restaurants")
st.plotly_chart(fig_street_count_top_ten)

st.write("""
## Step 2h
""")
st.write("""
#### Find the number of streets that only have one restaurant.
""")
street_count_one_per_street = street_count[street_count['rest_count']==1]
only_one_per_street = len(street_count_one_per_street)
st.write(only_one_per_street)

st.write("""
## Step 2i
""")
st.write("""
#### For streets with a lot of restaurants, look at the distribution of the number of seats. What trends can you see?
""")
street_seat_avg = rest_data.groupby(rest_data['street_name'])['number'].median().reset_index()
street_seat_avg.columns=['street_name','avg_seats']
street_count = street_count[street_count['rest_count']>15]
street_count_seat_avg = street_seat_avg.merge(street_count,on=['street_name'])

fig_street_count_seat_avg = sns.jointplot(x="rest_count", y="avg_seats", data=street_count_seat_avg, kind='reg') 
#fig_street_count_seat_avg2 = 
st.pyplot(fig_street_count_seat_avg)


