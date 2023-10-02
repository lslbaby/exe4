import sqlite3

# Create a connection and cursor
connection = sqlite3.connect('library.db')
cursor = connection.cursor()

# Create Books table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        BookID TEXT PRIMARY KEY,
        Title TEXT,
        Author TEXT,
        ISBN TEXT,
        Status TEXT
    )
''')

# Create Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        UserID TEXT PRIMARY KEY,
        Name TEXT,
        Email TEXT
    )
''')

# Create Reservations table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservations (
        ReservationID INTEGER PRIMARY KEY AUTOINCREMENT,
        BookID TEXT,
        UserID TEXT,
        ReservationDate TEXT,
        FOREIGN KEY (BookID) REFERENCES Books(BookID),
        FOREIGN KEY (UserID) REFERENCES Users(UserID)
    )
''')

# Function to add a new book to the database
def add_book():
    book_id = input('Enter BookID: ')
    title = input('Enter Title: ')
    author = input('Enter Author: ')
    isbn = input('Enter ISBN: ')
    status = input('Enter Status: ')
    
    cursor.execute('''
        INSERT INTO Books (BookID, Title, Author, ISBN, Status)
        VALUES (?, ?, ?, ?, ?)
    ''', (book_id, title, author, isbn, status))
    
    connection.commit()
    print('Book added successfully.')

# Function to find a book's details based on BookID
def find_book_details_by_id():
    book_id = input('Enter BookID: ')
    
    cursor.execute('''
        SELECT Books.*, Users.Name, Users.Email
        FROM Books
        LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
        LEFT JOIN Users ON Reservations.UserID = Users.UserID
        WHERE Books.BookID = ?
    ''', (book_id,))
    
    result = cursor.fetchone()
    
    if result is not None:
        print('Book ID:', result[0])
        print('Title:', result[1])
        print('Author:', result[2])
        print('ISBN:', result[3])
        print('Status:', result[4])
        
        if result[5] is not None:
            print('Reserved by:', result[5])
            print('User Name:', result[6])
            print('User Email:', result[7])
    else:
        print('Book not found.')

# Function to find a book's reservation status based on given input
def find_reservation_status(input_text):
    if input_text.startswith('LB'):
        # Searching by BookID
        cursor.execute('''
            SELECT Books.Status, Users.Name, Users.Email
            FROM Books
            LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
            LEFT JOIN Users ON Reservations.UserID = Users.UserID
            WHERE Books.BookID = ?
        ''', (input_text,))
        
        result = cursor.fetchone()
        
        if result is not None:
            print('Book Status:', result[0])
            
            if result[0] == 'Reserved':
                print('Reserved by:', result[1])
                print('User Email:', result[2])
        else:
            print('Book not found.')
    elif input_text.startswith('LU'):
        # Searching by UserID
        cursor.execute('''
            SELECT Books.Title, Books.Status
            FROM Books
            JOIN Reservations ON Books.BookID = Reservations.BookID
            JOIN Users ON Reservations.UserID = Users.UserID
            WHERE Users.UserID = ?
        ''', (input_text,))
        
        result = cursor.fetchall()
        
        if result:
            for row in result:
                print('Book Title:', row[0])
                print('Book Status:', row[1])
        else:
            print('No reservations found for the user.')
    elif input_text.startswith('LR'):
        # Searching by ReservationID
        cursor.execute('''
            SELECT Books.Title, Books.Status, Users.Name
            FROM Books
            JOIN Reservations ON Books.BookID = Reservations.BookID
            JOIN Users ON Reservations.UserID = Users.UserID
            WHERE Reservations.ReservationID = ?
        ''', (input_text,))
        
        result = cursor.fetchone()
        
        if result is not None:
            print('Book Title:', result[0])
            print('Book Status:', result[1])
            print('Reserved by:', result[2])
        else:
            print('Reservation not found.')
    else:
        # Searching by Title
        cursor.execute('''
            SELECT Books.BookID, Books.Status, Users.Name, Users.Email
            FROM Books
            LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
            LEFT JOIN Users ON Reservations.UserID = Users.UserID
            WHERE Books.Title = ?
        ''', (input_text,))
        
        result = cursor.fetchall()
        
        if result:
            for row in result:
                print('Book ID:', row[0])
                print('Book Status:', row[1])
                
                if row[1] == 'Reserved':
                    print('Reserved by:', row[2])
                    print('User Email:', row[3])
        else:
            print('Book not found.')

# Function to find all the books in the database
def find_all_books():
    cursor.execute('''
        SELECT Books.*, Users.Name, Users.Email
        FROM Books
        LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
        LEFT JOIN Users ON Reservations.UserID = Users.UserID
    ''')
    
    result = cursor.fetchall()
    
    if result:
        for row in result:
            print('Book ID:', row[0])
            print('Title:', row[1])
            print('Author:', row[2])
            print('ISBN:', row[3])
            print('Status:', row[4])
            
            if row[5] is not None:
                print('Reserved by:', row[5])
                print('User Name:', row[6])
                print('User Email:', row[7])
            
            print('----------------------------------------')
    else:
        print('No books found.')

# Function to modify/update book details
def modify_book_details():
    book_id = input('Enter BookID: ')
    
    cursor.execute('SELECT * FROM Books WHERE BookID = ?', (book_id,))
    book = cursor.fetchone()
    
    if book is not None:
        new_title = input('Enter new Title (leave blank to skip): ')
        new_author = input('Enter new Author (leave blank to skip): ')
        new_isbn = input('Enter new ISBN (leave blank to skip): ')
        new_status = input('Enter new Status (Reserved/Available) (leave blank to skip): ')
        
        if new_title:
            cursor.execute('UPDATE Books SET Title = ? WHERE BookID = ?', (new_title, book_id))
        if new_author:
            cursor.execute('UPDATE Books SET Author = ? WHERE BookID = ?', (new_author, book_id))
        if new_isbn:
            cursor.execute('UPDATE Books SET ISBN = ? WHERE BookID = ?', (new_isbn, book_id))
        
        if new_status:
            cursor.execute('UPDATE Books SET Status = ? WHERE BookID = ?', (new_status, book_id))
            cursor.execute('''
                UPDATE Reservations SET ReservationDate = ? WHERE BookID = ?
            ''', ('' if new_status == 'Available' else '2023-10-02', book_id))
        
        connection.commit()
        print('Book details updated successfully.')
    else:
        print('Book not found.')

# Function to delete a book
def delete_book():
    book_id = input('Enter BookID: ')
    
    cursor.execute('SELECT * FROM Books WHERE BookID = ?', (book_id,))
    book = cursor.fetchone()
    
    if book is not None:
        cursor.execute('DELETE FROM Books WHERE BookID = ?', (book_id,))
        
        if book[4] == 'Reserved':
            cursor.execute('DELETE FROM Reservations WHERE BookID = ?', (book_id,))
        
        connection.commit()
        print('Book deleted successfully.')
    else:
        print('Book not found.')

# Main program loop
while True:
    print('1. Add a new book to the database')
    print('2. Find a book\'s detail based on BookID')
    print('3. Find a book\'s reservation status based on BookID, Title, UserID, and ReservationID')
    print('4. Find all the books in the database')
    print('5. Modify/update book details based on BookID')
    print('6. Delete a book based on BookID')
    print('7. Exit')
    
    choice = input('Enter your choice: ')
    
    if choice == '1':
        add_book()
    elif choice == '2':
        find_book_details_by_id()
    elif choice == '3':
        input_text = input('Enter BookID, Title, UserID, or ReservationID: ')
        find_reservation_status(input_text)
    elif choice == '4':
        find_all_books()
    elif choice == '5':
        modify_book_details()
    elif choice == '6':
        delete_book()
    elif choice == '7':
        break
    else:
        print('Invalid choice. Please try again.')

# Close the connection
connection.close()
