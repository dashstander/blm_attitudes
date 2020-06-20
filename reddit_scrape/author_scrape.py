import aiofiles
import asyncio
import json
import pandas as pd
import re
from reddit_scrape.reddit_search import RedditAuthorCommentSearch


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


async def main():
    with open('credentials.json') as creds_file:
        creds = json.load(creds_file)
    bpt_accounts = pd.read_csv('almostdone.csv')
    api = RedditAuthorCommentSearch(credentials=creds, size=1000)
    counter = 24
    i = 0
    chunks = []
    async for batch in api.search(bpt_accounts.author.tolist(), return_batch=True):
        chunks.append(make_df(batch))
        i += 1
        if i % 50 == 0:
            print(f'Collected the {i}th dataframe.')
        if i % 500 == 0:
            df = clean_df(chunks)
            chunks = []
            print(f'Got df with {df.shape[0]} rows')
            async with aiofiles.open(f'/Users/dashiell/verified_bpt/comments_{counter}.csv', mode='w') as fp:
                await fp.write(df.to_csv(index=False))
            counter += 1
    if len(chunks) > 0:
        df = clean_df(chunks)
        df.to_csv(f'/Users/dashiell/verified_bpt/comments_{counter}.csv', index=False)
            

if __name__ == '__main__':
    asyncio.run(main())
