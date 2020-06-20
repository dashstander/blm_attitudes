import aiofiles
import asyncio
import json
import pandas as pd
import re
from reddit_scrape.reddit_search import RedditSubmissionSearch, RedditCommentSearch


def make_df(batch):
    return pd.DataFrame([comment.d_ for comment in batch])

def clean_df(data):
    df = pd.concat(data)
    newline = re.compile('[\n\r]')
    comma = re.compile(',')
    newline_token = '&nl;'
    comma_token = '&com;'
    df['body'] = df['body'].str.replace(comma, comma_token).str.replace(newline, newline_token)
    df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s')
    return df

async def do_search(api, start_date, end_date, search_term=None, **kwargs):
    async for batch in api.search(start_date,end_date, search_terms=search_term, return_batch=True, **kwargs):
        yield batch


async def main():
    with open('credentials.json') as creds_file:
        creds = json.load(creds_file)
    # leo_accounts = pd.read_csv('leo.csv')
    api = RedditCommentSearch(credentials=creds, size=1000)
    blm_search_terms = ['BlackLivesMatter', '"Black Lives Matter"', 'BLM', 'AllLivesMatter', 'BlueLivesMatter', '"All Lives Matter"', '"Blue Lives Matter"']
    counter = 0
    i = 0
    chunks = []
    data_dir = 'reddit_blm'
    for term in blm_search_terms:
        print(term)
        search = do_search(api, '2014-01-01', '2020-07-01', search_term=term)
        async for batch in search:
            chunks.append(make_df(batch))
            i += 1
            if i % 100 == 0:
                print(f'\tCollected the {i}th dataframe.')
            if i % 500 == 0:
                df = clean_df(chunks)
                chunks = []
                print(f'\tGot df with {df.shape[0]} rows, searching for term {term}.')
                async with aiofiles.open(f'/Users/dashiell/{data_dir}/comments_{counter}.csv', mode='w') as fp:
                    await fp.write(df.to_csv(index=False))
                counter += 1
        if len(chunks) > 0:
            df = clean_df(chunks)
            chunks = []
            counter += 1
            print(f'\tGot df with {df.shape[0]} rows, searching for term {term}.')
            df.to_csv(f'/Users/dashiell/{data_dir}/comments_{counter}.csv', index=False)
            

if __name__ == '__main__':
    asyncio.run(main())
