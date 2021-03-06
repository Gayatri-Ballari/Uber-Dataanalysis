# -*- coding: utf-8 -*-
"""uber-data-analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PQ6kMY4R5kyaHTu_y37zI4lyYBURCV_1

Dataset acquired from Kaggle: https://www.kaggle.com/fivethirtyeight/uber-pickups-in-new-york-city?select=uber-raw-data-jul14.csv

Dataset Name: uber-raw-data-jul14.csv

IMPORT ALL THE LIBRARIES
"""

!pip3 -q install numpy pandas matplotlib seaborn geopy folium datetime scipy sklearn tensorflow

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import geopy.distance
from math import radians,cos,sin,asin,sqrt
import folium
import datetime
from folium.plugins import HeatMap
from scipy.stats import ttest_ind

matplotlib.rcParams.update({'font.size': 12})

"""MOUNTING DRIVE"""

from google.colab import drive
drive.mount('/content/drive')

"""READING DATASET"""

uber_data = pd.read_csv('/content/drive/MyDrive/COMBINED_/dataset/uber-raw-data-jul14.csv')

# Print the first 10 elements
uber_data.head(10)

#print the type of data in Date/Time 
type(uber_data.loc[0,'Date/Time'])

""" CONVERTING STR TO DATETIME FORMAT FOR EASY INDEXING"""

uber_data['Date/Time'] = pd.to_datetime(uber_data['Date/Time'])

"""DIVIDING EACH HOUR IN EXISTING HOUR IN EXCISTING DATE/TIME COLUMN INTO FOUR SMALLER BINS OF 15 MINS EACH """

#create a new column to store this new binned column
uber_data['BinnedHour']=uber_data['Date/Time'].dt.floor('15min')

#printing the new column - BinnedHour
uber_data['BinnedHour']

"""VISUALIZING THE DATSET"""

plt.figure(figsize=(15,8))
uber_data['BinnedHour'].dt.day.value_counts().sort_index().plot(kind='bar',color='green')
for item in plt.gca().get_xticklabels():
    item.set_rotation(45)
plt.title('Uber Rides per day in July 2014 at NYC')
plt.xlabel('Days')
_=plt.ylabel('Rides')

"""**Observe the nearly recurring pattern in the data!. It is very noticable after day 11.**

**Let us have a more closer look at it, say every 15 minutes from July 1 to July 31.**
"""

plt.figure(figsize=(15,8))
uber_data['BinnedHour'].value_counts().sort_index().plot(c='darkblue',alpha=0.8)
plt.title('Uber Rides every 15 mins in the month of July at NYC')
plt.xlabel('Days')
_=plt.ylabel('No. of Rides')

"""The underlying trend is clearly visible now. It conveys that in a day there are times when the pickups are very low and very high, and they seem to follow a pattern.


"""

uber_data['BinnedHour'].value_counts()

#defining a dictionary to map the weekday to day name
DayMap={0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
uber_data['Day']=uber_data['BinnedHour'].dt.weekday.map(DayMap)



#Separating the date to another column
uber_data['Date']=uber_data['BinnedHour'].dt.date

#Defining ordered category of week days for easy sorting and visualization
uber_data['Day']=pd.Categorical(uber_data['Day'],categories=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],ordered=True)

#Separating time from the "BinnedHour" Column
uber_data['Time']=uber_data['BinnedHour'].dt.time

"""**Rearranging the dataset for weekly analysis**"""

weekly_data = uber_data.groupby(['Date','Day','Time']).count().dropna().rename(columns={'BinnedHour':'Rides'})['Rides'].reset_index()
weekly_data.head(10)

"""**Grouping weekly_data by days to plot total rides per week in july 2014.**"""

#Grouping the weekly_data daywise
daywise = weekly_data.groupby('Day').sum()
daywise

#Plotting the graphs for a better visualization
sns.set_style("dark")
plt.figure(figsize=(12,12))

#Creating a customized color palette for custom hue according to height of bars
vals = daywise.to_numpy().ravel()
normalized = (vals - np.min(vals)) / (np.max(vals) - np.min(vals))
indices = np.round(normalized * (len(vals) - 1)).astype(np.int32)
palette = sns.color_palette('Reds', len(vals))
colorPal = np.array(palette).take(indices, axis=0)

#Creating a bar plot
ax=sns.barplot(x = daywise.index,y= vals,palette=colorPal)
plt.ylabel('Total rides')
plt.title('Total Rides by week day in July 2014 at NYC')
for rect in ax.patches:
    ax.text(rect.get_x() + rect.get_width()/2.0,rect.get_height(),int(rect.get_height()), ha='center', va='bottom')

"""**According to the bar plot above, rides are maximum on Thursdays and minimum on Sundays. Sundays having the lowest number of rides makes sense logically, as it's a holiday and people often take rest on that day.**"""

weekly_data = weekly_data.groupby(['Day','Time']).mean()['Rides']
weekly_data.head(10)

#Unstacking the data to create heatmap
weekly_data= weekly_data.unstack(level=0)
weekly_data

plt.figure(figsize=(15,15))
sns.heatmap(weekly_data,cmap='Greens')
_=plt.title('Heatmap of average rides in time vs day grid')

"""**The heatmap indicates that the maximum average uber rides occur around 5:30PM to 6:15PM on Wednesdays and Thursdays and their values fall between 550 to 620.**

**Here is another way of looking at it:**
"""

plt.figure(figsize=(15,12))
weekly_data.plot(ax=plt.gca())
_=plt.title('Average rides per day vs time')
_=plt.ylabel('Average rides')
plt.locator_params(axis='x', nbins=10)

"""**Finding average rides on any day**"""

plt.figure(figsize=(15,10))
weekly_data.T.mean().plot(c = 'black')
_=plt.title('Average uber rides on any day in July 2014 at NYC')
plt.locator_params(axis='x', nbins=10)

"""**This plot further confirms that the average rides on any given day is lowest around 2 AM and highest in the around 5:30 PM.**

**Now, let's try visualizing the relationship between Base and total number of rides in July 2014:**
"""

#A mapper to map base number with its name
BaseMapper={'B02512' : 'Unter', 'B02598' : 'Hinter', 'B02617' : 'Weiter', 'B02682' : 'Schmecken','B02764' : 'Danach-NY'}

#Count plot of Base
plt.figure(figsize=(12,10))
sns.set_style("dark")
_=sns.countplot(x=uber_data['Base'].map(BaseMapper))
plt.ylabel('Total rides')
_=plt.title('CountPlot: Total uber rides vs Base - July 2014, NYC')

"""**The above plot tells us that most uber rides originated from Weiter Base and least from Danach-NY**

**To know more about the distribution of latitudes and longitudes, let's plot their histograms along with KDEs**
"""

plt.figure(figsize=(10,10))
sns.histplot(uber_data['Lat'], bins='auto',kde=True,color='r',alpha=0.4,label = 'latitude')
plt.legend(loc='upper right')
plt.xlabel('Latitude')
plt.twiny()
sns.histplot(uber_data['Lon'], bins='auto',kde=True,color='g',alpha=0.4,label = 'longitude')
_=plt.legend(loc='upper left')
_=plt.xlabel('Longitude')
_=plt.title('Distribution of Latitude and Longitude')

"""**Most latitudes are around 40.25, and longitudes around 40.75. This is true as the dataset comprises information only around New York City. This also indicates that most rides happen around (lat,lon) = (40.25,40.75)**

**Let's display the latitude - longitude information in 2D:**
"""

plt.figure(figsize=(12,12))
sns.scatterplot(x='Lat',y='Lon',data=uber_data,edgecolor='None',alpha=0.5,color='darkblue')
plt.xlabel('Latitude')
plt.ylabel('Longitude')
_=plt.title('Latitude - Longitude Scatter Plot')

"""**The dark blue area in the center shows the regions in New York City that had most number of uber rides in July 2014. The plot is better understood when a geographical map is placed underneath**

**Let's use geopy to calculate the distance between Metropolitan Museum and Emperical State Building**
"""

#This is an example of using geopy
metro_art_coordinates = (40.7794,-73.9632)
empire_state_building_coordinates = (40.7484,-73.9857)

distance = geopy.distance.distance(metro_art_coordinates,empire_state_building_coordinates)

print("Distance = ",distance)

"""**Using geopy on a larger dataset may be time consuming on slower PC's. Hence let's use the haversine method**"""

def haversine(coordinates1,coordinates2):
    
    lat1=coordinates1[0]
    lon1=coordinates1[1]
    lat2=coordinates2[0]
    lon2=coordinates2[1]
    
    #convert to radians and apply haverson formula
    lon1,lat1,lon2,lat2 = map(radians,[lon1,lat1,lon2,lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    r = 3956
    return c*r
print("Distance (mi) = ",haversine(metro_art_coordinates,empire_state_building_coordinates))

"""**Now, Let's try to predict which place they are more closer to, say MM or ESB. This can be done by individually calculating the distance between each uber ride coordinates with MM or ESB coordinates. If they are found to be in a particular threshold radius with MM, then we can predict that the ride is going to MM. Similarly for ESB.**"""

#calculating distance to MM and ESB for each point in the dataset
uber_data['Distance MM'] = uber_data[['Lat','Lon']].apply(lambda x: haversine(metro_art_coordinates,tuple(x)),axis=1)
uber_data['Distance ESB'] = uber_data[['Lat','Lon']].apply(lambda x: haversine(empire_state_building_coordinates,tuple(x)),axis=1)

#printing the first 10 elements of the updated dataset
uber_data.head(10)

#Now, let's keep a threshold of 0.25 miles and calculate the number of points that are closer to MM and ESB
#according to these thresholds

print((uber_data[['Distance MM','Distance ESB']]<0.25).sum())

"""**The result above shows the number of rides predicted to MM and ESB**

"""

distance_range = np.arange(0.1,5.1,0.1)

distance_data = [(uber_data[['Distance MM','Distance ESB']] < dist).sum() for dist in distance_range]

distance_data

#concatentate and transpose
distance_data = pd.concat(distance_data,axis=1)
distance_data = distance_data.T

#Shifting index 
distance_data.index = distance_range

distance_data=distance_data.rename(columns={'Distance MM':'CloserToMM','Distance ESB':'CloserToESB'})

plt.figure(figsize=(12,12))
distance_data.plot(ax=plt.gca())
plt.title('Number of Rides Closer to ESB and MM')
plt.xlabel('Threshold Radius(mi)')
plt.ylabel('Rides')

"""**The number of riders to MM and ESB initially diverges, but comes closer as threshold increases. Hence as radius increases, the rate of people going towards MM gets higher than that to ESB. In another way of thinking, as we expand the radius, most of the newly discovered rides are going to MM.**

**Now let us observe the heatmap plotted on geographical map (using folium)**
"""

#initilize the map around NYC and set the zoom level to 10
uber_map = folium.Map(location=metro_art_coordinates,zoom_start=10)

#lets mark MM and ESB on the map
folium.Marker(metro_art_coordinates,popup = "MM").add_to(uber_map)
folium.Marker(empire_state_building_coordinates,popup = "ESB").add_to(uber_map)

#convert to numpy array and plot it
Lat_Lon = uber_data[['Lat','Lon']].to_numpy()
folium.plugins.HeatMap(Lat_Lon,radius=10).add_to(uber_map)

#Displaying the map
uber_map

"""**Lets reduce the "Influence" of each point on the heatmap by using a weight of 0.5 (by default it is 1)**"""

uber_data['Weight']=0.5

#Take on 10000 points to plot (Just to speed up things)
Lat_Lon = uber_data[['Lat','Lon','Weight']].to_numpy()

#Plotting
uber_map = folium.Map(metro_art_coordinates,zoom_start=10)
folium.plugins.HeatMap(Lat_Lon,radius=15).add_to(uber_map)
uber_map

"""**The plot looks easy to visualize now. Boundaries and intensity distribution is clear**


**Let's now create a HeatMap that changes with time. This will help us to visualize the number of uber rides geographically at a given time.**

**We are plotting only the points that are in a radius of 0.25 miles from MM or ESB**
"""

i = uber_data[['Distance MM','Distance ESB']] < 0.25

i.head(10)

#Create a boolean mask to choose the rides that satisfy the 0.25 radius threshold
i=i.any(axis=1)

i[i==True]

#Create a copy of the data
map_data = uber_data[i].copy()

#use a smaller weight
map_data['Weight'] = 0.1

#Restricting data to that before 8th july for faster calculations
map_data = uber_data[uber_data["BinnedHour"] < datetime.datetime(2014,7,8)].copy()

#Generate samples for each timestamp in "BinnedHour" (these are the points that are plotted for each timestamp)
map_data = map_data.groupby("BinnedHour").apply(lambda x: x[['Lat','Lon','Weight']].sample(int(len(x)/3)).to_numpy().tolist())

map_data

#The index to be passed on to heatmapwithtime needs to be a time series of the following format
data_hour_index = [x.strftime("%m%d%Y, %H:%M:%S") for x in map_data.index]

#convert to list to feed it to heatmapwithtime
date_hour_data = map_data.tolist()

#initialize map
uber_map = folium.Map(location=metro_art_coordinates,zoom_start=10)

#plotting
hm = folium.plugins.HeatMapWithTime(date_hour_data,index=date_hour_data)

#add heatmap to folium map(uber_map)
hm.add_to(uber_map)
uber_map

"""**Click the play button to visualize the timeseries**"""

uber_data

weekends = weekly_data[['Saturday','Sunday']]

weekdays = weekly_data.drop(['Saturday','Sunday'],axis=1)

weekends = weekends.mean(axis=1)
weekdays = weekdays.mean(axis=1)

weekdays_weekends = pd.concat([weekdays,weekends],axis=1)
weekdays_weekends.columns = ['Weekdays','Weekends']

weekdays_weekends

plt.figure(figsize=(15,10))
weekdays_weekends.plot(ax=plt.gca())
weekly_data.T.mean().plot(ax=plt.gca(),c = 'black',label='Net Average')
_=plt.title('Time Averaged Rides: Weekend, Weekdays, Net Average (Whole July)')
_=plt.legend()

"""**The Net average plot is more similar to the weekdays average because there are more weekdays than weekends.** 

**In early morning, weekends have more rides. This makes sense as people often go out at night during the weekends.**

**The number of rides around 8 AM is less on weekends, but more on weekdays as it is usually the time when people goto work. Also, in the weekends, there is a surge in the number of evening rides as people return from work.**

**Let us normalize the weekday and weekends data with their own respective sums. This will give us an insight into the proportional data and help us answer questions like - "What percentage of rides happened around 12AM on weekends or weekdays"?**
"""

plt.figure(figsize=(15,10))
(weekdays_weekends/weekdays_weekends.sum()).plot(ax=plt.gca())
_=plt.title('Time Averaged Rides (Normalized) - Weekend, Weekdays')

"""**Nearly 1.5% of the total rides on weekends happen at midnight but only 0.5% of the total rides happen on weekdays!**
**Also, nearly 2% of the total rides on weekdays happen around 5:30PM!**

**So far, we have made our observations by eye. Let us do a statistical T test to compare the time-averaged rides on weekdays and weekends**

"""

#Grouping by date and time and creating a dataset that gives the total rides every 15 mins
for_ttest = uber_data.groupby(['Date','Time']).count()['Day'].reset_index(level=1)

#Total rides on each day in july
uber_data.groupby(['Date']).count()['Day']

#Normalizing the dataset by dividing rides in each time slot on a day by total number of rides on that day
for_ttest = pd.concat([for_ttest['Day']/uber_data.groupby(['Date']).count()['Day'],for_ttest['Time']],axis=1)

#renaming
for_ttest=for_ttest.rename(columns={'Day':'NormalizedRides'})

for_ttest

for_ttest = pd.concat([for_ttest,pd.to_datetime(for_ttest.reset_index()['Date']).dt.day_name().to_frame().set_index(for_ttest.index).rename(columns={'Date':'Day'})],axis=1)

#uber_data.groupby(['Date','Time','Day']).count().dropna().reset_index()[['Date','Day']].set_index('Date')

for_ttest

"""**The rides are first normalized by dividing the number of rides in each time slot by the total number of rides on that day**

**Then they are grouped by time and split to weekend and weekdays data and a T test is applied on them.**

**A Null hypothesis is assumed: The average ride counts are similar for each time slot on weekends and weekdays**
"""

ttestvals = for_ttest.groupby('Time').apply(lambda x: ttest_ind(x[x['Day']<'Saturday']['NormalizedRides'],x[x['Day']>='Saturday']['NormalizedRides']))

ttestvals=pd.DataFrame(ttestvals.to_list(),index = ttestvals.index)

ttestvals

"""**The t-statistic value is -11.5 around midnight! This means that the assumption(hypothesis) does not hold at that time. The pvalue is very low, hence the null hypthesis is rejected around midnight**

**Let's plot and see the values for all timeslots**

**if we hold a p-value threshold of 5% (confidence level = 95%), corresponding t-statistic value is 1.96**
"""

#Let's plot the "statistic" column
plt.figure(figsize=(15,12))
ax=ttestvals['statistic'].plot(kind='barh',color='red',ax=plt.gca())
plt.locator_params(axis='y', nbins=40)
plt.locator_params(axis='x', nbins=10)
plt.xlabel('t-statistic')
plt.axvline(x=1.96,alpha=0.5,color='black',linestyle='--')
plt.axvline(x=-1.96,alpha=0.5,color='black',linestyle='--')

for rect in ax.patches:
    if(abs(rect.get_width())<1.96):
        rect.set_color('green')
_=plt.title('Bar plot of tstatistic')

"""**The time-average ride counts are assumed similar on weekdays and weekends if the width of the bar plot is less than 1.96. Such values are colored in green.**

**Note that their count is very low**

**Let's visualize a KDE plot of the pvalue to confirm this:**
"""

#KDE plot
plt.figure(figsize=(8,8))
ttestvals['pvalue'].plot(kind='kde',color='darkblue',ax=plt.gca())
plt.title('KDE plot - P_value')
_=plt.xlabel('p_value')

"""**Density peaks around p_value=0. Hence it confirms that the time-averaged rides vary greatly at most time slots on weekends and weekdays**

**P-value distribution:**
"""

plt.figure(figsize=(12,10))
ax=ttestvals['pvalue'].plot(kind='line',color='black',ax=plt.gca())
plt.axhline(y=0.05,alpha=0.5,color='black',linestyle='--')
plt.locator_params(axis='x',nbins=20)
for item in plt.gca().get_xticklabels():
    item.set_rotation(45)
    
_=plt.title('Time vs P_value')
_=plt.ylabel('P_value')

"""**The threshold is p = 0.05. The null hypothesis is accepted at p_values below 0.05**

## Checking Relations in Data
"""

uber_data

#create a copy
df = uber_data.copy()

#get numbers of each weekday
df['WeekDay']=df['Date/Time'].dt.weekday

#Convert datetime to float. egs: 1:15AM will be 1.25, 12:45 will be 12.75 etc
def func(x):
    hr = float(x.hour)
    minute = int(x.minute/15)
    return hr + minute/4
df['Time']=df['Date/Time'].apply(func)

#Get the day number, removing month and year
df['Day']=df['Date/Time'].dt.day

df

#Remove unwanted columns that were created for visualization
df = df.drop(['Date/Time','BinnedHour','Date','Distance MM','Distance ESB','Lat','Lon'],axis=1)

#create a redundant columns for easy counting of tolal rides
df['DropMe']=1

#count the number of rides for a given day, weekday number, time and base
df = df.groupby(['Day','WeekDay','Time','Base']).count()['DropMe'].reset_index().rename(columns={'DropMe':'Rides'})

df

#Weekends are given special emphasis, as their trends were very different from that on weekdays.
#so we devote a special columns indicating whether the day is weekday or not
df['Weekend']=df.apply(lambda x: 1 if(x['WeekDay']>4) else 0,axis=1)

"""**Let's visualize a pairplot**"""

sns.pairplot(df,hue='Base')

"""**Notice the clusters in data! Especially time-rides, day-rides.**

**Let's create a jointplot of Rides vs Time**
"""

plt.figure()
_=sns.jointplot(x='Rides',y='Time',data = df,hue='Base')