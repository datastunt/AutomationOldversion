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
            job_id = entry['JobID']
            contact = entry['contact']
            reason = entry['reason']
            timestamp = entry['timestamp']
            # Example SQL query to insert data into a table named 'automation_progress'
            sql = "INSERT INTO automation_progress (JobID, Contact, Reason, Timestamp) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (job_id, contact, reason, timestamp))

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
            job_id = entry['JobID']
            contact = entry['contact']
            status = entry['status']
            timestamp = entry['timestamp']

            # Example SQL query to insert data into a table named 'automation_status'
            sql = "INSERT INTO automation_status (JobID, contact_number, Timestamp, Status) VALUES (%s, %s, %s, %s)"
            # Execute the SQL query with values as a tuple
            cursor.execute(sql, (job_id, contact, timestamp, status))
        # Commit changes to the database
        connection.commit()

    except connector.Error as err:
        print("An error occurred during save in database:", err)
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
                job_id = entry.get('JobID')  # Use .get() method to safely retrieve values
                contact = entry.get('contact')  # Use .get() method to safely retrieve values
                status = entry.get('status')  # Use .get() method to safely retrieve values
                timestamp = entry.get('timestamp')  # Use .get() method to safely retrieve values

                # Example SQL query to insert data into a table named 'message_logs'
                sql = "INSERT INTO message_logs (JobID, Contact_name, Timestamp, status) VALUES (%s, %s, %s, %s)"
                # Execute the SQL query with values as a tuple
                cursor.execute(sql, (job_id, contact, timestamp, status))
            # Commit changes to the database
            connection.commit()

        except connector.Error as err:
            print("An error occurred during save in database:", err)
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
        sql = "SELECT * FROM automation_status ORDER BY Timestamp DESC LIMIT 1"

        # Execute the query
        cursor.execute(sql)

        # Fetch the result
        last_added_data = cursor.fetchone()

        return last_added_data

    except connector.Error as err:
        print("An error occurred while fetching last added contact:", err)

    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()


