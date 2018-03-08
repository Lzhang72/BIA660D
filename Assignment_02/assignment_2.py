
# coding: utf-8

# In[1]:


# This script is for assignment 2 of course BIA 660D
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import random
import time
from selenium.webdriver.common.keys import Keys
import pandas
import requests
import bs4


# In[2]:


def extract_stats_data(driver):
    data_div = driver.find_element_by_id('datagrid')
    data_html = data_div.get_attribute('innerHTML')
    Soup = bs4.BeautifulSoup(data_html, 'html5lib')
    head = [t.text.replace("▼", "") for t in Soup.thead.find_all('th')]
    # print(head)
    contentlist = []
    for t in Soup.tbody.find_all('tr'):
        row_list = []
        for r in t.find_all('td'):
            row_list.append(r.text)
        # row_list_t = tuple(row_list)
        contentlist.append(row_list)
    # print(contentlist)
    DF = pandas.DataFrame.from_records(contentlist, columns=head)
    return DF


def extract_all_pages_data(driver):
    nextpage = driver.find_element_by_css_selector('.paginationWidget-next')
    df = extract_stats_data(driver)
    while nextpage.is_displayed():
        nextpage.click()
        normal_delay = random.normalvariate(3, 0.5)
        time.sleep(normal_delay)
        df = df.append(extract_stats_data(driver))
        nextpage = driver.find_element_by_css_selector('.paginationWidget-next')
    return df


# In[4]:


# This is for Question 1 and 2a
#get into the page that we want
driver = webdriver.Firefox(executable_path='geckodriver.exe')
driver.get('http://www.mlb.com')
stats_header_bar = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'megamenu-navbar-overflow__menu-item--stats')))
stats_header_bar.click()
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)
stats_line_items = stats_header_bar.find_elements_by_tag_name('li')
stats_line_items[0].click()
normal_delay = random.normalvariate(4, 0.5)
view_team_element =  driver.find_element_by_id('st_parent')
view_team_element.click()
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)
hitting_season_select = driver.find_element_by_id('st_hitting_season')
season_select = Select(hitting_season_select)
season_select.select_by_value('2015')
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)
hitting_game_type = driver.find_element_by_id('st_hitting_game_type')
game_type = Select(hitting_game_type)
game_type.select_by_index(0)
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)

#now we extarct the data
dfQ1_raw = extract_stats_data(driver)
dfQ1_ = dfQ1_raw.sort_values(by = ['HR'],ascending = False)
max_hr_team_name = dfQ1_.iloc[0,1]

print('The answer for Q1 is ',max_hr_team_name)

#now we calculate average homerun of each league
ALhr = dfQ1_.loc[dfQ1_['League']=='AL']['HR'].apply(pandas.to_numeric, errors='ignore').mean()

NLhr = dfQ1_.loc[dfQ1_['League']=='NL']['HR'].apply(pandas.to_numeric, errors='ignore').mean()

print('The answer for Q2a is')

if ALhr > NLhr:
    print('AL has most average home run',ALhr,'times')
else:
    if NLhr>ALhr:
        print('NL has most average home run',NLhr,'times')
    else:
        print('AL and NL have same home run game')
#now let's do first inning staff
split = driver.find_element_by_id('st_hitting_hitting_splits')
Select(split).select_by_value('i01')
inning_data = extract_stats_data(driver)

ALhr_1i = inning_data.loc[inning_data['League']=='AL']['HR'].apply(pandas.to_numeric, errors='ignore').mean()

NLhr_1i = inning_data.loc[inning_data['League']=='NL']['HR'].apply(pandas.to_numeric, errors='ignore').mean()

print('The answer for Q2b is')
if ALhr_1i > NLhr_1i:
    print('AL has most average home run in first inning',ALhr_1i,'times')
else:
    if NLhr_1i>ALhr_1i:
        print('NL has most average home run',NLhr_1i,'times')
    else:
        print('AL and NL have same home run game in first inning')


#archive the data to CSV file
dfQ1_.to_csv('Q1Q2a.csv')
inning_data.to_csv('Q2b.csv')

#close the drive
driver.close()


# In[27]:


#now for Q3
driver = webdriver.Firefox(executable_path='geckodriver.exe')
driver.get('http://www.mlb.com')
stats_header_bar = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'megamenu-navbar-overflow__menu-item--stats')))
stats_header_bar.click()
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)
stats_line_items = stats_header_bar.find_elements_by_tag_name('li')
stats_line_items[0].click()
normal_delay = random.normalvariate(4, 0.5)
season_select = driver.find_element_by_id('sp_hitting_season')
season_selection = Select(season_select)
season_selection.select_by_value('2017')
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)
hitting_game_type = driver.find_element_by_id('sp_hitting_game_type')
Select(hitting_game_type).select_by_index(0)
normal_delay = random.normalvariate(1, 0.5)
time.sleep(normal_delay)
sp_hitting_team = driver.find_element_by_id('sp_hitting_team_id')
Select(sp_hitting_team).select_by_visible_text('New York Yankees')
normal_delay = random.normalvariate(1, 0.5)
time.sleep(normal_delay)
sort = driver.find_element_by_css_selector('th.dg-avg > abbr:nth-child(1)')
sort.click()
#extract data
dfQ3 = extract_stats_data(driver)
dfQ3a = dfQ3.loc[dfQ3['AB'].apply(pandas.to_numeric, errors='ignore') >= 30]
player_name = dfQ3a.iloc[0,1]
#print(dfQ3a)

#answer question
print('The answer for the Q3a is :',' ',player_name,'position:',dfQ3a.iloc[0,5])

dfQ3b1 = dfQ3.loc[dfQ3['Pos'] == 'RF']
dfQ3b2 = dfQ3.loc[dfQ3['Pos'] == 'CF']
dfQ3b3 = dfQ3.loc[dfQ3['Pos'] == 'LF']
dfQ3b = dfQ3b1.append(dfQ3b2).append(dfQ3b3)
dfQ3b = dfQ3b.sort_values(by = ['AVG'], ascending = False)

print('the answer for the Q3b is :',dfQ3b.iloc[0,1],'position:',dfQ3b.iloc[0,5])

#archive the data to CSV file
dfQ3.to_csv('Q3.csv')
dfQ3a.to_csv('Q3a.csv')

#close the drive
driver.close()


# In[40]:


#now let's get into Q4
driver = webdriver.Firefox(executable_path='geckodriver.exe')
driver.get('http://www.mlb.com')
stats_header_bar = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'megamenu-navbar-overflow__menu-item--stats')))
stats_header_bar.click()
normal_delay = random.normalvariate(3, 0.5)
time.sleep(normal_delay)
stats_line_items = stats_header_bar.find_elements_by_tag_name('li')
stats_line_items[0].click()
normal_delay = random.normalvariate(4, 0.5)
season_select = driver.find_element_by_id('sp_hitting_season')
season_selection = Select(season_select)
season_selection.select_by_value('2015')
normal_delay = random.normalvariate(3, 0.5)
time.sleep(normal_delay)
hitting_game_type = driver.find_element_by_id('sp_hitting_game_type')
Select(hitting_game_type).select_by_index(0)
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)
league_AL = driver.find_element_by_css_selector('#sp_hitting-1 > fieldset:nth-child(1) > label:nth-child(4)')
league_AL.click()


#get all 2 pages data

dfQ4 = extract_all_pages_data(driver)
dfQ4 = dfQ4.sort_values(by='AB',ascending=False)

print('The answer for the Q4 is:',dfQ4.iloc[0,1],dfQ4.iloc[0,2],dfQ4.iloc[0,5])

#archive the data to CSV file
dfQ4.to_csv('Q4.csv')

#close the drive
driver.close()


# In[43]:


#now let's get into Q5,this gonna take a while to look every player's bio
driver = webdriver.Firefox(executable_path='geckodriver.exe')
driver.get('http://www.mlb.com')
stats_header_bar = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'megamenu-navbar-overflow__menu-item--stats')))
stats_header_bar.click()
normal_delay = random.normalvariate(3, 0.5)
time.sleep(normal_delay)
stats_line_items = stats_header_bar.find_elements_by_tag_name('li')
stats_line_items[0].click()
normal_delay = random.normalvariate(4, 0.5)
season_select = driver.find_element_by_id('sp_hitting_season')
season_selection = Select(season_select)
season_selection.select_by_value('2014')
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)
hitting_game_type = driver.find_element_by_id('sp_hitting_game_type')
Select(hitting_game_type).select_by_index(1)
normal_delay = random.normalvariate(2, 0.5)
time.sleep(normal_delay)

tbody = driver.find_element_by_xpath('/html/body/div[2]/div/div[3]/div/div[1]/div[8]/table/tbody')

players = tbody.find_elements_by_tag_name('tr')

latin_American_list = ['Antigua & Barbuda',
                       'Bahamas','Barbados',
                       'Cayman Islands',
                       'Cuba','Dominica',
                       'Dominican Republic',
                       'Grenada','Guadeloupe',
                       'Haiti','Jamaica','Martinique',
                       'Puerto Rico','Saint Barthélemy',
                       'St. Kitts & Nevis','St. Lucia',
                       'St. Vincent and the Grenadines',
                       'Trinidad & Tobago',
                       'Turks & Caicos Islands',
                       'Virgin Islands',
                       'Belize',
                       'Costa Rica',
                       'El Salvador',
                       'Guatemala',
                       'Honduras',
                       'Mexico',
                       'Nicaragua',
                       'Panama',
                       'Argentina',
                       'Bolivia',
                       'Brazil',
                       'Chile',
                       'Colombia',
                       'Ecuador',
                       'French Guiana',
                       'Guyana',
                       'Paraguay',
                       'Peru',
                       'Suriname',
                       'Uruguay',
                       'Venezuela',
                       'Caribbean',
                       'Central America',
                       'South America',
                       'Latin America',
                       'International',]


Latin_player = []
for i in range(len(players)):
    j=i+1
    xpath = '/html/body/div[2]/div/div[3]/div/div[1]/div[8]/table/tbody/tr[{}]/td[2]/a'
    player_info = driver.find_element_by_xpath(xpath.format(j))
    player_info.click()
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
    player_bio = driver.find_element_by_css_selector('div.player-bio:nth-child(2)')
    born_place1 = player_bio.find_element_by_css_selector('ul:nth-child(2) > li:nth-child(2)')
    born_place2 = player_bio.find_element_by_css_selector('ul:nth-child(2) > li:nth-child(3)')
    born_place3 = player_bio.find_element_by_css_selector('ul:nth-child(2) > li:nth-child(4)')
    born_place = born_place1.text + born_place2.text + born_place3.text
    #print(born_place)
    for t in latin_American_list:
        if t in born_place:
            position = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/header/div/div/ul/li[1]').text
            name = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/header/div/div/h1/span[1]').text
            got_one = [name,position]
            Latin_player.append(got_one)
            #print('found one')
    driver.back()
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)

dfQ5 = pandas.DataFrame.from_records(Latin_player,columns=['Player name','Position'])

print('for Q5, the Latin American all star player listed below:')

print(dfQ5)

dfQ5.to_csv('Q5.csv')
driver.close()
normal_delay = random.normalvariate(1, 0.5)
time.sleep(normal_delay)


# In[45]:


#here are code for Q6
import http.client, urllib.request, urllib.parse, urllib.error, base64,json

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '2c12dc03824946e99e37e5ba42060206',
}

params = urllib.parse.urlencode({
})

try:
    conn = http.client.HTTPSConnection('api.fantasydata.net')
    conn.request("GET", "/v3/mlb/stats/JSON/Games/2016?%s" % params, "{body}", headers)
    response = conn.getresponse()
    data1 = response.read()
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

_games = json.loads(data1)

df_games = pandas.DataFrame.from_records(_games)


headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '2c12dc03824946e99e37e5ba42060206',
}

params = urllib.parse.urlencode({
})

try:
    conn = http.client.HTTPSConnection('api.fantasydata.net')
    conn.request("GET", "/v3/mlb/scores/JSON/Stadiums?%s" % params, "{body}", headers)
    response = conn.getresponse()
    data2 = response.read()
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

_stadium = json.loads(data2)

df_stad = pandas.DataFrame.from_records(_stadium)

#here is the home run houston games:
HR_hous = df_games.loc[df_games['HomeTeam'] == 'HOU']
sche_list = []
for i in range(len(HR_hous)):
    stad_ID = HR_hous.iloc[i,62]
    stad_info = df_stad.loc[df_stad['StadiumID']==stad_ID,['Name','City','State']]
    stad_name = stad_info.iloc[0,0]
    stad_city = stad_info.iloc[0,1]
    stad_state = stad_info.iloc[0,2]
    opp_team = HR_hous.iloc[i,1]
    game_date = HR_hous.iloc[i,19]
    geme_info = [opp_team,game_date,stad_name,stad_city,stad_state]
    sche_list.append(geme_info)
sche_info_HR = pandas.DataFrame.from_records(sche_list,columns=['opponent Team Name', 'game date', 'stadium name', 'city', 'state'])

#here is the away houston games:
away_hous = df_games.loc[df_games['AwayTeam'] == 'HOU']
sche_list_away = []
for i in range(len(away_hous)):
    stad_ID = away_hous.iloc[i,62]
    stad_info = df_stad.loc[df_stad['StadiumID']==stad_ID,['Name','City','State']]
    stad_name = stad_info.iloc[0,0]
    stad_city = stad_info.iloc[0,1]
    stad_state = stad_info.iloc[0,2]
    opp_team = away_hous.iloc[i,33]
    game_date = away_hous.iloc[i,19]
    geme_info = [opp_team,game_date,stad_name,stad_city,stad_state]
    sche_list_away.append(geme_info)
sche_info_away = pandas.DataFrame.from_records(sche_list_away,columns=['opponent Team Name', 'game date', 'stadium name', 'city', 'state'])
#all houston games sorted by date:
sche_info_all = sche_info_HR.append(sche_info_away).sort_values(by='game date')

print('the answer for the Q6:')
print(sche_info_all)

sche_info_all.to_csv('Q6.csv')

