import io
import os
import subprocess
import sys
import time
import random
import string
import matplotlib
import pandas as pd
from PIL import Image
from io import BytesIO
from flask import app, Flask
from webdriver_setup import *
from datetime import datetime
from googletrans import Translator
from matplotlib import pyplot as plt
from selenium.webdriver.common.by import By
from urllib3.exceptions import NewConnectionError
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException, NoSuchElementException, TimeoutException
from datastorage import uncompleted_contact, completed_contact, current_contact_data_status, job_time


app = Flask(__name__)
matplotlib.use('Agg')
terminate_flag = False
outer_driver = None
UPLOAD_FOLDER = 'static/uploads'
COMPRESSED_FOLDER = 'static/compressed'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}


def handle_request(request_type):
    try:
        global outer_driver
        if request_type == "take_qr_code_screenshot" and outer_driver is None:
            global_driver = firefox_browser()
            global_driver.get("https://web.whatsapp.com/")
            outer_driver = global_driver
            return outer_driver
        elif request_type == "take_qr_code_screenshot" and outer_driver is not None:
            driver = outer_driver
            return driver
        elif request_type == "run_automation" and outer_driver is not None:
            return outer_driver
        elif request_type == "run_automation" and outer_driver is None:
            global_driver = firefox_browser()
            driver = global_driver
            return driver
        elif request_type == "user_logout" and outer_driver is not None:
            driver = outer_driver
            return driver
        elif request_type == "user_logout" and outer_driver is None:
            global_driver = firefox_browser()
            global_driver.get("https://web.whatsapp.com/")
            driver = global_driver
            return driver
        elif request_type == "check_user" and outer_driver is not None:
            driver = outer_driver
            return driver
        elif request_type == "check_user" and outer_driver is None:
            global_driver = firefox_browser()
            global_driver.get("https://web.whatsapp.com/")
            driver = global_driver
            return driver
        else:
            raise ValueError("Invalid request_type")
    except (InvalidSessionIdException, RecursionError, WebDriverException):
        outer_driver = firefox_browser()
        outer_driver.get("https://web.whatsapp.com/")
        return outer_driver


def take_qr_code_screenshot():
    driver = handle_request("take_qr_code_screenshot")
    time.sleep(5.5)
    try:
        qr_code_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[aria-label='Scan me!']")))
        # Get the location and size of the QR code element
        location = qr_code_element.location
        size = qr_code_element.size

        # Take a screenshot of the QR code area
        qr_code_screenshot = driver.get_screenshot_as_png()
        qr_code_image = Image.open(BytesIO(qr_code_screenshot))
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        qr_code_image = qr_code_image.crop((left, top, right, bottom))

        # Save the image to a file
        qr_code_image_path = "static/whatsapp_qr_code.png"
        qr_code_image.save(qr_code_image_path)
        # Return the path to the image file
        return qr_code_image_path

    except (InvalidSessionIdException, NewConnectionError):
        return take_qr_code_screenshot()
    except TimeoutException:
        driver.delete_all_cookies()
        driver.get("https://web.whatsapp.com/")
    except NoSuchElementException:
        driver.delete_all_cookies()
        driver.get("https://web.whatsapp.com/")
        # Handle the exception by closing the driver and reopening it
    except Exception as e:
        error_msg = f"Error occurred during taking qr code SS: {str(e)}"
        log_error(error_msg)
        try:
            select_user = driver.find_element(By.CSS_SELECTOR,
                                              "div.x10l6tqk.x13vifvy.x17qophe.x78zum5.x6s0dn4.xl56j7k.xh8yej3.x5yr21d.x705qin.xsp8fsz")
            select_user.click()
            time.sleep(1.2)
            login_user = driver.find_element(By.CSS_SELECTOR, "div.xdod15v._ao3e.selectable-text.copyable-text")
            username = login_user.text
            return username
        except:
            driver.get("https://web.whatsapp.com/")



def check_user(session):
    driver = handle_request("check_user")
    try:
        time.sleep(25.5)
        select_user = driver.find_element(By.CSS_SELECTOR,
                                          "div.x10l6tqk.x13vifvy.x17qophe.x78zum5.x6s0dn4.xl56j7k.xh8yej3.x5yr21d.x705qin.xsp8fsz")
        select_user.click()
        time.sleep(1.2)
        login_user = driver.find_element(By.CSS_SELECTOR, "div.xdod15v._ao3e.selectable-text.copyable-text")
        username = session.setdefault('username', []).append(login_user.text)
        return username
    except:
        pass


# To Log out the user,  if user is not logged in then qrcode function is called
def user_logout():
    driver = handle_request("user_logout")
    time.sleep(10.2)
    try:
        select_three_dots = driver.find_element(By.CSS_SELECTOR, 'div[title="Menu"]')
        select_three_dots.click()
        time.sleep(1.5)
        logout_button = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Log out']")
        logout_button.click()
        time.sleep(1.9)
        final_logout = driver.find_element(By.XPATH,
                                           "/html/body/div[1]/div/div/span[2]/div/div/div/div/div/div/div[3]/div/button[2]/div/div")
        final_logout.click()
        user_logout_data = "User logout Successfully"
        return user_logout_data
    except:
        qr_data = take_qr_code_screenshot()
        return qr_data


# This function is to run the job
def run_automation(bulk_file, media, text, session):
    job_time()
    driver = handle_request("run_automation")
    try:
        driver.get("https://web.whatsapp.com/")
        time.sleep(20.5)

        if not terminate_flag:
            if media == "Invalid file format!":
                media = None
            bulk_file_management(driver, bulk_file, media, text, session)
        else:
            sys.exit()
    except Exception as e:
        error_msg = f"Error occurred during opening WhatsApp link: : {str(e)}"
        log_error(error_msg)


def bulk_file_management(driver, bulk_file, media, text, session):
    if bulk_file and not terminate_flag:
        try:
            jobid = generate_job_id()
            bulk_file.save(bulk_file.filename)
            bulk_file = bulk_file.filename
            contacts_list = extracting_contacts(bulk_file)
            contact_persons = len(contacts_list)
            session['contact_persons'] = contact_persons  # Update session data
            contact_count = 1
            for number, name in contacts_list:
                if contact_count == 100:
                    session.clear()
                job_time()
                name = str(name).strip()

                if not terminate_flag:
                    try:
                        time.sleep(float(generate_random_time()))   # random time break before searching name.
                        # Find the search input textbox
                        search_btn = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[title='New chat']")))
                        search_btn.click()
                        time.sleep(2.1)

                        # Find the search box
                        search_input = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[title='Search input textbox']")))
                        search_input.clear()

                        # Input the name into the search input
                        number = str(number)
                        for letter in number:
                            search_input.send_keys(letter)
                            time.sleep(0.1)

                        time.sleep(2.1)

                        try:
                            # Check if contact is unavailable
                            selector = "div.x9f619.x78zum5.xdt5ytf.x6s0dn4.x40yjcy.x2b8uid.x1c4vz4f.x2lah0s.xdl72j9.x1nhvcw1.xt7dq6l.x15uerrv.x13omvei.x1j3kn9t.x1m6arcz > div.x1f6kntn.x1fc57z9.x40yjcy > span._ao3e"
                            select_unavailable_contact = driver.find_element(By.CSS_SELECTOR, selector)
                            condition_text = select_unavailable_contact.text
                            condition = f"No results found for '{name}'"
                            if condition_text == condition:
                                handle_unavailable_contact(driver, name, number, jobid, session)
                            contact_count = contact_count + 1
                        except NoSuchElementException:
                            search_input.send_keys(Keys.ENTER)
                            time.sleep(2.1)
                            if text:
                                handle_text_message(driver, text, name)
                            if media:
                                handle_media(driver, media)
                            handle_send_button(driver, text, media, contact_count)
                            handle_available_contact(name, number, jobid, session)
                            contact_count = contact_count + 1
                        except Exception as e:
                            error_msg = f"Error occurred during searching contact : {str(e)}"
                            log_error(error_msg)
                            pass
                    except Exception as e:
                        handle_error_contact(name, e)
                        continue
                else:
                    sys.exit()
        except Exception as e:
            handle_error_opening_bulk_file(e)
        finally:
            remove_files(bulk_file, media)


def handle_unavailable_contact(driver, name, number, jobid, session):
    back_btn = driver.find_element(By.XPATH,
                                   "//*[@id='app']/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/button")
    back_btn.click()
    timestamp = datetime.now().strftime('%H:%M:%S %d-%m-%Y')
    unavailable_contact_data = {
        'jobid': jobid,
        'contact_name': name,
        'contact_number': number,
        'status': "contact unavailable.",
        'timestamp': timestamp
    }
    current_contact_data_status([unavailable_contact_data])
    uncompleted_contact([unavailable_contact_data])
    session.setdefault('uncompleted_task', []).append(unavailable_contact_data)


def handle_available_contact(name, number, jobid, session):
    timestamp = datetime.now().strftime('%H:%M:%S %d-%m-%Y')
    avlbl_contact_data = {
        'jobid': jobid,
        'contact_name': name,
        'contact_number': number,
        'status': "Message sent successfully.",
        'timestamp': timestamp
    }
    current_contact_data_status([avlbl_contact_data])
    completed_contact([avlbl_contact_data])
    session.setdefault('completed_task', []).append(avlbl_contact_data)


def handle_text_message(driver, text, name):
    select_text_box = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox'][title='Type a message']")))
    select_text_box.click()
    select_text_box.clear()
    if "{name}" in text:
        translator = Translator()
        translated_text = translator.translate(name, src='en', dest='hi')
        user = translated_text.text
        text_data = text.replace("{name}", user)
    else:
        text_data = text
    for msg in text_data:
        select_text_box.send_keys(msg)
        time.sleep(0.1)


def handle_media(driver, media):
    attach_btn = driver.find_element(By.CSS_SELECTOR, "div.x11xpdln.x1d8287x.x1h4ghdb")
    driver.execute_script("arguments[0].click();", attach_btn)
    time.sleep(1.5)

    select_media_input = driver.find_element(By.CSS_SELECTOR,
                                             "input[type='file'][accept='image/*,video/mp4,video/3gpp,video/quicktime']")

    file_name = media
    file_absolute_path = os.path.abspath(os.path.join('static', 'uploads', file_name))
    select_media_input.send_keys(file_absolute_path)


def handle_send_button(driver, text, media, contact_count):
    if text and media or media:
        if contact_count == 1:
            time.sleep(4.5)
            send_button_selector = 'div[aria-label="Send"]'
            send_button = driver.find_element(By.CSS_SELECTOR, send_button_selector)
            send_button.click()
        else:
            time.sleep(2.3)
            send_button_selector = 'span[data-icon="send"]'
            send_button = driver.find_element(By.CSS_SELECTOR, send_button_selector)
            send_button.click()
    elif text and not media:
        time.sleep(1.9)
        send_button_selector = 'button[aria-label="Send"].x1c4vz4f.x2lah0s.xdl72j9.xfect85.x1iy03kw.x1lfpgzf'
        send_button = driver.find_element(By.CSS_SELECTOR, send_button_selector)
        send_button.click()
    time.sleep(1.5)


def handle_error_contact(name, e):
    error_msg = f"Error occurred during processing contact {name}: {str(e)}"
    log_error(error_msg)


def handle_error_opening_bulk_file(e):
    error_msg = f"Error occurred during opening bulk file contact: {str(e)}"
    log_error(error_msg)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def compress_video(input_path, output_path):
    command = f'ffmpeg -i {input_path} -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -b:v 1M {output_path}'
    subprocess.run(command, shell=True)


def upload_file(file):
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        if os.path.getsize(filepath) > 64 * 1024 * 1024:  # Check if file size is greater than 64MB
            compressed_filename = f'compressed_{filename}'
            compressed_filepath = os.path.join(app.config['COMPRESSED_FOLDER'], compressed_filename)
            compress_video(filepath, compressed_filepath)
            return compressed_filename
        else:
            return filename
    else:
        return 'Invalid file format!'


def remove_files(bulk_file, media):
    os.remove(bulk_file)
    if media:
        file_absolute_path = os.path.abspath(os.path.join('static', 'uploads', media))
        os.remove(file_absolute_path)


# this function is used to extract contact name and number from uploaded excel
def extracting_contacts(bulk_file):
    try:
        # Read the Excel file
        all_sheets_data = pd.read_excel(bulk_file, sheet_name=None)
        contacts_list = []

        # Iterate through all sheets and extract contacts
        for sheet_name, sheet_data in all_sheets_data.items():
            if sheet_data is not None and not sheet_data.empty:
                for index, row in sheet_data.iterrows():
                    # Extract the contact information (assuming 'Number' and 'Name' are column names)
                    contacts_list.append((row['Number'], row['Name']))

        return contacts_list
    except Exception as e:
        # Handle any exceptions
        error_msg = f"Error occurred during contact extraction: {str(e)}"
        log_error(error_msg)
        return []


# Function to log errors
def log_error(error_msg):
    with open('error_log.txt', 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{timestamp}: {error_msg}\n')


# To kill Automation
def kill_automation():
    global terminate_flag
    terminate_flag = True
    return terminate_flag


def generate_random_time():
    seconds_list = [1, 2, 3, 4, 5]
    li_item = random.choice(seconds_list)
    sequence = [f'{li_item}.{i}' for i in range(li_item, 11)]
    random_time = random.choice(sequence)
    return random_time


# TO generate job ID
def generate_job_id():
    alphabet = string.ascii_uppercase
    current_date = datetime.now().strftime('%d-%m-%Y')  # Get current date
    random_string = ''.join(random.choices(alphabet, k=6))  # Generate a random string of alphabets
    job_id = f"JOB-{current_date}-{random_string}"  # Combine current date and random string
    return job_id


# to generate pdf from the output of html table
def generate_pdf(df):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)  # Adjust font size as needed
    table.scale(1, 1.5)  # Adjust table scale for better fit in PDF
    # Save the figure as a PDF to a bytes buffer
    pdf_output = io.BytesIO()
    plt.savefig(pdf_output, format='pdf', bbox_inches='tight')
    pdf_output.seek(0)
    plt.close(fig)
    return pdf_output.getvalue()


# This function is triggered when user click for vcf conversion
def create_vcf(input_excel):
    try:
        # Read Excel file into DataFrame
        df = pd.read_excel(input_excel, dtype={'Number': str})  # Force 'Number' column to be read as string

        # Create output directory for vCards
        output_dir = "vcards"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        vcf_paths = []

        # Iterate over rows in the DataFrame
        for index, row in df.iterrows():
            # Split the name based on the last space
            name_parts = str(row["Name"]).rsplit(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''  # Extract last name if available

            # Create vCard content for the current row
            vcard_content = f'BEGIN:VCARD\n'
            vcard_content += f'VERSION:2.1\n'
            vcard_content += f'N:{last_name};{first_name}\n' if last_name else f'N:;{first_name}\n'
            vcard_content += f'FN:{first_name} {last_name}\n' if last_name else f'FN:{first_name}\n'
            vcard_content += f'TEL;CELL;VOICE:{row["Number"]}\n'
            vcard_content += f'REV:{pd.Timestamp.now().strftime("%Y%m%dT%H%M%SZ")}\n'
            vcard_content += f'END:VCARD\n'

            # Define output vCard file path based on the person's name
            if last_name:
                output_vcf = os.path.join(output_dir, f'{first_name} {last_name}.vcf')
            else:
                output_vcf = os.path.join(output_dir, f'{first_name}.vcf')

            # Write vCard content to file
            with open(output_vcf, 'w', encoding='utf-8') as vcf_file:
                vcf_file.write(vcard_content)

            vcf_paths.append(output_vcf)  # Append the path to the list of VCF paths

        # Return the list of generated vCard file paths
        return vcf_paths
    except Exception as e:
        error_msg = f"Error occurred during converting vcf : {str(e)}"
        log_error(error_msg)  # Make sure log_error function is properly implemented
        raise  # Reraise the exception for further handling or debugging
