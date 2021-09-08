""" Board Game Exchange Reddit Scraper
    Author: jrauenbuehler
    Language: Python 3.9.1
    Last Updated: 2021-09-04
    Notes: Search BoardGameExchange for items that you want to buy, sell, or trade
"""
import os
import praw
import pandas as pd
import logging as log

def search_sub(connection, subreddit, search_list, flair=["None"], post_limit=100,sort_type='new'):
        '''
        Search subreddit for posts that contain matching text in title or body.
        Parameters
        ----------
        connection (str): Connection to the reddit API
        subreddit (str): Subreddit to search through
        search_list (list): Items that you want to search for
        flair (list): Labels on post to filter by (Ex: "For Sale" or "Want to Buy")
        post_limit (int): The number of posts you want to limit search to
        sort_type (str): Category to order by before search (Ex: "new" for new posts, "top" for top posts in last 24hrs, "hot" for hot posts in last 24hrs)
        '''        
        posts_dict = { "title":[], "url":[], "body":[], "link_flair_text":[], "match":[], "sub":[] }
        
        #get new posts from subreddit by sort_type
        if sort_type == 'new':
                posts = connection.subreddit(subreddit).new(limit=post_limit)
        elif sort_type == 'hot':
                posts = connection.subreddit(subreddit).hot(limit=post_limit)
        elif sort_type == 'top':
                posts = connection.subreddit(subreddit).top(limit=post_limit)
        for p in posts:
                for item in search_list:
                        #check if item in search list is in title or body
                        if item in to_lower(p.title) or item in to_lower(p.selftext):
                                posts_dict["title"].append(to_lower(p.title))
                                posts_dict["url"].append(p.url)
                                posts_dict["body"].append(to_lower(p.selftext))
                                posts_dict["link_flair_text"].append(to_lower(p.link_flair_text))
                                posts_dict["match"].append(item)
                                posts_dict["sub"].append(subreddit)

        topics = pd.DataFrame(posts_dict)

        #If applicable filter to only posts with designated flairs
        if not flair:
                pass    #if no flairs listed
        else:
                boolean_series = topics["link_flair_text"].isin(flair)
                topics= topics[boolean_series]

        return topics

def split_list(str_to_split, delimiter):
        '''
        Split string into a list based upon designated parameter
        Parameters
        ----------
        str_to_split (str): string that you want to split. If empty then empty list is returned
        delimiter (str): what you want the list split at
        ''' 
        if pd.isnull(str_to_split):
                lst = []
        else:
                str_lower = to_lower(str_to_split)
                lst = str_lower.split(delimiter)
        return lst

def to_lower(str_to_lower):
        '''
        Try to convert string to lowercase. If NoneType, return "none"
        ''' 
        try:
                str_low = str_to_lower.lower()
        except:
               str_low = 'none'
        return str_low

def main():

        input_file = os.path.join(os.path.dirname(__file__),"input.xlsx")
        input_df = pd.read_excel(input_file)
        sub_scrape = pd.DataFrame()

        #build connection to reddit API
        reddit = praw.Reddit(client_id='',
                             client_secret='',
                             user_agent='',
                             username='',
                             password='')

        #iterate over subs and return items
        for index, row in input_df.iterrows():
                sub = row["subreddit"]
                #convert listed items separated by commas to actual lists
                search = split_list(row["items"],",")
                flairs = split_list(row["flairs"],",")
                limit = row["post_limit"]
      
                #helper function to find items to search for by flair 
                #create temp to write over and append to df
                sub_scrape_temp = search_sub(connection=reddit, subreddit=sub, search_list=search, sort_type='new',flair=flairs, post_limit=limit)
                sub_scrape = sub_scrape.append(sub_scrape_temp)

        #Future Idea: Split body to return n words surrounding keyword. REGEX?
        #Output data to excel
        file_loc = os.path.join(os.path.dirname(__file__), 'output.xlsx')
        sub_scrape.to_excel(file_loc,index=False)


        return True
if __name__ == '__main__':
    res = main()
    print(res)