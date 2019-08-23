from flask import Flask, render_template, flash, redirect, request, session
import pymysql

fine_query = """select students.roll_no, students.name, students.course, students.sem, f.fine
            from students
            left join 
            (
            select roll_no, sum(t_fine) as fine
            from 
            (select roll_no, book_id, issued_date, return_date,
            case
                when return_date = '0000-00-00 00:00:00' then
                    case
                        when datediff(now(), issued_date) > 15 then
                            (datediff(now(), issued_date) - 15)*5
                        else                            0
                    end    
                when datediff(return_date, issued_date) > 15 then
                    (datediff(return_date, issued_date) - 15)*5
                else
                    0 
            end as t_fine
            from issued) as fine_total
            group by roll_no
            ) as f
             on students.roll_no = f.roll_no;
"""


conn = pymysql.connect(host="localhost", user="root", passwd="root", db="library",
                       use_unicode=True, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
# if cursorclass is not used then the data we fetch will get in tuple form.
cursor = conn.cursor()  # setup of cursor

app = Flask(__name__)  # initializing the Flask class in flask library


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']  # username which will fill by the user in the form.
        password_candidate = request.form['password']  # password get from the form
        sql = "select password from librarians where username = %s"
        data = cursor.execute(sql, args=username)  # taking data from the database related to the username and password
        if data == 1:  # if username is correct
            password_in_data = cursor.fetchone()  # fetch the value
            compare_password = password_in_data['password']
            if compare_password == password_candidate:
                session['logged_in'] = True  # Making session
                session['username'] = username
                return render_template('dashboard.html')
            else:
                flash('Invalid Password!')
                flash('Please Try Again!')
                return render_template('login.html')
        else:   # if username is incorrect
            flash(u"Invalid Username!", 'error')
            flash("Please Try Again!")
            return render_template('login.html', )
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        return render_template('dashboard.html')


@app.route('/student_details', methods=['GET', 'POST'])
def student_details():
    if request.method == 'POST':
        try:
            form_roll_no = int(request.form['roll_no'])
            n = cursor.execute("select * from students where roll_no = %s", args=form_roll_no)
            if n > 0:
                details = cursor.fetchone()
                detail = list(details.values())
                name = detail[1]
                Roll_no = detail[0]
                branch = detail[2]
                sql = "select issued.roll_no, issued.book_id, books.name from issued inner join books on " \
                      "issued.book_id = books.book_id where return_date = '0000-00-00 00:00:00'"
                cursor.execute(sql)
                books = cursor.fetchall()
                issued_book = []
                cursor.execute(fine_query)
                data = cursor.fetchall()
                s_fine = 0
                for d in data:
                    if d['roll_no'] == form_roll_no:
                        s_fine = d['fine']
                if books:
                    print(books)
                    for book in books:
                        a = list(book.values())
                        if a[0] == form_roll_no:
                            issued_book.append(a[2])

                return render_template('dashboard.html', n=name, r=Roll_no, branch=branch, i=issued_book, bo=books, f=s_fine)
            else:
                flash(" doesn't exist!")
                error = 'Invalid RollNo'
                return render_template('dashboard.html', error=error, rn=form_roll_no)
        except Exception:
            flash("Please Enter a valid number.")
            error = 'except'
            return render_template('dashboard.html', error=error,)


@app.route('/issued_book', methods=['GET', 'POST'])
def issued_book():
    if request.method == 'POST':

        try:
            roll_no = int(request.form['roll_no'])
            book_id = int(request.form['book_id'])
            duplicate = cursor.execute("select * from issued where roll_no = %s and book_id = %s and return_date= '0000-00-00 00:00:00'", args=(roll_no, book_id))
            rows = 0
            if duplicate == 0:
                rows = cursor.execute("insert into issued(roll_no, book_id) values(%s, %s)",
                       args=(roll_no, book_id))
        except Exception:
            rows = 0
            duplicate = 0
        finally:
            conn.commit()
            if rows == 1:
                return render_template('dashboard.html', b=book_id, rn=roll_no, s='success in issuing')
            else:
                return render_template('dashboard.html', s='error in issuing')


@app.route('/reissue_book', methods=['GET', 'POST'])
def reissue_book():
    if request.method == 'POST':
        try:
            roll_no = int(request.form['roll_no'])
            book_id = int(request.form['book_id'])
            sql = "update issued set return_date=now() where roll_no = %s and book_id = %s and return_date = '0000-00-00 00:00:00'"
            row = cursor.execute(sql, args=(roll_no, book_id))
            sql = "insert into issued (roll_no, book_id) values (%s, %s)"
            cursor.execute(sql, args=(roll_no, book_id))

            conn.commit()
        except Exception:
            row = 0
        finally:
            if row==1:
                return render_template('dashboard.html', s='success in reissuing', b=book_id, rn=roll_no)
            else:
                return render_template('dashboard.html', s='error in reissuing')

    return render_template('dashboard.html')


@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        try:
            roll_no = int(request.form['roll_no'])
            book_id = int(request.form['book_id'])
            print(roll_no, book_id)
            sql = "update issued set return_date=now() where roll_no = %s and book_id = %s and return_date = '0000-00-00 00:00:00'"
            row = cursor.execute(sql, args=(roll_no, book_id))
            conn.commit()

        except Exception:
            row = 0
        finally:
            if row==1:
                return render_template('dashboard.html', s='success in returning', b=book_id, rn=roll_no)
            else:
                return render_template('dashboard.html', s='error in returning')



@app.route('/fine', methods=['GET', 'POST'])
def fine():
    if request.method == 'POST':
        cursor.execute(fine_query)
        data = cursor.fetchall()
        return render_template('fine_data.html', d=data)


@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        cursor.execute('select * from books')
        data = cursor.fetchall()
        return render_template('books.html', d=data)


@app.route('/total_issues', methods=['GET', 'POST'])
def total_issues():
    if request.method == 'POST':
        sql = """select issued.roll_no, issued.book_id, books.name as book_name, students.name as student_name from
              issued inner join books on issued.book_id = books.book_id inner join students on 
              students.roll_no = issued.roll_no where return_date = '0000-00-00 00:00:00'"""
        cursor.execute(sql)
        data = cursor.fetchall()
        return render_template('total_issues.html', d=data)


if __name__ == '__main__':
    app.secret_key = 'secret123'  # secret key for making the session secure
    app.run(debug=True)
