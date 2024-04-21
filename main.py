import shutil
import zipfile
from engine import *
from flask import Flask, render_template, request, Response, send_file, jsonify, session

app = Flask(__name__)
app.secret_key = '@wpAutomation321'


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/automation", methods=['POST'])
def automation():
    session.clear()
    # media = request.files.get('media_content')
    video = request.files.get('video_content')
    video = upload_file(video)
    text = request.form.get('message')
    bulk_file = request.files.get('bulkFile')
    run_automation(bulk_file, video, text, session)
    completed_task = session.get('completed_task', [])
    uncompleted_task = session.get('uncompleted_task', [])
    contact_persons = session.get('contact_persons', [])
    result = {
        'completed_task': completed_task,
        'uncompleted_task': uncompleted_task,
        'contact_persons': contact_persons
    }
    return render_template('logs_table.html', result=result)


@app.route("/qrcode", methods=['GET'])
def get_qrcode_scanner():
    qrcode = take_qr_code_screenshot()
    return jsonify({'qrcode': qrcode})


@app.route("/checker", methods=['GET'])
def checker():
    check_user(session)
    user = session.get('username', [])
    return jsonify({"user": user})


@app.route("/logout", methods=['GET'])
def logout():
    user_logout()
    return render_template('index.html')


@app.route("/kill_automation", methods=['GET'])
def kill_automation_route():
    kill_automation()
    return render_template('index.html')


@app.route('/download_pdf')
def download_pdf():
    completed_task = session.get('completed_task', [])
    uncompleted_task = session.get('uncompleted_task', [])
    # data = {'completed_job': completed_task, 'uncompleted_job': uncompleted_task, "contacts": contact_persons}
    # Combine completed and uncompleted job data
    main_data = {'Done task': completed_task, 'Undone task': uncompleted_task}
    # Efficient DataFrame creation
    rows = []
    for key, values in main_data.items():
        for item in values:
            rows.append({
                'jobid': item['jobid'],
                'contact_name': item['contact_name'],
                'contact_number': item['contact_number'],  # Use 'Undone' for tasks without a 'status'
                'status': item['status'],
                'timestamp': item['timestamp']
            })
    df = pd.DataFrame(rows)
    # Generate PDF
    pdf = generate_pdf(df)
    # Set up response
    response = Response(
        pdf,
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=data.pdf'}
    )
    return response


@app.route("/download-vcf", methods=["POST"])
def download_vcf():
    try:
        excel_file = request.files.get('excelFile')
        vcf_paths = create_vcf(excel_file)

        if vcf_paths:
            # Create an in-memory zip file to store the VCFs
            zip_buffer = (io.BytesIO())
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for vcf_path in vcf_paths:
                    zip_file.write(vcf_path, os.path.basename(vcf_path))

            # Move to the beginning of the buffer before sending
            zip_buffer.seek(0)

            # Send the zip file as an attachment
            response = send_file(zip_buffer, as_attachment=True, download_name='vcards.zip')
            # Empty the vcards directory
            shutil.rmtree('vcards')
            os.makedirs('vcards')  # Recreate the empty directory
            return response
        else:
            return "Error generating vCard files", 500
    except Exception as e:
        error_msg = f"Error occurred during downloading vcf : {str(e)}"
        log_error(error_msg)
        pass


if __name__ == "__main__":
    # Get the port from the environment variable, defaulting to 8080 if not set
    app.run(port=8080, host="0.0.0.0")
