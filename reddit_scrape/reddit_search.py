import praw
import psaw


class RedditSearchBase:
    default_fields = None

    def __init__(self, credentials, size, fields=None):
        self.ps_api = psaw.PushshiftAPI(max_results_per_request=size)
        self.reddit = praw.Reddit(**credentials)
        if fields is None:
            self.fields = self.default_fields

    def search(self, start_date, end_date, return_batch=False, search_terms=None):
        raise NotImplementedError
        

class RedditSubmissionSearch(RedditSearchBase):
    default_fields = [
        'title',
        'selftext',
        'id',
        'subreddit_id',
        'score',
        'num_comments',
        'removed_by_category',
        'author',
        'author_fullname',
        'retrieved_on',
        'stickied',
        'locked',
        'num_crossposts',
        'permalink',
        'link_flair_text',
        'created_utc'
    ]

    def search(self, start_date, end_date, return_batch=False, search_terms=None, subreddit=None):
        params = {
            "since": start_date,
            "before": end_date,
            "filter": self.fields,
            "not:selftext": "[removed]",
            "return_batch": return_batch
        }
        if search_terms:
            params.update({'q': search_terms})
        if subreddit:
            params.update({'subreddit': subreddit})
        return self.ps_api.search_submissions(**params)

    def get_comments(self, submission):
        comment_search = psaw.PushshiftAPI(r=self.reddit).search_comments(
            submission_id=submission.id,
            return_batch=True
        )
        for comment in comment_search:
            author = comment.author.name
            if author == 'AutoModerator':
                continue
            yield {
                'comment_author': author,
                'comment_body': comment.body,
                'comment_score': comment.score,
                'comment_created_utc': comment.created_utc,
                'comment_id': comment.id,
                'comment_parent_id': comment.parent_id
            }

class RedditCommentSearch(RedditSearchBase):
    default_fields = [
        'author',
        'author_flair_text', 
        'author_fullname', 
        'body',
        'created_utc',
        'id', 
        'parent_id',
        'score',
        'subreddit',
        'subreddit_id',
        'retreived_on',
        'stickied',
        'locked'
    ]

    def search(self, start_date, end_date, return_batch=False, search_terms=None, subreddit=None):
        params = {
            "since": start_date,
            "before": end_date,
            "filter": self.fields,
            "return_batch": return_batch
        }
        if search_terms:
            params.update({'q': search_terms})
        if subreddit:
            params.update({'subreddit': subreddit})
        return self.ps_api.search_comments(**params)


class RedditAuthorSearch(RedditSearchBase):
    search_func = None
    
    async def search(self, authors, return_batch=False):
        params = {
            'filter': self.fields,
            'not:author': 'AutoModerator',
            'return_batch': return_batch
        }
        for author in authors:
            if author.lower() == 'automoderator':
                continue
            params['author'] = author
            async for batch in self.search_func(**params):
                yield batch

class RedditAuthorCommentSearch(RedditAuthorSearch):

    default_fields = [
        'author',
        'author_flair_text', 
        'author_fullname', 
        'body',
        'created_utc',
        'id', 
        'parent_id',
        'score',
        'subreddit',
        'subreddit_id',
        'retreived_on',
        'stickied',
        'locked'
    ]

    def __init__(self, credentials, size, fields=None):
        super().__init__(credentials, size, fields)
        self.search_func = self.ps_api.search_comments


class RedditAuthorSubmissionSearch(RedditAuthorSearch):
    
    default_fields = [
        'title',
        'selftext',
        'id',
        'subreddit_id',
        'score',
        'num_comments',
        'removed_by_category',
        'author',
        'author_fullname',
        'retrieved_on',
        'stickied',
        'locked',
        'num_crossposts',
        'permalink',
        'link_flair_text',
        'created_utc'
    ]

    def __init__(self, credentials, size, fields=None):
        super().__init__(credentials, size, fields)
        self.search_func = self.ps_api.search_submissions
