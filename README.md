# Client Ticketing System

## Abstract

In the realm of customer service and support, effective management of client inquiries and issues is paramount for organizational success. A client ticketing system serves as a structured approach to streamline this process, ensuring timely resolution and customer satisfaction. The system acts as a centralized platform where clients can submit their queries or problems, which are then organized into tickets. Each ticket is assigned a unique identifier and categorized based on priority and type of issue. The ticket is passed on to the consultancy firm where the manager assigns the issue to the developer/consultant. The developer/consultant needs to update the status of the issue to the manager who is further answerable to the client. The system works with the help of Flask and MySQL for database management. By prioritizing efficiency, communication, and data-driven insights, businesses can foster stronger client relationships and achieve operational excellence.


### Instructions:

1. **Abstract:** Provides a concise overview of the project's purpose and functionality.
2. **Features:** Lists key features and capabilities of the system.
3. **Installation:** Provides step-by-step instructions on how to install and set up the project locally.
4. **Usage:** Describes how to use the main functionalities of the application through API endpoints.
5. **Conclusion:** Summarizes the outcome of the project


## Features

- **User Authentication and Authorization:** Implementing secure login mechanisms for clients, managers, and developers/consultants.
- **Database Management:** Utilizing MySQL for efficient data storage and retrieval of ticket information.
- **REST API Development:** Creating RESTful APIs using Python Flask for seamless interaction between the front-end and back-end components.
- **Data Processing:** Employing Pandas and NumPy for data manipulation and analysis.
- **User Interface Design:** Developing an intuitive user interface for clients, managers, and developers/consultants to interact with the system.
- **Notification System:** Implementing email or in-app notifications to inform users of ticket status changes.

## Installation

### Prerequisites

- Python 3.x installed on your system.
- MySQL database (e.g., MySQL Workbench) configured.

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/VanshBajaj24/clientticketingsystem.git
   cd clientticketingsystem

2. Install dependencies using `pip`:

   ```bash
   pip install -r requirements.txt

3. Configure MySQL database:
   - Create a MYSQL database named 'proj'
   - Update 'app.config' in 'app.py' with your MYSQL credentials:

     ```bash
     app.config['MYSQL_HOST'] = 'localhost'
      app.config['MYSQL_USER'] = 'root'
      app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
      app.config['MYSQL_DB'] = 'proj'

4. Run the application:

      ```bash
      python app.py

5. Access the application in your web browser at `http://localhost:5000`.

# Usage

## Registration and Login

- **Register:** Use the `/register` endpoint to create a new user.
- **Login:** Use the `/login` endpoint to authenticate and obtain a session.

## Ticket Management

- **Raise Ticket:** Use the `/raise_ticket` endpoint to create a new ticket.
- **View Tickets:** Use the `/view_tickets` endpoint to view tickets for a logged-in client.
- **Assign Ticket:** Use the `/assign_ticket/<ticket_id>` endpoint to assign a ticket to a consultant (for managers).
- **Update Ticket Status:** Use the `/update_ticket_status/<ticket_id>` endpoint to update ticket status (for consultants and managers).

## Reporting

- **Generate Reports:** Use the `/generate_reports` endpoint to generate various reports based on ticket data (for managers).

## Logout

- **Logout:** Use the `/logout` endpoint to end the session and log out.

# Conclusion

- In conclusion, the Client Ticketing System offers a streamlined approach to managing client inquiries and issues, enhancing efficiency and customer satisfaction through effective communication and timely resolution. Powered by Flask and SQL, it stands poised to support organizational success by prioritizing operational excellence and strong client relationships.
