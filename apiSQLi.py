from flask import Flask, jsonify, request, render_template
import pyodbc

server_name = "XXXXXXXXXXXXXXXXXXXX.database.windows.net"
database_name = "XXXXXXXXXXXXXXXXXXXX"
username = "XXXXXXXXXXXXXXXXXXXX"
password = "XXXXXXXXXXXXXXXXXXXX"
odbc_driver = "/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.0.so.1.1"
conn = pyodbc.connect(f"DRIVER={odbc_driver};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password}")

app = Flask(__name__)
    
@app.route('/vulnerable', methods=['GET', 'POST'])
def vulnerable():
    if request.method == 'POST':
        search_term = request.form['search_term']
        if not search_term:
            return "Please enter a search term", 400
        cursor = conn.cursor()
        query = "SELECT * FROM XXXXXXXXXXXXXXXXXXXX WHERE ProductID LIKE '%" + search_term + "%'"
        cursor.execute(query)
        results = cursor.fetchall()
        return render_template('results.html', results=results)
    else:
        return render_template('vulnerable.html')

# Here are the changes:
#
#    The input validation checks whether the search_term parameter is a valid integer value. If it is not, the function returns a 400 Bad Request response with an error message.
#    The query string now uses a placeholder (?) instead of string concatenation to indicate the position of the parameter in the query.
#    The execute method now takes a tuple of parameter values as its second argument, and passes ('%' + search_term + '%',) as the parameter value. This ensures that the parameter is properly sanitized and validated as a string value.
#    The function now returns a rendered template with the results of the query.
#
# With these changes, the function now uses parameterized queries to prevent SQL injection attacks, and input validation to ensure that the search_term parameter is a valid integer value.


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_term = request.form['search_term']
        if not search_term.isdigit():
            return "Invalid input: 'search_term' must be an integer", 400
        cursor = conn.cursor()
        query = "SELECT * FROM XXXXXXXXXXXXXXXXXXXX WHERE ProductID LIKE ?"
        cursor.execute(query, ('%' + search_term + '%',))
        results = cursor.fetchall()
        return render_template('results.html', results=results)
    else:
        return render_template('home.html')

# In this example, the id value is concatenated directly into the SQL query string. 
# This approach is vulnerable to SQL injection attacks because an attacker could inject SQL code 
# by manipulating the id value. 
# curl http://127.0.0.1:5000/vulnerable_query?id=9

@app.route('/query')
def query():
    id = request.args.get('id')
    cursor = conn.cursor()
    query = "SELECT * FROM XXXXXXXXXXXXXXXXXXXX WHERE AddressID = ?"
    cursor.execute(query, id)
    results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    return jsonify(results)

# In this example, the id value is concatenated directly into the SQL query string. 
# This approach is vulnerable to SQL injection attacks because an attacker could inject SQL code 
# by manipulating the id value. 
# curl http://127.0.0.1:5000/vulnerable_query?id=9
# http://127.0.0.1:5000/vulnerable_query?id=1 OR 1=1 --

@app.route('/vulnerable_query')
def vulnerable_query():
    id = request.args.get('id')
    cursor = conn.cursor()
    query = "SELECT * FROM XXXXXXXXXXXXXXXXXXXX WHERE AddressID = %s" % id
    cursor.execute(query)
    results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    return jsonify(results)


# Here are the changes:
#
#    The function name has been changed to secure_query, to reflect the fact that it is now using parameterized queries and input validation.
#    The input validation checks whether the id parameter is a valid integer value. If it is not, the function returns a 400 Bad Request response with an error message.
#    The query string now uses a placeholder (?) instead of %s to indicate the position of the parameter in the query.
#    The execute method now takes a tuple of parameter values as its second argument, and passes (id,) as the parameter value. This ensures that the parameter is properly sanitized and validated as an integer value.
#    The function now returns a JSON response with the results of the query.
#
#With these changes, the function now uses parameterized queries to prevent SQL injection attacks, and input validation to ensure that the id parameter is a valid integer value.
# http://localhost:5000/secure_query?id=9

@app.route('/secure_query')
def secure_query():
    id = request.args.get('id')
    if not id.isdigit():
        return "Invalid input: 'id' must be an integer", 400
    cursor = conn.cursor()
    query = "SELECT * FROM XXXXXXXXXXXXXXXXXXXX WHERE AddressID = ?"
    cursor.execute(query, (id,))
    results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    return jsonify(results)


@app.route('/test') # http://127.0.0.1:5000/test
def test_database():
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    return 'Database connection test successful. Result: {}'.format(result[0])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)