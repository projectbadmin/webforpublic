from flask import redirect, request, session, url_for, jsonify
from commonFunction import send_post_request


def get_dataStreamingList(stream_status, retention_hour, class_code):
    response = send_post_request(
        'https://at05fj659h.execute-api.ap-south-1.amazonaws.com/DataStreamingList', 
        {
        "STREAM_STATUS": stream_status,
        "STREAM_REMAINED_RETENTION_HOUR": retention_hour,
        "STREAM_DATA_CLASS_CODE": class_code
        }
    )
    return response

def request_newJob(datetimeselectiontype, fromdate, todate, fromtime, totime, class_code, fut_opt, expiry_mth, strike_prc, call_put, retention_hour):    
    requestContentInJSON = {
        "DATETIMESELECTIONTYPE": datetimeselectiontype,
        "FROMDATE": fromdate.replace("-", ""),
        "TODATE": todate.replace("-", ""),
        "FROMTIME": fromtime.replace(":", ""),
        "TOTIME": totime.replace(":", ""),
        "CLASS_CODE": class_code,
        "FUT_OPT": fut_opt,
        "EXPIRY_MTH": expiry_mth,
        "STRIKE_PRC": strike_prc,
        "CALL_PUT": call_put,
        "RETENTION_HOUR": retention_hour
    }
    response = send_post_request(
        'https://7r1ppr7pe1.execute-api.ap-south-1.amazonaws.com/Prerequisite_for_stepFunction_DataProvider', requestContentInJSON
    )
    response['requestContentInJSON'] = requestContentInJSON
    return response