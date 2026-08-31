from sqlite3 import Connection

import numpy as np
import requests
from src import youtube_utils

import pytest


def test_get_youtube_video():
    url = 'https://www.youtube.com/watch?v=HqG2xN-M8C8'

    video = youtube_utils.get_youtube_video(url)
    assert isinstance(video, youtube_utils.YoutubeVideo)
    assert video.author_name == 'Big Joel'
    assert video.video_id == 'HqG2xN-M8C8'


def test_get_youtube_video_fail():
    url = 'https://www.youtube.com/watch?v=INVALID'

    with pytest.raises(requests.exceptions.HTTPError):
        video = youtube_utils.get_youtube_video(url)


def test_video_from_id():
    video = youtube_utils.video_from_id('HqG2xN-M8C8')
    assert isinstance(video, youtube_utils.YoutubeVideo)


def test_video_from_id_fail():
    with pytest.raises(requests.exceptions.HTTPError):
        video = youtube_utils.video_from_id('INVALID_ID')


def test_submit_videos_to_db(test_conn: Connection):
    cur = test_conn.cursor()

    video = youtube_utils.YoutubeVideo(title='Test title', 
                                       url='http://youtube.com',
                                       author_name='Tim',
                                       thumbnail=np.zeros((256,256)),
                                       video_id='ABC')
    youtube_utils.submit_videos_to_db(cur, videos=[video])
