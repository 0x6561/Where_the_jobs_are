import config, imaplib, email
import pprint, re, html, json, csv 
import html2text
#import spacy, nltk  
#from nltk import word_tokenize, pos_tag, ne_chunk
from city_to_state import city_to_state_dict
from geopy import geocoders  
from geopy.exc import GeocoderTimedOut
gn = geocoders.GeoNames(username="0x6561")

from geotext import GeoText

pp = pprint.PrettyPrinter(indent=4)

# for spacy nlp
#spacy_nlp = spacy.load('en')

# for cleaning emails (removing html etc)
remove_tag_regex = re.compile(r'(<!--.*?-->|<[^>]*>)', flags=re.DOTALL)
remove_urls_regex = re.compile(r'(^https?:\/\/.*[\r\n]\*|\s+\s+)', flags=re.DOTALL)
remove_non_ascii_regex = re.compile(r'(\n|\r|\t|=|_|-|&|nbsp|amp|;|:|\s+ \s+|\*|\'|\"|\{|\}|\(|\))', flags=re.DOTALL)
h2t = html2text.HTML2Text()# this should be global
h2t.ignore_links = True
h2t.ignore_images = True

# used to identify emails of interest
# include messages with these in subject
job_words = ['job', 'role', 'opening', 'opportunity', 'position', 'hire', 'developer', 'engineer']
# exclude any with these in subject
job_board = ['indeed', 'linkedin', 'careerbuilder', 'jobing', 'dice', 'monster']


def strip_tags(m):
    m = remove_tag_regex.sub('', m)
    m = remove_urls_regex.sub('',m)
    m = remove_non_ascii_regex.sub(' ',m)
    return m

#for nltk
def nltk_prep():
    nltk.download('words')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')
    nltk.download('maxent_ne_chunker')

def nlp_parse_spacy(txt):
    nlpTxt = spacy_nlp(txt)
    for e in nlpTxt.ents:
        print('Type: %s, Value: %s' % (e.label_, e))

# performs these steps:
#1. Work Tokenization
#2. Parts of Speech (POS) tagging
#3. Named Entity Recognition
def nltk_process(raw_txt):
    raw_txt = nltk.word_tokenize(raw_txt)
    raw_txt = nltk.pos_tag(raw_txt)
    #raw_txt = ne_chunk(raw_txt)
    pattern = 'NP: {<DT>?<JJ>*<NN>}'
    cp = nltk.RegexpParser(pattern)
    result = cp.parse(raw_txt)
    pp.pprint(result)
    return raw_txt 

# returns a 'list' of email ids 
# which have offers (based on email subject)
def get_offers(msgL):
    offer_list = []
    for num in msgL:
        typ, data = M.fetch(num, '(BODY.PEEK[HEADER])')
        for msg_part in data:
            if isinstance(msg_part, tuple):
                msg = email.message_from_string(msg_part[1].decode("utf-8"))
                for header in [ 'from', 'subject' ]:
                    sender = msg['from'].lower()
                    if not any(s in sender for s in job_board):
                        subject = msg['subject'].lower()
                        if any(w in subject for w in job_words):
                            offer_list.append(num)
    return offer_list

def get_mail_body(msg_num):
    body = ''
    #status, data = M.fetch(msg_num, '(RFC822)')
    status, data = M.fetch(msg_num, '(UID BODY[TEXT])')
    body = data[0][1].decode("utf-8")
    body = strip_tags(body)
    return body

# returns a dict with count of cities
def parse_offers(offer_list):
    all_cities = {}
    for o in offer_list:
        body = get_mail_body(o)
        places = GeoText(body)
        c_list = set(places.cities)
        for c in c_list:
            if c in all_cities:
                all_cities[c] += 1
            else:
                all_cities[c] = 1
    return all_cities

# finds state city is in (very unscientific) and
# gets longitude and latititude for city returns 
# a dict with : 'city, state' : city, state, long, lat number of offers
def locate_citys(all_cities):
    locations = {}
    for city in all_cities: # get state city is in
        if city in city_to_state_dict:
            city_state = city + ", " + city_to_state_dict[city] # gets state
            try:
                long_lat = gn.geocode(city_state, exactly_one=False, timeout=10)[0]
                if 'United States' in long_lat.address:
                    locations[str(long_lat)] = [long_lat.address, long_lat.longitude, long_lat.latitude, all_cities[city]] 
                    pp.pprint(locations[str(long_lat)])
            except GeocoderTimedOut as e:
                pp.pprint("Error: geocode failed on input %s with message %s"%(city_state, e.message))
    return locations

def write_csv(data):
    with open('offer_list.csv', 'w' ) as outfile:  
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(['location', 'longitude', 'latitude', 'count'])
        for r in data.keys():
            csv_writer.writerow(data[r])

try:
    M = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    M.login(config.fromaddr, config.password)
    M.select('INBOX', readonly=True)
    typ, data = M.search(None, 'ALL')
    msgList = data[0].split() 
    offers = get_offers(msgList)
    all_cities = parse_offers(offers)
    results = locate_citys(all_cities)
    pp.pprint(results)
    write_csv(results)

finally:
    M.close()
    M.logout()

