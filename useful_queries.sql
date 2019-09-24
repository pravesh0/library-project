-- To find the list of all the students with f_days till today ( one roll_no may have multiple records)
select roll_no, book_id, issued_date, return_date,
case
	when return_date = '0000-00-00 00:00:00' then
		case
			when datediff(now(), issued_date) > 15 then
				datediff(now(), issued_date) - 15
			else 
				0
        end
        
	when datediff(return_date, issued_date) > 15 then
		datediff(return_date, issued_date) - 15
	else
		0

end as f_days

from issued;




-- Selects the rollno with their corresponding sum of fine days (f_days)
select roll_no, sum(f_days)
from 
(select roll_no, book_id, issued_date, return_date,
case
	when return_date = '0000-00-00 00:00:00' then
		case
			when datediff(now(), issued_date) > 15 then
				datediff(now(), issued_date) - 15
			else 
				0
        end
        
	when datediff(return_date, issued_date) > 15 then
		datediff(return_date, issued_date) - 15
	else
		0

end as f_days

from issued) as fine
group by roll_no;



-- for new book issuing
insert into issued (roll_no, book_id) values ('any-value', 'any-value') ;


-- when returning the book
update issued set return_date= now()
where roll_no = 10144 and book_id = 20143 and return_date = '0000-00-00 00:00:00';


-- when re-issuing the book ( both query should be executed sequentially)
update issued set return_date=now()
where roll_no = 10144 and book_id = 20143 and return_date = '0000-00-00 00:00:00';
insert into issued (roll_no, book_id) values (10144, 20143);


-- when adding new librarian
insert into librarians ( username , password, name, email) values ( 'username', 'password', 'name', 'email');


-- when adding new student 
insert into students (name, course, sem, email, phone) values ();


-- when adding a new book to the library
insert into books (name, subject, author, stock) values ();
