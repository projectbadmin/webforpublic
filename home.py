import datetime
from flask import redirect, request, session, url_for, jsonify
from commonFunction import send_post_request


def get_dataStreamingList(stream_status, retention_hour, class_code, id, cloudbatchjob_id):
    dataStreamList = send_post_request(
        'https://at05fj659h.execute-api.ap-south-1.amazonaws.com/DataStreamingList', 
        {
        "STREAM_STATUS": stream_status,
        "STREAM_REMAINED_RETENTION_HOUR": retention_hour,
        "STREAM_DATA_CLASS_CODE": class_code,
        "ID": id
        }
    )
    if 'message' in dataStreamList and dataStreamList.get('message', 'No message found')=='request fail':
        return {}
    
    for dataStream in dataStreamList:
        dataStream['CLOUDBATCHJOBLIST'] = []
    
    cloudBatchJobList = send_post_request(
        'https://friwpvbini.execute-api.ap-south-1.amazonaws.com/Get_CloudBatchJob',{
            "ID": cloudbatchjob_id
        }   
    )

    cloudBatchJobListInSession = []
    for key in session.keys():
        if 'status' in session[key] and session[key].get('status') == 'DRAFT':
            cloudBatchJobListInSession.append(session[key])

    if 'message' in cloudBatchJobList and cloudBatchJobList.get('message', 'No message found')=='request fail':
        return {}
    
    # set the cloudBatchJobList from DB to the corresponding dataStream
    for dataStream in dataStreamList:
        for cloudBatchJob in cloudBatchJobList:
            if dataStream['ID'] == cloudBatchJob['DATA_STREAM_ID']:
                dataStream['CLOUDBATCHJOBLIST'].append(cloudBatchJob)

    # set the cloudBatchJobList from section to the corresponding dataStream
    for dataStream in dataStreamList:
        for cloudBatchJob in cloudBatchJobListInSession:
            if dataStream['ID'] == cloudBatchJob['requestid']:
                dataStream['CLOUDBATCHJOBLIST'].append(cloudBatchJob)
    
    return dataStreamList

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
    #response = {}
    #response['message'] = 'request successful'
    #response['DATA_STREAM_ID'] = 'f04485a5-a5c4-11ef-9553-4387f2d8ee77_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    response['requestContentInJSON'] = requestContentInJSON
    return response
