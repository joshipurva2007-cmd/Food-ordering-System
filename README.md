
# Online Food Order Processing System

## Project Overview

The Online Food Order Processing System is a web-based application developed using Python, Flask, HTML, CSS, JavaScript, and SQLite.

It manages incoming customer food orders using the Queue Data Structure. Orders are processed in the same order in which they are received.

## Features

- Food menu with item prices
- Customer order placement
- Automatic total amount calculation
- FIFO queue management
- Order preparation status tracking
- Completed orders display
- Order history
- Bill generation and printing
- SQLite database for permanent order storage
- Responsive user interface

## Data Structure Used

**Queue (FIFO - First In, First Out)**

A queue follows the First In, First Out principle. The order received first is processed first.

Example:

Order 101 → Order 102 → Order 103

Order 101 must be completed before Order 102 can be processed.

## Technologies Used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript

## Project Setup

### 1. Install Python

Install Python 3 from https://www.python.org/

### 2. Open the Project Folder

Open the project folder in Visual Studio Code.

### 3. Install Dependencies

Open the VS Code terminal and run:

```bash
python -m pip install -r requirements.txt
```

### 4. Run the Application

Execute:

```bash
python app.py
```

### 5. Open the Website

Open your browser and visit:

http://127.0.0.1:5000/

## Database

The application automatically creates the `food_orders.db` SQLite database when it starts.

Customer orders and their statuses are stored in the database.

## Order Status Flow

Pending → Preparing → Completed

## Conclusion

This project demonstrates how a Queue Data Structure can be used in a real-world food ordering system to ensure that orders are processed fairly and in the correct sequence.
