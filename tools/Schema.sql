-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
--   Schema.sql
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


-- DROP TABLES IF THEY EXIST
/*
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Inventory;
DROP TABLE IF EXISTS Suppliers;
DROP TABLE IF EXISTS Sales;
DROP TABLE IF EXISTS Forecast;
DROP TABLE IF EXISTS Orders;
*/

-- CREATE PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductName TEXT NOT NULL,
    ProductPrice REAL
);


-- CREATE INVENTORY TABLE
CREATE TABLE IF NOT EXISTS Inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    StockCount INTEGER,
    ProductID INTEGER,
    FOREIGN KEY (ProductID) REFERENCES Products(id)    
);


-- CREATE SUPPLIERS TABLE
CREATE TABLE IF NOT EXISTS Suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    SupplierName TEXT,
    SupplierPhone INTEGER,
    SupplierEmail TEXT,
    ProductID INTEGER,
    ProductCost REAL,
    FOREIGN KEY (ProductID) REFERENCES Products(id)     
);


-- CREATE SALES TABLE
CREATE TABLE IF NOT EXISTS Sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    SaleQuantity INTEGER,
    SaleDate DATE,
    InventoryID INTEGER,
    FOREIGN KEY (InventoryID) REFERENCES Inventory(id)    
);


-- CREATE DEMAND TABLE
CREATE TABLE IF NOT EXISTS Forecast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ForecastDate DATE,
    ForecastQuantity INTEGER,
    InventoryID INTEGER,
    FOREIGN KEY (InventoryID) REFERENCES Inventory(id)    
);


-- CREATE ORDERS TABLE
CREATE TABLE IF NOT EXISTS Orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderDate DATE,
    OrderedQuantity INTEGER,
    ReceivedQuantity INTEGER,
    OrderStatus TEXT,
    ProductID INTEGER,
    SupplierID INTEGER,
    FOREIGN KEY (ProductID) REFERENCES Products(id),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(id)    
);


/* EOF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */