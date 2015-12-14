import pickle
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import numpy as np

# Load in data
us = pickle.load(open("wikivoyage_text_US.p","rb"))
canada = pickle.load(open("wikivoyage_text_Canada.p","rb"))
europe = pickle.load(open("wikivoyage_text_Europe.p","rb"))
mexico = pickle.load(open("wikivoyage_text_Mexico.p","rb"))

# Combine into one dataframe
df = pd.DataFrame.from_dict(us,orient='index')
df['region'] = 'us'
df = df.reset_index()
df = df.rename(columns=({ 'index' : 'Name'}))

dfsets = [canada,europe,mexico]
dfset_names = ['canada','europe','mexico']

for dataset in range(0,3):

    df1 = pd.DataFrame.from_dict(dfsets[dataset],orient='index')
    df1['region'] = dfset_names[dataset]
    df1 = df1.reset_index()
    df1 = df1.rename(columns=({ 'index' : 'Name'}))
    df = df.append(df1,ignore_index=True)

# Remove wiki markup from text
def unwiki(wiki):
        # from https://github.com/lukeorland/wikipedia_sentences_refs/blob/master/mediawiki_article_sentences_refs/wiki2plain.py
        """
       Remove wiki markup from the text.
       """
        wiki = re.sub(r'(?i)\{\{IPA(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'(?i)\{\{Lang(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\|[^\{\}]*?\|\}', '', wiki)
        wiki = re.sub(r'(?i)\[\[Category:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[Image:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[File:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'\[\[[^\[\]]*?\|([^\[\]]*?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', '', wiki)
        wiki = re.sub(r'(?i)File:[^\[\]]*?', '', wiki)
        wiki = re.sub(r'\[[^\[\]]*? ([^\[\]]*?)\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r"''+", '', wiki)
        wiki = re.sub(r'(?m)^\*$', '', wiki)

        return wiki

def unhtml(html):
        """
       Remove HTML from the text.
       """
        html = re.sub(r'(?i)&nbsp;', ' ', html)
        html = re.sub(r'(?i)<br[ \\]*?>', '\n', html)
        html = re.sub(r'(?m)<!--.*?--\s*>', '', html)
        html = re.sub(r'(?i)<ref[^>]*>[^>]*<\/ ?ref>', '', html)
        html = re.sub(r'(?m)<.*?>', '', html)
        html = re.sub(r'(?i)&amp;', '&', html)

        return html

def f(x):
    return unhtml(unwiki(x))


# Remove category pages from dataset
df['text'] = df['text'].apply(f)

pages = df[df['type'] == 'page']

def f(x):
    return re.sub('PAGE', '', x)

pages['Name'] = pages['Name'].apply(f)

pages = pages[pages['loc'].str.contains("//tools.wmflabs.org/wikivoyage/w/poimap2")==True]

StopWords = stopwords.words('english')


# Remove other characters and links from text
def f(x):
    x = re.sub(r'WikiPedia:([\s\S]*)','', x)
    x = re.sub(r'Dmoz:([\s\S]*)','', x)
    x = re.sub(r'\[([\s\S]*)\]','', x)
    x = re.sub(r'[0-9]','', x)
    #x = re.sub(r'\=\=Get in\=\=([\s\S]*)(?=\=\=Get around\=\=)','',x)
    #x = re.sub(r'\=\=Get around\=\=([\s\S]*)(?=\=\=See\=\=)','',x)
    #x = re.sub(r'\=\=Respect\=\=([\s\S]*)(?=\=\=Go next\=\=)','',x)
    #x = re.sub(r'\=\=Stay safe\=\=([\s\S]*)(?=\=\=Go next\=\=)','',x)
    x = re.sub(r'\=\=([\S ]*)\=\=', '', x)
    x = re.sub(r'\=\=Go next\=\=([\s\S]*)','', x)
    return x

pages['regex_text'] = pages['text'].apply(f)

pages2 = pages.reset_index()


# Remove airports from dataset
pages2 = pages2.ix[np.array([i for i,j in enumerate(list(pages2["Name"])) if "Airport" not in j])]

pages2['len'] = map(lambda x: len(x), pages2['regex_text'])

# Remove pages with less than 1000 characters from the dataset
pages2 = pages2[pages2['len']> 1000]

# Tokenize text
features = list(pages2['regex_text'].apply(lambda x: "".join(x.lower().splitlines())))

tokenizer = RegexpTokenizer(r'\w+')

features = [tokenizer.tokenize(x) for x in features]

# Remove stopwords, short words and wiki references
features = [[y for y in x if y not in StopWords and len(y) >2 and 'wiki' not in y] for x in features]
labels_list = list(pages2['Name'])

# Save to pickle file
pickle.dump(features, open( "features.p", "wb" ) )
pickle.dump(labels_list, open( "labels_list.p", "wb" ) )
