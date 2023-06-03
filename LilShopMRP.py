# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LilShopMRP.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from flask import Flask, g, render_template, request, redirect, url_for
import sqlite3
import os
from contextlib import closing


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# HELPERS

dir_path = os.path.dirname(os.path.realpath(__file__))
sql_schema = os.path.join(dir_path, 'tools/Schema.sql')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DATABASE ACTION

database = os.path.join(dir_path, 'LilShopMRP.db')

def connect_db():
    return sqlite3.connect(database)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource(sql_schema, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        
def get_table(table_name):
    with closing(connect_db()) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(f"SELECT * FROM {table_name}").fetchall()
    return [dict(row) for row in rows]
        
def add_to_db(table_name, **kwargs):
    columns = ', '.join(kwargs.keys())
    placeholders = ', '.join('?' for _ in kwargs)
    values = tuple(kwargs.values())
    with closing(connect_db()) as db:
        db.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
        db.commit()
        
def count_table_rows(table_name):
    with closing(connect_db()) as db:
        count = db.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    return count

def update_in_db(table_name, id, **kwargs):
    columns = ', '.join(f"{key} = ?" for key in kwargs)
    values = list(kwargs.values()) + [id]
    with closing(connect_db()) as db:
        db.execute(f"UPDATE {table_name} SET {columns} WHERE id = ?", values)
        db.commit()

def delete_from_db(table_name, id):
    with closing(connect_db()) as db:
        db.execute(f"DELETE FROM {table_name} WHERE id = ?", (id,))
        db.commit()
        
def get_inventory_with_product_names():
    with closing(connect_db()) as db:
        db.row_factory = sqlite3.Row
        inventory = db.execute("""
            SELECT Inventory.id, Inventory.StockCount, Products.ProductName
            FROM Inventory
            INNER JOIN Products ON Inventory.ProductID = Products.id
        """).fetchall()
    return [dict(row) for row in inventory]

def get_stock_count():
    with closing(connect_db()) as db:
        total = db.execute("SELECT SUM(StockCount) FROM Inventory").fetchone()[0]
    return total if total is not None else 0

def get_total_stock_value():
    with closing(connect_db()) as db:
        total = db.execute("""
            SELECT SUM(Inventory.StockCount * Products.ProductPrice)
            FROM Inventory
            INNER JOIN Products ON Inventory.ProductID = Products.id
        """).fetchone()[0]
    return total if total is not None else 0


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FLASK KICKOFF

app = Flask(__name__)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
@app.route('/')
def index():
    products = get_table('Products')
    product_count = count_table_rows('Products')
    
    inventory = get_inventory_with_product_names()
    stock_count = get_stock_count()
    total_stock_value = get_total_stock_value()
    
    return render_template('index.html', 
                           products=products,
                           product_count=product_count,                           
                           inventory=inventory,
                           stock_count=stock_count,
                           total_stock_value=total_stock_value)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTS

@app.route('/add_product', methods=['POST'])
def add_product():
    add_to_db('Products', ProductName=request.form['ProductName'], ProductPrice=request.form['ProductPrice'])
    return redirect(url_for('index'))

@app.route('/get_product/<int:id>')
def get_product(id):
    with closing(connect_db()) as db:
        db.row_factory = sqlite3.Row
        product = db.execute("SELECT * FROM Products WHERE id = ?", (id,)).fetchone()
    return render_template('modal-product.html', product=dict(product))

@app.route('/update_product/<int:id>', methods=['POST'])
def update_product(id):
    update_in_db('Products', id, ProductName=request.form['ProductName'], ProductPrice=request.form['ProductPrice'])
    return redirect(url_for('index'))

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    delete_from_db('Products', id)
    return redirect(url_for('index'))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# INVENTORY

@app.route('/add_inventory', methods=['POST'])
def add_inventory_route():
    add_to_db('Inventory', ProductID=request.form['ProductID'], StockCount=request.form['StockCount'])
    return redirect(url_for('index'))

@app.route('/increment_inventory/<int:id>', methods=['POST'])
def increment_inventory(id):
    with closing(connect_db()) as db:
        db.execute("UPDATE Inventory SET StockCount = StockCount + 1 WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for('index'))

@app.route('/decrement_inventory/<int:id>', methods=['POST'])
def decrement_inventory(id):
    with closing(connect_db()) as db:
        db.execute("UPDATE Inventory SET StockCount = StockCount - 1 WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for('index'))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SUPPLIERS


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SALES


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FORECAST


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ORDERS


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

# EOF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~