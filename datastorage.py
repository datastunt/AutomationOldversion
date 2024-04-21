import time
from datetime import datetime

from mysql import connector


def uncompleted_contact(data):
    connection = connector.connect(host='datastuntstaging.co.in',
                                   user='u385679644_wpautomation',
                                   password='z>P4I+3L/Q2a',
                                   database='u385679644_wpautomation')
    cursor = connection.cursor()
    try:
        connection.start_transaction()

        # Bulk insert data from logs dictionary into MySQL table
        for entry in data:
            job_id = entry.get('jobid')  # Use .get() method to safely retrieve values
            contact_name = entry.get('contact_name')  # Use .get() method to safely retrieve values
            contact_number = entry.get('contact_number')  # Use .get() method to safely retrieve values
            status = entry.get('status')  # Use .get() method to safely retrieve values
            timestamp = entry.get('timestamp')  # Use .get() method to safely retrieve values
            # Example SQL query to insert data into a table named 'automation_progress'
            sql = "INSERT INTO Successfull_jobs (jobid, contact_name, contact_number, status, timestamp) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (job_id, contact_name, contact_number, timestamp, status))

        # Commit changes to the database
        connection.commit()

    except connector.Error as err:
        print("An error occurred during save in database: ", err)
        connection.rollback()

    finally:
        # Close the database connection
        cursor.close()
        connection.close()


def completed_contact(data):
    connection = connector.connect(host='datastuntstaging.co.in',
                                   user='u385679644_wpautomation',
                                   password='z>P4I+3L/Q2a',
                                   database='u385679644_wpautomation')
    cursor = connection.cursor()
    try:
        connection.start_transaction()
        # Iterate over each dictionary in the data list
        for entry in data:
            # Extract values from the dictionary
            job_id = entry.get('jobid')  # Use .get() method to safely retrieve values
            contact_name = entry.get('contact_name')  # Use .get() method to safely retrieve values
            contact_number = entry.get('contact_number')  # Use .get() method to safely retrieve values
            status = entry.get('status')  # Use .get() method to safely retrieve values
            timestamp = entry.get('timestamp')  # Use .get() method to safely retrieve values

            # Example SQL query to insert data into a table named 'automation_status'
            sql = "INSERT INTO Successfull_jobs (jobid, contact_name, contact_number, status, timestamp) VALUES (%s, %s, %s, %s, %s)"
            # Execute the SQL query with values as a tuple
            cursor.execute(sql, (job_id, contact_name, contact_number, timestamp, status))
        # Commit changes to the database
        connection.commit()

    except connector.Error as err:
        # print("An error occurred during save in database:", err)
        connection.rollback()

    finally:
        # Close the database connection
        cursor.close()
        connection.close()


def current_contact_data_status(data):
    # Ensure data is a list of dictionaries
    if isinstance(data, list) and all(isinstance(entry, dict) for entry in data):
        connection = connector.connect(host='datastuntstaging.co.in',
                                       user='u385679644_wpautomation',
                                       password='z>P4I+3L/Q2a',
                                       database='u385679644_wpautomation')
        cursor = connection.cursor()
        try:
            connection.start_transaction()
            # Iterate over each dictionary in the data list
            for entry in data:
                # Extract values from the dictionary
                job_id = entry.get('jobid')  # Use .get() method to safely retrieve values
                contact_name = entry.get('contact_name')  # Use .get() method to safely retrieve values
                contact_number = entry.get('contact_number')  # Use .get() method to safely retrieve values
                status = entry.get('status')  # Use .get() method to safely retrieve values
                timestamp = entry.get('timestamp')  # Use .get() method to safely retrieve values

                # Example SQL query to insert data into a table named 'message_logs'
                sql = "INSERT INTO All_jobs (jobid, contact_name, contact_number, status, timestamp) VALUES (%s, %s, %s, %s, %s)"
                # Execute the SQL query with values as a tuple
                cursor.execute(sql, (job_id, contact_name, contact_number, timestamp, status))
            # Commit changes to the database
            connection.commit()

        except connector.Error as err:
            # print("An error occurred during save in database:", err)
            connection.rollback()

        finally:
            # Close the database connection
            cursor.close()
            connection.close()
    else:
        print("Error: 'data' must be a list of dictionaries.")


def trace_current_status():
    # Connect to the database
    connection = connector.connect(host='datastuntstaging.co.in',
                                   user='u385679644_wpautomation',
                                   password='z>P4I+3L/Q2a',
                                   database='u385679644_wpautomation')
    cursor = connection.cursor(dictionary=True)

    try:
        # Query to fetch the last added data based on timestamp
        sql = "SELECT * FROM All_jobs ORDER BY Timestamp DESC LIMIT 1"

        # Execute the query
        cursor.execute(sql)

        # Fetch the result
        last_added_data = cursor.fetchone()

        return last_added_data

    except connector.Error as err:
        # print("An error occurred while fetching last added contact:", err)
        pass

    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()


import datetime
import time


def job_time():
    current_hour = datetime.datetime.now().strftime('%H:%M:%S')
    target_time_str = "05:00:00"
    before_time_str = "23:59:59"

    # Convert current_hour to datetime object
    current_time = datetime.datetime.strptime(current_hour, "%H:%M:%S")
    # convert before_time_str to object
    before_time = datetime.datetime.strptime(before_time_str, "%H:%M:%S")
    # Convert target_time_str to datetime object
    target_time = datetime.datetime.strptime(target_time_str, "%H:%M:%S")

    # Check if target_time is earlier than current_time
    if before_time < current_time < target_time:
        # Add 1 day to target_time
        print("time to sleep")
        target_time += datetime.timedelta(days=1)
        time_difference = (target_time - current_time).total_seconds()

        # Check if time difference is negative
        if time_difference < 0:
            # Add 24 hours to time difference
            time_difference += 24 * 3600  # 24 hours in seconds
        time.sleep(time_difference)
    else:
        pass
