import uuid
from flask import  Flask, jsonify, redirect, render_template, request, session, url_for
from cloudbatchjobresult import fetch_result
from commonFunction import check_logged_in_or_not, findStreamRequestFromSession, findRequestFromSession, send_post_request
from home import get_dataStreamingList, request_newJob
from initialize import initialize
from processUserCode import checkSyntaxBeforeCompile, process, realTimeUpdateLog, checkSyntax
from cloudbatchjobinjava import check_and_generate_keywords_, cloneToNewRequest, cloudbatchjobinjava, cloudbatchjobinjava_edit_program_file, read_javap_result, save

application = Flask(__name__, static_folder='static', template_folder='templates')
initialize(application)


@application.route('/')
def index():
    return redirect(url_for('home'))

@application.route('/home')
def home():
    data_streaming_list = get_dataStreamingList("","","","","")
    return render_template('home.html', data_streaming_list=data_streaming_list)

@application.route('/creation')
def creation():
    return render_template('creation.html')

@application.route('/login', methods=['GET','POST'])
def login():
    logged_in = check_logged_in_or_not()
    if logged_in:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = send_post_request(
            'https://nk32qyplih.execute-api.ap-south-1.amazonaws.com/Login', 
            {'USERNAME': username, 'PASSWORD': password}
        )
        message = response.get('message', 'No message found')
        if message == "Login successful":
            session.permanent = True
            session['userid'] = response.get('userid', None)
            session['cookie'] = response.get('cookie', None)
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@application.route('/logout', methods=['GET'])
def logout():
    send_post_request('https://b22md47un2.execute-api.ap-south-1.amazonaws.com/Logout', {})
    session.clear()
    return redirect(url_for('login'))

@application.route('/cloudbatchjobingui')
def cloudbatchjobingui():
    read_javap_result(application)
    return render_template('cloudbatchjobingui.html')

@application.route('/cloudbatchjobinjava/check_and_generate_keywords', methods=['POST'])
def check_and_generate_keywords():
    data = request.get_json()
    line = data.get('line')
    cursor_pos = data.get('cursor_pos')
    method = data.get('method')
    output = check_and_generate_keywords_(line, cursor_pos, method)
    return jsonify({'output': output})

@application.route('/cloudbatchjobinjava/submit/<stream_id>/<cloudbatchjob_id>', methods=['POST'])
def submitCloudbatchjobinjava(stream_id, cloudbatchjob_id):    
    # get the requestContentInJSON
    requestContentInJSON = ""
    cloudBatchJobrequest = findRequestFromSession(stream_id, cloudbatchjob_id)
    if cloudBatchJobrequest is None:
        return render_template('error.html', error_message="Cloub Batch Job not found")
    else:
        requestContentInJSON = cloudBatchJobrequest['requestContentInJSON']
    
    job_alias = request.form['job_alias']
    code_for_onStart = request.form['code_for_onStart']
    code_for_onProcess = request.form['code_for_onProcess']
    code_for_onEnd = request.form['code_for_onEnd']
    result = checkSyntaxBeforeCompile(application, code_for_onStart, code_for_onProcess, code_for_onEnd, stream_id, requestContentInJSON)
    if(result != ""):
        return render_template('error.html', error_message=result)
    # process the code
    result = process(application, code_for_onStart, code_for_onProcess, code_for_onEnd, stream_id, requestContentInJSON, job_alias)
    # remove the draft session
    for i in range(len(session['CloudBatchJobLocalDraft'])):
        if session['CloudBatchJobLocalDraft'][i]['ID'] == stream_id:
            for j in range(len(session['CloudBatchJobLocalDraft'][i]['CLOUDBATCHJOBLIST'])):
                if session['CloudBatchJobLocalDraft'][i]['CLOUDBATCHJOBLIST'][j]['ID'] == cloudbatchjob_id:
                    del session['CloudBatchJobLocalDraft'][i]['CLOUDBATCHJOBLIST'][j]
                    break
            break
    # return the output
    return redirect(url_for('view_cloudbatchjob_result', stream_id=stream_id, cloudbatchjob_id=cloudbatchjob_id))


@application.route('/cloudbatchjobinjava/latest_output', methods=['POST'])
def get_latest_output():
    data = request.get_json()
    tempPageRequestID = data['tempPageRequestID']
    output = realTimeUpdateLog(application, tempPageRequestID)
    return jsonify({'output': output})


@application.route('/cloudbatchjobinjava/check_syntax_for_onStart', methods=['POST'])
def check_syntax_for_onStart():
    data = request.get_json()
    requestid = data['requestid']
    tempPageRequestID = data['tempPageRequestID']
    # get the requestContentInJSON
    requestContentInJSON = ""
    cloudBatchJobrequest = findRequestFromSession(requestid, tempPageRequestID)
    if cloudBatchJobrequest is None:
        return jsonify({'errors': 'No cloud batch job request found'})
    else:
        requestContentInJSON = cloudBatchJobrequest['requestContentInJSON']
        code_for_onStart = data['code_for_onStart']
        result = checkSyntax(application, "onStart", code_for_onStart, requestid, requestContentInJSON)
        return jsonify({'errors': result})

@application.route('/cloudbatchjobinjava/check_syntax_for_onProcess', methods=['POST'])
def check_syntax_for_onProcess():
    data = request.get_json()
    requestid = data['requestid']
    tempPageRequestID = data['tempPageRequestID']
    # get the requestContentInJSON
    requestContentInJSON = ""
    cloudBatchJobrequest = findRequestFromSession(requestid, tempPageRequestID)
    if cloudBatchJobrequest is None:
        return jsonify({'errors': 'No request found'})
    else:
        requestContentInJSON = cloudBatchJobrequest['requestContentInJSON']
        code_for_onProcess = data['code_for_onProcess']
        result = checkSyntax(application, "onProcess", code_for_onProcess, requestid, requestContentInJSON)
        return jsonify({'errors': result})

@application.route('/cloudbatchjobinjava/check_syntax_for_onEnd', methods=['POST'])
def check_syntax_for_onEnd():
    data = request.get_json()
    requestid = data['requestid']
    tempPageRequestID = data['tempPageRequestID']
    # get the requestContentInJSON
    requestContentInJSON = ""
    cloudBatchJobrequest = findRequestFromSession(requestid, tempPageRequestID)
    if cloudBatchJobrequest is None:
        return jsonify({'errors': 'No request found'})
    else:
        requestContentInJSON = cloudBatchJobrequest['requestContentInJSON']
        code_for_onEnd = data['code_for_onEnd']
        result = checkSyntax(application, "onEnd", code_for_onEnd, requestid, requestContentInJSON)
        return jsonify({'errors': result})


@application.route('/cloudbatchjobinjava/use-data-streaming/save/<tempPageRequestID>', methods=['POST'])
def use_data_streaming_and_save(tempPageRequestID):
    requestid = request.form['requestid']
    job_alias = request.form['job_alias']

    # get the requestContentInJSON
    requestContentInJSON = ""
    cloudBatchJobrequest = findRequestFromSession(requestid, tempPageRequestID)
    if cloudBatchJobrequest is not None:
        requestContentInJSON = cloudBatchJobrequest['requestContentInJSON']
    else:
        requestContentInJSON = findStreamRequestFromSession(requestid)['REQUEST_CONTENT']
    
    code_for_onStart = request.form['code_for_onStart']
    code_for_onProcess = request.form['code_for_onProcess']
    code_for_onEnd = request.form['code_for_onEnd']

    result = save(requestid, job_alias, requestContentInJSON, code_for_onStart, code_for_onProcess, code_for_onEnd, tempPageRequestID)
    return result



@application.route('/creation/request-new-data-streaming', methods=['POST'])
def request_new_data_streaming():
    if session.get('request-new-data-streaming') is False:
        session['request-new-data-streaming'] = True
        datetimeselectiontype = request.form['datetime-selection-type']
        fromdate = request.form['from-date']
        todate = request.form['to-date']
        fromtime = request.form['from-time']
        totime = request.form['to-time']
        class_code = request.form['class-code']
        fut_opt = request.form['fut-opt']
        expiry_mth = request.form['expiry-mth']
        strike_prc = request.form['strike-prc']
        call_put = request.form['call-put']
        retention_hour = request.form['retention-hour']
        stream_unique_id = str(uuid.uuid1())
        request_newJob(datetimeselectiontype, fromdate, todate, fromtime, totime, class_code, fut_opt, expiry_mth, strike_prc, call_put, retention_hour, stream_unique_id)
        session['request-new-data-streaming'] = False
        get_dataStreamingList("","","","","")
        return redirect(url_for('use_data_streaming', stream_id=stream_unique_id))
    else:
        return "Last request is still in progress"
    

@application.route('/home/use-data-streaming/<stream_id>')
def use_data_streaming(stream_id):
    cloudbatchjobinjava_template = cloudbatchjobinjava(application, stream_id)
    return cloudbatchjobinjava_template
    

@application.route('/home/use-data-streaming/<stream_id>/<cloudbatchjob_id>')
def use_data_streaming_and_edit_program_file(stream_id, cloudbatchjob_id):
    cloudBatchJobrequest = findRequestFromSession(stream_id, cloudbatchjob_id)
    if cloudBatchJobrequest is None:
        return render_template('error.html', error_message="Cloub Batch Job not found")
    else:
        job_alias = cloudBatchJobrequest['ALIAS']
        status = cloudBatchJobrequest['STATUS']
    
    streamRequest = findStreamRequestFromSession(stream_id)
    requestContentInJSON = streamRequest['REQUEST_CONTENT']
    
    cloudbatchjobinjava_template = cloudbatchjobinjava_edit_program_file(application, stream_id, requestContentInJSON, cloudbatchjob_id, job_alias, status)
    return cloudbatchjobinjava_template


@application.route('/home/use-data-streaming/<stream_id>/clone', methods=['POST'])
def use_data_streaming_clone(stream_id):
    job_alias = request.form['job_alias']+"(clone)"
    clone_from = request.form['clone_from']
    code_for_onStart = request.form['code_for_onStart']
    code_for_onProcess = request.form['code_for_onProcess']
    code_for_onEnd = request.form['code_for_onEnd']

    # get the requestContentInJSON
    requestContentInJSON = {}
    streamRequest = findStreamRequestFromSession(stream_id)
    
    # clone the request
    clone_tempPageRequestID = cloneToNewRequest(application, stream_id, streamRequest, code_for_onStart, code_for_onProcess, code_for_onEnd, job_alias)
    return f'/home/use-data-streaming/{stream_id}/{clone_tempPageRequestID}'

    

@application.route('/home/view-cloudbatchjob-result/<stream_id>/<cloudbatchjob_id>')
def view_cloudbatchjob_result(stream_id, cloudbatchjob_id):
    temprequest = findRequestFromSession(stream_id, cloudbatchjob_id)
    if temprequest is None:
        return render_template('error.html', error_message="Cloub Batch Job not found")
    alias = temprequest['ALIAS']
    return render_template('cloudbatchjobresult.html', stream_id=stream_id, cloudbatchjob_id=cloudbatchjob_id, alias=alias)


@application.route('/home/view-cloudbatchjob-result/fetch', methods=['POST'])
def fetch_cloudbatchjob_result():
    data = request.get_json()
    stream_id = data['stream_id']
    cloudbatchjob_id = data['cloudbatchjob_id']
    result = fetch_result(application, stream_id, cloudbatchjob_id)
    return result


@application.route('/home/delete-draft/<cloudbatchjob_id>', methods=['POST'])
def delete_draft(cloudbatchjob_id):
    for i in range(len(session['CloudBatchJobLocalDraft'])):
        for j in range(len(session['CloudBatchJobLocalDraft'][i]['CLOUDBATCHJOBLIST'])):
            if session['CloudBatchJobLocalDraft'][i]['CLOUDBATCHJOBLIST'][j]['ID'] == cloudbatchjob_id:
                del session['CloudBatchJobLocalDraft'][i]['CLOUDBATCHJOBLIST'][j]
                return "Draft deleted successfully"

# Register the function to run before each request
@application.before_request
def before_request():
    if request.endpoint not in ['login', 'static']:
        if request.method not in ['GET', 'POST']:
            return "Method not allowed", 405
        logged_in = check_logged_in_or_not()
        if not logged_in:
            session.clear()
            return redirect(url_for('login'))

if __name__ == '__main__':
    application.run(port=8000, debug=True)
    #application.run(host='0.0.0.0', port=5001, debug=True)