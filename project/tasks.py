from YouTubeIDFetcher import YouTubeIDFetcher
from YouTubeMetaFetcher import YouTubeMetaFetcher
from YouTubeMPDFetcher import YouTubeMPDFetcher
from YouTubeCommentFetcher import YouTubeCommentFetcher
from YouTubeVideoFetcher import YouTubeVideoFetcher
from project import celery
from project import db
from celery.signals import task_prerun
import json
import logging
logger = logging.getLogger('tasks')
@task_prerun.connect
def celery_prerun(*args, **kwargs):
    with celery.app.app_context():
        pass

@celery.task(bind=True)
def fetch(self,queryId,parameters):
    with celery.app.app_context():
        
        from project.models import YoutubeQuery, Task
        query = YoutubeQuery.query.filter_by(id=queryId).first()
        #create the ORM Task Model for the database
        current_task = Task(self.request.id,"IDFetcher")
        query.tasks.append(current_task)
        db.session.commit()
        parameter = {}
        parameter['queryId'] = queryId
        parameter['queryRaw'] = query.queryRaw
        logger.info("Start fetching ids for query id :"+str(parameter['queryId'])+" with parameter: "+parameter['queryRaw'])
        fetcher = YouTubeIDFetcher("https://www.googleapis.com/youtube/v3/search",parameter,int(parameters['HTTPClients']),int(parameters['ClientConnectionPool']),self)

        result = fetcher.work()
        current_task.result = json.dumps(result)
        current_task.state = result['state']
        db.session.commit()
        return result


@celery.task(bind=True)
def meta(self,queryId,parameters):
    with celery.app.app_context():
        from project.models import YoutubeQuery, Task
        query = YoutubeQuery.query.filter_by(id=queryId).first()
        #create the ORM Task Model for the database
        current_task = Task(self.request.id,"MetaFetcher")
        query.tasks.append(current_task)
        db.session.commit()
        parameter = {}
        parameter['queryId'] = queryId
        queryRaw = json.loads(query.queryRaw)
        parameter['key'] = queryRaw['key']
        fetcher = YouTubeMetaFetcher("https://www.googleapis.com/youtube/v3/videos",parameter,int(parameters['HTTPClients']),int(parameters['ClientConnectionPool']),self)
        result = fetcher.work()

        current_task.result = json.dumps(result)
        current_task.state = result['state']
        db.session.commit()
        return result


@celery.task(bind=True)
def manifest(self,queryId):
    with celery.app.app_context():
        from project.models import YoutubeQuery, Task
        query = YoutubeQuery.query.filter_by(id=queryId).first()
        #create the ORM Task Model for the database
        current_task = Task(self.request.id,"ManifestFetcher")
        query.tasks.append(current_task)
        db.session.commit()

        fetcher = YouTubeMPDFetcher("https://www.youtube.com/get_video_info",queryId,1,1,self)
        result = fetcher.work()

        current_task.result = json.dumps(result)
        current_task.state = result['state']
        db.session.commit()
        return result


@celery.task(bind=True)
def comments(self,queryId,parameters):
    with celery.app.app_context():

        from project.models import YoutubeQuery, Task
        query = YoutubeQuery.query.filter_by(id=queryId).first()
        #create the ORM Task Model for the database
        current_task = Task(self.request.id,"CommentFetcher")
        query.tasks.append(current_task)
        db.session.commit()
        parameter = {}
        parameter['get_replies'] = parameters['getReplies']
        parameter['queryId'] = queryId
        queryRaw = json.loads(query.queryRaw)
        parameter['key'] = queryRaw['key']
        fetcher = YouTubeCommentFetcher('https://www.googleapis.com/youtube/v3',parameter, int(parameters['HTTPClients']),int(parameters['ClientConnectionPool']), self)
        result = fetcher.work()

        current_task.result = json.dumps(result)
        current_task.state = result['state']
        db.session.commit()
        return result

@celery.task(bind=True)
def downloadVideos(self,queryId,options):
    with celery.app.app_context():
        from project.models import YoutubeQuery, Task
        query = YoutubeQuery.query.filter_by(id=queryId).first()
        #create the ORM Task Model for the database
        current_task = Task(self.request.id,"VideoFetcher")
        query.tasks.append(current_task)
        db.session.commit()
        option = {}
        option['queryId'] = queryId 
        option['resolution'] = options['resolution']
        option['sound'] = options['sound'] if 'sound' in options else False
        option['method'] = options['method'] if 'method' in options else 'all'
        option['amount'] = options['amount'] if option['method']=='random' else 0
        
        fetcher = YouTubeVideoFetcher('https://www.youtube.com/get_video_info',option, 1, 1, self)
        result = fetcher.work()

        current_task.result = json.dumps(result)
        current_task.state = result['state']
        db.session.commit()
        return result
    