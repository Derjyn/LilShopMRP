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
            SELECT Inventory.id, Inventory.InventoryCount, Products.ProductName
            FROM Inventory
            INNER JOIN Products ON Inventory.ProductID = Products.id
        """).fetchall()
    return [dict(row) for row in inventory]

def get_inventory_count():
    with closing(connect_db()) as db:
        total = db.execute("SELECT SUM(InventoryCount) FROM Inventory").fetchone()[0]
    return total if total is not None else 0

def get_total_inventory_value():
    with closing(connect_db()) as db:
        total = db.execute("""
            SELECT SUM(Inventory.InventoryCount * Products.ProductPrice)
            FROM Inventory
            INNER JOIN Products ON Inventory.ProductID = Products.id
        """).fetchone()[0]
    return total if total is not None else 0

def add_supplier(supplier_name, supplier_phone, supplier_email, product_id, product_cost):
    add_to_db('Suppliers', 
              SupplierName=supplier_name, 
              SupplierPhone=supplier_phone, 
              SupplierEmail=supplier_email, 
              ProductID=product_id, 
              ProductCost=product_cost)
    
def get_suppliers_with_product_names():
    with closing(connect_db()) as db:
        db.row_factory = sqlite3.Row
        suppliers = db.execute("""
            SELECT Suppliers.id,Suppliers.SupplierName, Suppliers.SupplierPhone, Suppliers.SupplierEmail, Suppliers.ProductCost, Products.ProductName
            FROM Suppliers
            INNER JOIN Products ON Suppliers.ProductID = Products.id
        """).fetchall()
    return [dict(row) for row in suppliers]    


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
    inventory_count = get_inventory_count()
    total_inventory_value = get_total_inventory_value()    
    suppliers = get_suppliers_with_product_names()
    
    return render_template('index.html', 
                           products=products,
                           product_count=product_count,                           
                           inventory=inventory,
                           inventory_count=inventory_count,
                           total_inventory_value=total_inventory_value,
                           suppliers=suppliers)


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
    add_to_db('Inventory', ProductID=request.form['ProductID'], InventoryCount=request.form['InventoryCount'])
    return redirect(url_for('index'))

@app.route('/increment_inventory/<int:id>', methods=['POST'])
def increment_inventory(id):
    with closing(connect_db()) as db:
        db.execute("UPDATE Inventory SET InventoryCount = InventoryCount + 1 WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for('index'))

@app.route('/decrement_inventory/<int:id>', methods=['POST'])
def decrement_inventory(id):
    with closing(connect_db()) as db:
        quantity = db.execute("SELECT InventoryCount FROM Inventory WHERE id = ?", (id,)).fetchone()[0]
        if quantity > 0:
            db.execute("UPDATE Inventory SET InventoryCount = InventoryCount - 1 WHERE id = ?", (id,))
            db.commit()
    return redirect(url_for('index'))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SUPPLIERS

@app.route('/add_supplier', methods=['POST'])
def add_supplier_route():
    add_supplier(
        request.form['supplier_name'],
        request.form['supplier_phone'],
        request.form['supplier_email'],
        request.form['product_id'],
        request.form['product_cost'])
    return redirect(url_for('index'))

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