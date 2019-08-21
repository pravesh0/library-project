from flask import Flask, render_template, flash, redirect, request, url_for, session
import pymysql

# making connection of python file with mysql
connect = pymysql.connect(host="localhost", user="root", passwd="", db="library",
                          use_unicode=True, charset="utf8",cursorclass=pymysql.cursors.DictCursor)
# if cursorclass is not used then the data we fetch will get in tuple form.
cursor = connect.cursor()  # setup of cursor

app = Flask(__name__)  # initializing the Flask class in flask library


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']  # username which will fill by the user in the form.
        password_candidate = request.form['password']   # password get from the form
        data = cursor.execute("select password from librarians where username = %s", args=username)  # taking data from the database related to the username and password
        if data > 0:  # if data exist
             password_in_data = cursor.fetchone()  # fetch the value
             compare_password = 0  # initialize a variable
             for i in password_in_data.values():  # taking the value of password which fetch from database.
                 compare_password = i
             if compare_password == password_candidate:
                 session['logged_in'] = True   # Making session
                 session['username'] = username
                 return render_template('dashboard.html')
             else:
                 flash('Password Invalid')
                 return render_template('login.html')
        else:
            error = 'Username not found'
        return render_template('login.html', error=error)
    return render_template('login.html')

# Further use for searching total books in the library
# @app.route('/total_books')
# def total_books(self):
#     count_books = cursor.execute("select * from books")
#     print("There are " + str(count_books) + " books in stock")
#     book_details = cursor.fetchall()
#     for each_book in book_details:
#         print(each_book.values())


@app.route('/student_details', methods=['GET', 'POST'])
def student_details():
    global name, Roll_no, branch
    if request.method == 'POST':
        roll_no = int(request.form['roll_no'])
        cursor.execute("select * from students where roll_no = %s", args=roll_no)
        details = cursor.fetchone()
        detail = list(details.values())
        name = detail[1]
        Roll_no = detail[0]
        branch = detail[2]
        cursor.execute("select issued.roll_no, issued.book_id, books.name from issued inner join books on "
                       "issued.book_id = books.book_id where return_date = '0000-00-00 00:00:00'")
        books = cursor.fetchall()
        for book in books:
            a = list(book.values())
            if a[0] == roll_no:
                issued_book = a[2]

    return render_template('dashboard.html', n = name, r = Roll_no, b = branch, i = issued_book)

@app.route('/issued_book', methods = ['GET', 'POST'])
def issued_book():
    if request.method == 'POST':
        issued_id = int(request.form['issued_id'])  #there is no default or autoincrement value of issued_id so we have to give it.
        roll_no = int(request.form['roll_no'])
        book_id = int(request.form['book_id'])
        cursor.execute("insert into issued(issued_id, roll_no, book_id) values(%s, %s, %s)", args=(issued_id, roll_no, book_id))
        connect.commit()

    return render_template('dashboard.html'),  flash("Book is Issued Successfully", 'success')

if __name__ == '__main__':
    app.secret_key = 'secret123'  # secret key for making the session secure
    app.run(debug=True)
