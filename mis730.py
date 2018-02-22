import spacy
import re


nlp = spacy.load('en')

def find_area(string):
    num = re.compile(r'(\d\d\d)(-)*( )*(\d\d\d)(-)*( )*(\d\d\d\d)')
    s = num.search(string)
    if s.group(1) in ['201','551']:
        return 'NJ'
    if s.group(1) in ['212','646','332','718','917']:
        return 'NY'
    else:
        return 'Unknown'

def call_time(string):
    tim = re.compile(r'(\d\d):(\d\d):(\d\d)-(\d\d):(\d\d):(\d\d)')
    freq = tim.findall(string)
    tsum = 0
    for i in range(len(freq)):
        t = (int(freq[i][3])-int(freq[i][0]))*3600 + (int(freq[i][4])-int(freq[i][1]))*60 + (int(freq[i][5])-int(freq[i][2]))
        tsum = tsum + t
    return str(len(freq)+1)+' times call avg duration: '+str(tsum/len(freq))+'s'

#record = (r'201-710-0908 3/11/2017 23:20:05-23:20:10 # 5/21/2017 05:30:55-05:31:17 # you have been chosen to win 5 million dollars')
record = (r'332-469-2210 6/05/2017 14:23:44-14:50:50 # your dell warranty is about to expire to renew your warranty')

doc = nlp(record)
stats = 'Unknow'
for t in doc:
    if t.pos_ == 'VERB' and str(t) in ['win','hospital','bill','prize','chosen']:
         stats = 'potential scam'
         break
    else:
         if t.pos_ == 'VERB' and str(t) in ['Dell','service','renew','tecnic supoort','expire']:
             stats = 'dell service'
             break

print(find_area(record),call_time(record),stats)