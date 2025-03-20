import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import webbrowser
import os
from PIL import Image, ImageTk


class Book:
    def __init__(self, title, author, isbn, pdf_path=None):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.pdf_path = pdf_path
        self.next = None


class Library:
    def __init__(self):
        self.head = None
        self.undo_stack = []
        self.create_table()

    def connect_db(self):
        return sqlite3.connect("library_management.db")

    def create_table(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT NOT NULL UNIQUE,
            pdf_path TEXT
        );
        '''
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()

    def add_book(self, title, author, isbn):
        # Check if the book with the same ISBN already exists in the database
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books WHERE isbn=?", (isbn,))
        result = cursor.fetchone()
        conn.close()

        # If the ISBN already exists, do not add it to the database
        if result[0] > 0:
            messagebox.showerror("Error", f'Book with ISBN "{isbn}" already exists.')
            return  # ISBN already exists, so we don't add the book again

        # Create a new book in memory (linked list)
        new_book = Book(title, author, isbn)
        if not self.head:
            self.head = new_book
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_book

        # Add the book to the database
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)", (title, author, isbn))
            conn.commit()
            self.undo_stack.append(("add", new_book))
            messagebox.showinfo("Success", f'Book "{title}" added successfully.')
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f'Book with ISBN "{isbn}" already exists.')
        finally:
            conn.close()

    def delete_book(self, isbn):
        # Delete from linked list
        current = self.head
        previous = None
        while current:
            if current.isbn == isbn:
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next

                # Delete from database
                conn = self.connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE isbn=?", (isbn,))
                conn.commit()
                conn.close()

                # Record the undo operation
                self.undo_stack.append(("delete", current))

                messagebox.showinfo("Success", f'Book "{current.title}" deleted successfully.')
                return
            previous = current
            current = current.next
        messagebox.showwarning("Not Found", "Book not found!")

    def upload_pdf(self, isbn):
        # Upload PDF path to the book entry in the database
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books WHERE isbn=?", (isbn,))
        result = cursor.fetchone()
        if result[0] == 0:
            messagebox.showerror("Error", f"Incorrect ISBN: {isbn}. Book not found.")
            return
        pdf_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF Files", "*.pdf")])
        if pdf_path:
            cursor.execute("UPDATE books SET pdf_path=? WHERE isbn=?", (pdf_path, isbn))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f'PDF for book with ISBN "{isbn}" uploaded successfully.')
        else:
            conn.close()

    def view_pdf(self, isbn):
        # Open the PDF if it exists
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT pdf_path FROM books WHERE isbn=?", (isbn,))
        pdf_path = cursor.fetchone()
        conn.close()
        if pdf_path and pdf_path[0]:
            webbrowser.open(pdf_path[0])
        else:
            messagebox.showwarning("Not Found", "No PDF found for this book.")

    def undo(self):
        # Undo the last operation (either add or delete)
        if not self.undo_stack:
            messagebox.showwarning("Undo", "No operations to undo!")
            return

        operation = self.undo_stack.pop()
        if operation[0] == "add":
            self.delete_book(operation[1].isbn)  # Undo add by deleting the book
        elif operation[0] == "delete":
            self.add_book(operation[1].title, operation[1].author,
                          operation[1].isbn)  # Undo delete by re-adding the book

    def view_books(self):
        # Retrieve all books from the database
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, isbn, pdf_path FROM books")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("Books", "No books found.")
            return

        # Create the HTML content with enhanced CSS for stunning 3D effects
        html_content = """
        <html>
        <head>
            <title>Library Books</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
            <style>
                :root {
                    --primary-color: #3498db;
                    --secondary-color: #2ecc71;
                    --background-light: #f4f6f7;
                    --text-dark: #2c3e50;
                    --text-muted: #7f8c8d;
                    --border-radius: 12px;
                    --box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                }

                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                body {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    background: linear-gradient(135deg, var(--background-light) 0%, #e9ecef 100%);
                    color: var(--text-dark);
                    line-height: 1.6;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 2rem;
                }

                .container {
                    width: 100%;
                    max-width: 1200px; /* Updated width */
                    background: white;
                    border-radius: var(--border-radius);
                    box-shadow: var(--box-shadow);
                    overflow: hidden;
                    transition: all 0.3s ease;
                    perspective: 1000px;
                }

                h1 {
                    text-align: center;
                    padding: 2rem 0;
                    background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
                    color: white;
                    margin-bottom: 1rem;
                    font-weight: 600;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }

                .header {
                    display: flex;
                    justify-content: flex-start; /* Align items to the left */
                    padding: 1rem;
                }

                .search-container {
                    flex: 1;
                    text-align: left;
                    margin-right: 20px; /* Space between search bar and table */
                }

                .search-input {
                    padding: 10px;
                    width: 100%; /* Full width of the container */
                    max-width: 400px; /* Optional max width */
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    font-size: 16px;
                }

                table {
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 0 10px;
                    padding: 0 20px;
                }

                th, td {
                    padding: 15px;
                    text-align: left;
                    transition: all 0.3s ease;
                }

                th {
                    background-color: var(--primary-color);
                    color: white;
                    text-transform: uppercase;
                    font-weight: 600;
                    letter-spacing: 1px;
                    position: sticky;
                    top: 0;
                    z-index: 10;
                }

                tr {
                    background-color: white;
                    border-radius: var(--border-radius);
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                    margin 0;
                    -bottom: 10px;
                    transition: all 0.3s ease;
                }

                tr:hover {
                    transform: scale(1.02) translateY(-5px);
                    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
                }

                td {
                    color: var(--text-dark);
                    border-bottom: 1px solid #ecf0f1;
                }

                .pdf-link {
                    display: inline-flex;
                    align-items: center;
                    color: var(--primary-color);
                    text-decoration: none;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    padding: 5px 10px;
                    border-radius: 6px;
                }

                .pdf-link:hover {
                    background-color: rgba(52, 152, 219, 0.1);
                    color: var(--secondary-color);
                    transform: translateX(5px);
                }

                .pdf-icon {
                    width: 20px;
                    height: 20px;
                    margin-right: 8px;
                    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
                }

                @media screen and (max-width: 768px) {
                    .container {
                        margin: 1rem;
                        padding: 0;
                    }

                    table {
                        font-size: 14px;
                        padding: 0 10px;
                    }

                    th, td {
                        padding: 10px;
                    }
                }

                /* Subtle Animations */
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                tr {
                    animation: fadeIn 0.5s ease backwards;
                }

                tr:nth-child(even) {
                    animation-delay: 0.1s;
                }

                tr:nth-child(odd) {
                    animation-delay: 0.2s;
                }
            </style>
            <script>
                function searchBooks() {
                    const input = document.getElementById('isbnSearch').value.toLowerCase();
                    const rows = document.querySelectorAll('table tbody tr');

                    rows.forEach(row => {
                        const isbnCell = row.cells[2].textContent.toLowerCase();
                        if (isbnCell.includes(input)) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    });
                }
            </script>
        </head>
        <body>
            <div class="container">
                <h1>Library Books Collection</h1>
                <div class="header">
                    <div class="search-container">
                        <input type="text" id="isbnSearch" class="search-input" placeholder="Search by ISBN..." onkeyup="searchBooks()">
                    </div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Author</th>
                            <th>ISBN</th>
                            <th>PDF</th>
                        </tr>
                    </thead>
                    <tbody>
            """

        # Add each book to the HTML content with a stylish 3D effect
        for row in rows:
            title, author, isbn, pdf_path = row
            if pdf_path:
                # Use file:// path to create clickable links for PDF files
                pdf_link = f'<a class="pdf-link" href="file://{os.path.abspath(pdf_path)}" target="_blank"><img src="https://img.icons8.com/ios-filled/50/000000/pdf-2.png" class="pdf-icon"/>View PDF</a>'
            else:
                pdf_link = "No PDF available"

            html_content += f"""
            <tr>
                <td>{title}</td>
                <td>{author}</td>
                <td>{isbn}</td>
                <td>{pdf_link}</td>
            </tr>
            """

        # Close the HTML tags
        html_content += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """

        # Save the HTML content to a file
        html_file_path = "books_list.html"
        with open(html_file_path, "w") as file:
            file.write(html_content)

        # Open the HTML file in the default web browser
        webbrowser.open(f"file://{os.path.abspath(html_file_path)}")

    def load_books_from_db(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, isbn, pdf_path FROM books")
        rows = cursor.fetchall()

        for row in rows:
            new_book = Book(row[ 0], row[1], row[2], row[3])
            if not self.head:
                self.head = new_book
            else:
                current = self.head
                while current.next:
                    current = current.next
                current.next = new_book

        conn.close()

    def update_book(self, isbn, title, author, new_isbn):
        # Update the book in the database
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET title=?, author=?, isbn=? WHERE isbn=?",
                       (title, author, new_isbn, isbn))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f'Book with ISBN "{isbn}" updated successfully.')

    def get_book_by_isbn(self, isbn):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, isbn FROM books WHERE isbn=?", (isbn,))
        book = cursor.fetchone()
        conn.close()
        return book if book else None


class LibraryApp:
    def __init__(self, root):
        self.library = Library()
        self.library.load_books_from_db()

        self.window = root
        self.window.title("LIBRARY MANAGEMENT SYSTEM")
        self.window.geometry("1920x1080")
        self.window.config(bg="#f0f0f0")  # Light gray background

        self.create_widgets()

    def create_widgets(self):
        original_image = Image.open("ks.png")  # Replace with your image path
        resized_image = original_image.resize((1495, 200), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(resized_image)

        # Create a label to display the image
        self.image_label = tk.Label(self.window, image=self.image, bg="#f0f0f0")
        self.image_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        self.title_label = tk.Label(self.window, text="LIBRARY MANAGEMENT SYSTEM", font=("Helvetica", 36, "bold"),
                                    bg="#f0f0f0", fg="#333")  # Dark gray text
        self.title_label.grid(row=1, column=0, columnspan=2, pady=20)

        button_frame = tk.Frame(self.window, bg="#f0f0f0")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        self.create_button(button_frame, "Add Book", self.add_book, 0, 0)
        self.create_button(button_frame, "Delete Book", self.delete_book, 0, 1)
        self.create_button(button_frame, "View Books", self.library.view_books, 1, 0)
        self.create_button(button_frame, "Upload PDF", self.upload_pdf, 1, 1)
        self.create_button(button_frame, "View PDF", self.view_pdf, 2, 0)
        self.create_button(button_frame, "Update Book", self.update_book, 2, 1)
        undo_button = tk.Button(button_frame, text="Undo Last Operation", command=self.library.undo, width=20,
                                bg="#007bff", fg="white", font=("Helvetica", 14))
        undo_button.grid(row=3, column=0, columnspan=2, padx=20, pady=10)  # Row 3, spans both columns
        exit_button = tk.Button(button_frame, text="Exit", command=self.window.quit, width=20, bg="#ff4d4d", fg="white",
                                font=("Helvetica", 14))
        exit_button.grid(row=4, column=0, columnspan=2, padx=20, pady=20)

    def create_button(self, parent, text, command, row, column):
        button = tk.Button(parent, text=text, command=command, width=20, bg="#007bff", fg="white", font=("Helvetica", 14))
        button.grid(row=row, column=column, padx=20, pady=10)
        button.bind("<Enter>", lambda e: button.config(bg="#0056b3"))
        button.bind("<Leave>", lambda e: button.config(bg="#007bff"))

    def add_book(self):
        add_book_window = tk.Toplevel(self.window)
        add_book_window.title("Add Book")
        add_book_window.geometry("500x300")
        add_book_window.config(bg="#f0f0f0")

        tk.Label(add_book_window, text="Book Title:", bg="#f0f0f0").pack(pady=5)
        title_entry = tk.Entry(add_book_window, width=30)
        title_entry.pack(pady=5)

        tk.Label(add_book_window, text="Author:", bg="#f0f0f0").pack(pady=5)
        author_entry = tk.Entry(add_book_window, width=30)
        author_entry.pack(pady=5)

        tk.Label(add_book_window, text="ISBN (numbers only):", bg="#f0f0f0").pack(pady=5)


        def validate_isbn_input(P):
            if P == "" or P.isdigit():
                return True
            else:
                return False


        validate_isbn = add_book_window.register(validate_isbn_input)


        isbn_entry = tk.Entry(add_book_window, width=30, validate="key", validatecommand=(validate_isbn, '%P'))
        isbn_entry.pack(pady=5)


        def on_ok():
            title = title_entry.get()
            author = author_entry.get()
            isbn = isbn_entry.get()
            if title and author and isbn:
                self.library.add_book(title, author, isbn)
                add_book_window.destroy()

        # Create OK button
        ok_button = tk.Button(add_book_window, text="OK", command=on_ok, bg="#007bff", fg="white")
        ok_button.pack(pady=20)

        # Create Cancel button
        cancel_button = tk.Button(add_book_window, text="Cancel", command=add_book_window.destroy, bg="#ff4d4d", fg="white")
        cancel_button.pack(pady=5)

    def delete_book(self):
        isbn = simpledialog.askstring("Input", "Enter book ISBN to delete:")
        if isbn:
            self.library.delete_book(isbn)

    def upload_pdf(self):
        isbn = simpledialog.askstring("Input", "Enter book ISBN to upload PDF:")
        if isbn:
            self.library.upload_pdf(isbn)
    def view_pdf(self):
        isbn = simpledialog.askstring("Input", "Enter book ISBN to view PDF:")
        if isbn:
            self.library.view_pdf(isbn)

    def update_book(self):
        isbn = simpledialog.askstring("Input", "Enter book ISBN to update:")
        if isbn:
            # Check if the book exists
            book = self.library.get_book_by_isbn(isbn)
            if book:
                self.update_book_dialog(isbn, book)
            else:
                messagebox.showerror("Error", "Book with this ISBN not found.")

    def update_book_dialog(self, isbn, book):
        # Create a new Toplevel window for updating book details
        update_book_window = tk.Toplevel(self.window)
        update_book_window.title("Update Book")
        update_book_window.geometry("500x300")
        update_book_window.config(bg="#f0f0f0")

        # Create labels and entry fields for title, author, and ISBN
        tk.Label(update_book_window, text="Book Title:", bg="#f0f0f0").pack(pady=5)
        title_entry = tk.Entry(update_book_window, width=30)
        title_entry.insert(0, book[0])  # Pre-fill with current title
        title_entry.pack(pady=5)

        tk.Label(update_book_window, text="Author:", bg="#f0f0f0").pack(pady=5)
        author_entry = tk.Entry(update_book_window, width=30)
        author_entry.insert(0, book[1])  # Pre-fill with current author
        author_entry.pack(pady=5)

        tk.Label(update_book_window, text="ISBN (numbers only):", bg="#f0f0f0").pack(pady=5)


        def validate_isbn_input(P):
            if P == "" or P.isdigit():
                return True
            else:
                return False

        validate_isbn = update_book_window.register(validate_isbn_input)


        isbn_entry = tk.Entry(update_book_window, width=30, validate="key", validatecommand=(validate_isbn, '%P'))
        isbn_entry.insert(0, book[2])
        isbn_entry.pack(pady=5)


        def on_ok():
            title = title_entry.get()
            author = author_entry.get()
            new_isbn = isbn_entry.get()
            if title and author and new_isbn:

                self.library.update_book(isbn, title, author, new_isbn)
                update_book_window.destroy()
            else:
                messagebox.showwarning("Input Error", "Please fill all fields.")

        ok_button = tk.Button(update_book_window, text="OK", command=on_ok, bg="#007bff", fg="white")
        ok_button.pack(pady=20)

        cancel_button = tk.Button(update_book_window, text="Cancel", command=update_book_window.destroy, bg="#ff4d4d", fg="white")
        cancel_button.pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()