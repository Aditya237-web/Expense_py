from flask import Flask, request, redirect, url_for
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# Function to connect to the database
def connect_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="1234",  # Replace with your MySQL password
        database="expense_tracker"
    )
    conn.cursor().execute('''CREATE TABLE IF NOT EXISTS expenses (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                amount DECIMAL(10,2),
                                category VARCHAR(255),
                                date DATE)''')
    conn.commit()
    return conn

# Home route to display expenses and total spending
@app.route('/')
def home():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_spending = cursor.fetchone()[0] or 0  # Default to 0 if no expenses
    conn.close()

    # Inline HTML content
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Expense Tracker</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; margin: 0; padding: 0; }}
            header {{ background-color: #4CAF50; color: white; padding: 1rem; text-align: center; }}
            main {{ padding: 2rem; }}
            h1, h2 {{ text-align: center; }}
            form {{ display: flex; flex-direction: column; gap: 1rem; max-width: 400px; margin: 0 auto; }}
            input {{ padding: 0.5rem; border: 1px solid #ccc; border-radius: 5px; }}
            button {{ padding: 0.5rem; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background-color: #45a049; }}
            table {{ margin: 2rem auto; width: 80%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
            .total-spending, .clear-expenses {{ text-align: center; margin-top: 2rem; font-size: 1.2rem; }}
        </style>
    </head>
    <body>
        <header>
            <h1>💰 Expense Tracker</h1>
        </header>
        <main>
            <!-- Add Expense Form -->
            <section>
                <h2>Add New Expense</h2>
                <form action="/add_expense" method="POST">
                    <label for="amount">Amount (₹):</label>
                    <input type="number" name="amount" id="amount" step="0.01" required>
                    <label for="category">Category:</label>
                    <input type="text" name="category" id="category" required>
                    <button type="submit">Add Expense</button>
                </form>
            </section>

            <!-- Expense List -->
            <section>
                <h2>Expense List</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Amount (₹)</th>
                            <th>Category</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    if expenses:  # If expenses exist, display them
        for exp in expenses:
            html += f"""
                        <tr>
                            <td>{exp[0]}</td>
                            <td>{exp[1]}</td>
                            <td>{exp[2]}</td>
                            <td>{exp[3]}</td>
                        </tr>
            """
    else:  # If no expenses, show a message
        html += """
                        <tr>
                            <td colspan="4">No expenses available</td>
                        </tr>
        """

    html += f"""
                    </tbody>
                </table>
            </section>

            <!-- Total Spending -->
            <section>
                <div class="total-spending">
                    💰 Total Spending: ₹{total_spending:.2f}
                </div>
            </section>

            <!-- Clear Expenses Button -->
            <section>
                <div class="clear-expenses">
                    <form action="/clear_expenses" method="POST">
                        <button type="submit" style="background-color: red;">Clear All Expenses</button>
                    </form>
                </div>
            </section>
        </main>
    </body>
    </html>
    """
    return html

# Route to handle adding new expenses
@app.route('/add_expense', methods=['POST'])
def add_expense():
    amount = request.form['amount']
    category = request.form['category']
    date = datetime.now().strftime('%Y-%m-%d')
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (amount, category, date) VALUES (%s, %s, %s)", (amount, category, date))
    conn.commit()
    conn.close()
    # Add the redirect with a status code to force the reload
    return redirect(url_for('home'), code=303)

# Route to clear all expenses
@app.route('/clear_expenses', methods=['POST'])
def clear_expenses():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses")  # Clear all rows in the table
    cursor.execute("ALTER TABLE expenses AUTO_INCREMENT = 1")  # Reset AUTO_INCREMENT value
    conn.commit()
    conn.close()
    return home()  # Redirect to the homepage

if __name__ == '__main__':
    app.run(debug=True)
