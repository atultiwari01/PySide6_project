
import sys
import mysql.connector
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QTableWidget, QTableWidgetItem, QTabWidget, 
                              QFormLayout, QSpinBox, QDoubleSpinBox, QMessageBox,
                              QHeaderView, QComboBox, QDateEdit)
from PySide6.QtCore import Qt, QDate

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password"
            )
            self.cursor = self.connection.cursor()
            
            # Create database 
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS billing_app")
            self.cursor.execute("USE billing_app")
            
            # Create customers table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    address TEXT
                )
            """)
            
            # Create bills table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS bills (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT,
                    bill_date DATE,
                    total_amount DECIMAL(10, 2),
                    items TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                )
            """)
            
            self.connection.commit()
            print("Database and tables created successfully")
            
        except mysql.connector.Error as error:
            print(f"Failed to connect to MySQL: {error}")
            if self.connection:
                self.connection.close()
                self.connection = None
            self.cursor = None
    
    def add_customer(self, name, email, phone, address):
        if not self.connection or not self.cursor:
            print("No database connection")
            return None
            
        try:
            query = """
                INSERT INTO customers (name, email, phone, address)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query, (name, email, phone, address))
            self.connection.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as error:
            print(f"Failed to add customer: {error}")
            return None
    
    def get_all_customers(self):
        if not self.connection or not self.cursor:
            print("No database connection")
            return []
            
        try:
            self.cursor.execute("SELECT * FROM customers")
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"Failed to retrieve customers: {error}")
            return []
    
    def add_bill(self, customer_id, bill_date, total_amount, items):
        if not self.connection or not self.cursor:
            print("No database connection")
            return None
            
        try:
            query = """
                INSERT INTO bills (customer_id, bill_date, total_amount, items)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query, (customer_id, bill_date, total_amount, items))
            self.connection.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as error:
            print(f"Failed to add bill: {error}")
            return None
    
    def get_all_bills(self):
        if not self.connection or not self.cursor:
            print("No database connection")
            return []
            
        try:
            query = """
                SELECT b.id, c.name, b.bill_date, b.total_amount, b.items
                FROM bills b
                JOIN customers c ON b.customer_id = c.id
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"Failed to retrieve bills: {error}")
            return []
    
    def get_customer_names(self):
        if not self.connection or not self.cursor:
            print("No database connection")
            return []
            
        try:
            self.cursor.execute("SELECT id, name FROM customers")
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"Failed to retrieve customer names: {error}")
            return []
    
    def close(self):
        if self.connection and self.cursor:
            self.cursor.close()
            self.connection.close()
            print("MySQL connection closed")


class BillingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing System")
        self.setGeometry(100, 100, 800, 600)
        
        self.db = DatabaseManager()
        
        # Check if database connection was successful
        if not self.db.connection or not self.db.cursor:
            QMessageBox.critical(self, "Database Error", 
                                "Failed to connect to the database. Please check your MySQL settings.")
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Create Customer Tab
        customer_tab = QWidget()
        customer_layout = QVBoxLayout(customer_tab)
        
        # Customer form
        customer_form = QFormLayout()
        
        self.customer_name = QLineEdit()
        self.customer_email = QLineEdit()
        self.customer_phone = QLineEdit()
        self.customer_address = QLineEdit()
        
        customer_form.addRow("Name:", self.customer_name)
        customer_form.addRow("Email:", self.customer_email)
        customer_form.addRow("Phone:", self.customer_phone)
        customer_form.addRow("Address:", self.customer_address)
        
        customer_layout.addLayout(customer_form)
        
        # Add customer button
        add_customer_btn = QPushButton("Add Customer")
        add_customer_btn.clicked.connect(self.add_customer)
        customer_layout.addWidget(add_customer_btn)
        
        # Customer table
        self.customer_table = QTableWidget(0, 5)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "Address"])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        customer_layout.addWidget(QLabel("Customer List:"))
        customer_layout.addWidget(self.customer_table)
        
        # Create Billing Tab
        billing_tab = QWidget()
        billing_layout = QVBoxLayout(billing_tab)
        
        # Billing form
        billing_form = QFormLayout()
        
        self.customer_selector = QComboBox()
        self.update_customer_selector()
        
        self.bill_date = QDateEdit()
        self.bill_date.setDate(QDate.currentDate())
        self.bill_date.setCalendarPopup(True)
        
        self.bill_items = QLineEdit()
        self.bill_items.setPlaceholderText("Item1:Qty:Price, Item2:Qty:Price, ...")
        
        self.bill_total = QDoubleSpinBox()
        self.bill_total.setRange(0, 1000000)
        self.bill_total.setPrefix("$")
        
        billing_form.addRow("Customer:", self.customer_selector)
        billing_form.addRow("Bill Date:", self.bill_date)
        billing_form.addRow("Items:", self.bill_items)
        billing_form.addRow("Total Amount:", self.bill_total)
        
        billing_layout.addLayout(billing_form)
        
        # Add bill button
        add_bill_btn = QPushButton("Create Bill")
        add_bill_btn.clicked.connect(self.add_bill)
        billing_layout.addWidget(add_bill_btn)
        
        # Bills table
        self.bills_table = QTableWidget(0, 5)
        self.bills_table.setHorizontalHeaderLabels(["ID", "Customer", "Date", "Amount", "Items"])
        self.bills_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        billing_layout.addWidget(QLabel("Bills List:"))
        billing_layout.addWidget(self.bills_table)
        
        # Add tabs to the tab widget
        tabs.addTab(customer_tab, "Customers")
        tabs.addTab(billing_tab, "Billing")
        
        # Add tab widget to main layout
        main_layout.addWidget(tabs)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_data)
        main_layout.addWidget(refresh_btn)
        
        # Connection status label
        self.status_label = QLabel()
        if self.db.connection and self.db.cursor:
            self.status_label.setText("Database connection: Connected")
            self.status_label.setStyleSheet("color: green")
        else:
            self.status_label.setText("Database connection: Not connected")
            self.status_label.setStyleSheet("color: red")
        main_layout.addWidget(self.status_label)
        
        # Load initial data
        self.refresh_data()
    
    def add_customer(self):
        if not self.db.connection or not self.db.cursor:
            QMessageBox.warning(self, "Database Error", "No database connection")
            return
            
        name = self.customer_name.text()
        email = self.customer_email.text()
        phone = self.customer_phone.text()
        address = self.customer_address.text()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Customer name is required")
            return
        
        customer_id = self.db.add_customer(name, email, phone, address)
        
        if customer_id:
            QMessageBox.information(self, "Success", f"Customer added with ID: {customer_id}")
            # Clear form
            self.customer_name.clear()
            self.customer_email.clear()
            self.customer_phone.clear()
            self.customer_address.clear()
            # Refresh data
            self.refresh_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to add customer")
    
    def add_bill(self):
        if not self.db.connection or not self.db.cursor:
            QMessageBox.warning(self, "Database Error", "No database connection")
            return
            
        if self.customer_selector.count() == 0:
            QMessageBox.warning(self, "Validation Error", "No customers available. Please add a customer first.")
            return
        
        customer_id = self.customer_selector.currentData()
        bill_date = self.bill_date.date().toString("yyyy-MM-dd")
        total_amount = self.bill_total.value()
        items = self.bill_items.text()
        
        if not items:
            QMessageBox.warning(self, "Validation Error", "Please enter at least one item")
            return
        
        if total_amount <= 0:
            QMessageBox.warning(self, "Validation Error", "Total amount must be greater than zero")
            return
        
        bill_id = self.db.add_bill(customer_id, bill_date, total_amount, items)
        
        if bill_id:
            QMessageBox.information(self, "Success", f"Bill created with ID: {bill_id}")
            # Clear form
            self.bill_items.clear()
            self.bill_total.setValue(0)
            # Refresh data
            self.refresh_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to create bill")
    
    def update_customer_selector(self):
        self.customer_selector.clear()
        if not self.db.connection or not self.db.cursor:
            return
            
        customers = self.db.get_customer_names()
        
        for customer in customers:
            self.customer_selector.addItem(customer[1], customer[0])
    
    def load_customers(self):
        if not self.db.connection or not self.db.cursor:
            return
            
        customers = self.db.get_all_customers()
        self.customer_table.setRowCount(0)
        
        for row_idx, customer in enumerate(customers):
            self.customer_table.insertRow(row_idx)
            for col_idx, value in enumerate(customer):
                self.customer_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    def load_bills(self):
        if not self.db.connection or not self.db.cursor:
            return
            
        bills = self.db.get_all_bills()
        self.bills_table.setRowCount(0)
        
        for row_idx, bill in enumerate(bills):
            self.bills_table.insertRow(row_idx)
            for col_idx, value in enumerate(bill):
                self.bills_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    def refresh_data(self):
        if not self.db.connection or not self.db.cursor:
            return
            
        self.load_customers()
        self.update_customer_selector()
        self.load_bills()
    
    def closeEvent(self, event):
        self.db.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillingApp()
    window.show()
    sys.exit(app.exec())