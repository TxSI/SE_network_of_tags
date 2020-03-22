import matplotlib.pyplot as plt
from wordcloud import WordCloud
from dbm import DBM

dbm = DBM()

#Get all tags from all users
all_users = dbm.get_user(flt={'tags':{'$exists':1}})
all_tags = ""
norm_tags = {}
for user in all_users:
    for tag in user['tags']:
        all_tags += tag['name']+" "
        if tag['name'] in norm_tags:
            norm_tags[tag['name']] += tag['count']
        else:
            norm_tags[tag['name']] = tag['count']

print("Number of distinct tags:", len(norm_tags))

# Generate a non-normalized tag cloud image
wordcloud = WordCloud(  width=700,
                        height=500,
                        stopwords=['n'],
                        normalize_plurals=False,
                        max_words=1000).generate(all_tags)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("Non Normalized Tag-Cloud")


# Generate a Normalized tag cloud image
wordcloud = WordCloud(  width=700,
                        height=500,
                        stopwords=['n'],
                        normalize_plurals=False,
                        max_words=1000)\
                    .generate_from_frequencies(norm_tags)

plt.figure()
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("Normalized Tag-Cloud")
plt.show()


