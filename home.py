from flask import session
from commonFunction import send_post_request


def get_dataStreamingList():
    userid = session.get('userid', None)
    cookie = session.get('cookie', None)
    response = send_post_request(
        'https://at05fj659h.execute-api.ap-south-1.amazonaws.com/DataStreamingList', 
        {
        "USERID": userid,
        "COOKIE": cookie,
        "STREAM_STATUS": "",
        "STREAM_REMAINED_RETENTION_HOUR": "",
        "STREAM_DATA_CLASS_CODE": ""
        }
    )
    return response