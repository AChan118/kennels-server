import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from views import get_all_animals, create_animal
from urllib.parse import urlparse, parse_qs
from views.animal_requests import delete_animal, get_animals_by_location, get_animals_by_status, get_single_animal, update_animal
from views import get_all_locations, create_location
from views.customer_requests import create_customer, get_all_customers, get_customers_by_email, get_single_customer, update_customer
from views.employee_requests import create_employee, delete_employee, get_employee_by_location, get_single_employee, update_employee
from views import get_all_employees
from views.location_requests import get_single_location, delete_location, update_location

# Here's a class. It inherits from another class.
# For now, think of a class as a container for functions that
# work together for a common purpose. In this case, that
# common purpose is to respond to HTTP requests from a client.


class HandleRequests(BaseHTTPRequestHandler):
    # replace the parse_url function in the class
    def parse_url(self, path):
        """Parse the url into the resource and id"""
        parsed_url = urlparse(path)
        path_params = parsed_url.path.split('/')  # ['', 'animals', 1]
        resource = path_params[1]

        if parsed_url.query:
            query = parse_qs(parsed_url.query)
            return (resource, query)

        pk = None
        try:
            pk = int(path_params[2])
        except (IndexError, ValueError):
            pass
        return (resource, pk)
    # This is a Docstring it should be at the beginning of all classes and functions
    # It gives a description of the class or function

    # Here's a class function

    # Here's a method on the class that overrides the parent's method.
    # It handles any GET request.
    def do_GET(self):
        """Handles GET requests to the server
        """
        # Set the response code to 'Ok'
        self._set_headers(200)
        response = {}  # Default response

        # Parse URL and store entire tuple in a variable
        parsed = self.parse_url(self.path)
        if '?' not in self.path:
            (resource, id) = parsed

            if resource == "animals":
                if id is not None:
                    response = get_single_animal(id)
                    if response is not None:
                        response = get_single_animal(id)
                    else:
                        self._set_headers(404)
                        response = {
                            "message": f"Animal {id} is out playing right now"}

                else:
                    response = get_all_animals()

            elif resource == "locations":
                if id is not None:
                    response = get_single_location(id)

                else:
                    response = get_all_locations()

            elif resource == "employees":
                if id is not None:
                    response = get_single_employee(id)

                else:
                    response = get_all_employees()

            elif resource == "customers":
                if id is not None:
                    response = get_single_customer(id)

                else:
                    response = get_all_customers()
        else:  # There is a ? in the path, run the query param functions
            (resource, query) = parsed

            # see if the query dictionary has an email key
            if query.get('email') and resource == 'customers':
                response = get_customers_by_email(query['email'][0])
            elif query.get('location_id') and resource == 'animals':
                response = get_animals_by_location(query['location_id'][0])
            elif query.get('location_id') and resource == 'employees':
                response = get_employee_by_location(query['location_id'][0])
            elif query.get('status') and resource == 'animals':
                response = get_animals_by_status(query['status'][0])

        self.wfile.write(json.dumps(response).encode())

    # Here's a method on the class that overrides the parent's method.
    # It handles any POST request.
    def do_POST(self):
        self._set_headers(201)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)

        # Convert JSON string to a Python dictionary
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        # Initialize new animal
        new_thing = None

        # Add a new animal to the list. Don't worry about
        # the orange squiggle, you'll define the create_animal
        # function next.
        if resource == "animals":
            if 'name' in post_body and 'breed' in post_body:
                self._set_headers(201)
                new_thing = create_animal(post_body)
            else:
                self._set_headers(400)
                new_thing = {
                    "message": f'{"name is required" if "name" not in post_body else ""} {"breed is required" if "breed" not in post_body else ""}'}

        # Encode the new animal and send in response

        if resource == "locations":
            new_thing = create_location(post_body)

        # Encode the new location and send in response

        if resource == "employees":
            new_thing = create_employee(post_body)

        if resource == "customers":
            new_thing = create_customer(post_body)

        # Encode the new location and send in response
        self.wfile.write(json.dumps(new_thing).encode())

    def do_DELETE(self):
        # Set a 204 response code
        self._set_headers(204)

    # Parse the URL
        (resource, id) = self.parse_url(self.path)

    # Delete a single animal from the list
        if resource == "animals":
            delete_animal(id)

    # Encode the new animal and send in response

        if resource == "location":
            delete_location(id)

        if resource == "employee":
            delete_employee(id)

        if resource == "customer":
            self._set_headers(405)

    # Encode the new animal and send in response
        self.wfile.write("".encode())

    # A method that handles any PUT request.
    def do_PUT(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

    # Parse the URL
        (resource, id) = self.parse_url(self.path)

        success = False

        if resource == "animals":
            success = update_animal(id, post_body)

    # rest of the elif's
        elif resource == "locations":
            success = update_location(id, post_body)

        elif resource == "employee":
            success = update_employee(id, post_body)

        elif resource == "customer":
            success = update_customer(id, post_body)
        if success:
            self._set_headers(204)
        else:
            self._set_headers(404)
        # Encode the new animal and send in response
        self.wfile.write("".encode())

    def _set_headers(self, status):
        # Notice this Docstring also includes information about the arguments passed to the function
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response

        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    # Another method! This supports requests with the OPTIONS verb.
    def do_OPTIONS(self):
        """Sets the options headers
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                         'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Requested-With, Content-Type, Accept')
        self.end_headers()


# This function is not inside the class. It is the starting
# point of this application.
def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()


if __name__ == "__main__":
    main()
