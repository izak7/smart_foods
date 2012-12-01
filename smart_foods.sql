--Suppliers
--Raw materials
--clients
--Products
--Supplies
--Sales_journal
-- transactions
CREATE TABLE sessions (
    session_id CHAR(128) UNIQUE NOT NULL,
    atime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data TEXT
);

CREATE TABLE user_roles (
        id BIGSERIAL NOT NULL PRIMARY KEY,
        cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        user_role TEXT NOT NULL UNIQUE,
        descr text DEFAULT ''
);

CREATE TABLE user_role_permissions (
        id bigserial NOT NULL PRIMARY KEY,
        user_role BIGINT NOT NULL REFERENCES user_roles ON DELETE CASCADE ON UPDATE CASCADE,
        Sys_module TEXT NOT NULL, -- the name of the module - defined above this level
        sys_perms VARCHAR(16) NOT NULL,
        unique(sys_module,user_role)
);

CREATE TABLE users (
    id bigserial NOT NULL PRIMARY KEY,
    cdate timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL, -- blowfish hash of password
    email TEXT,
    user_role  BIGINT NOT NULL REFERENCES user_roles ON DELETE RESTRICT ON UPDATE CASCADE,
    transaction_limit TEXT DEFAULT '0/'||to_char(NOW(),'yyyymmdd'),
    is_active BOOLEAN NOT NULL DEFAULT 't',
    is_system_user BOOLEAN NOT NULL DEFAULT 'f'

);

CREATE TABLE audit_log (
        id BIGSERIAL NOT NULL PRIMARY KEY,
        cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        actor_type TEXT NOT NULL,
        actor_id BIGINT,
        action text NOT NULL,
        --remote_ip INET,
        detail TEXT NOT NULL
);

CREATE INDEX au_idx1 ON audit_log(cdate);
CREATE INDEX au_idx2 ON audit_log(actor_type);
CREATE INDEX au_idx3 ON audit_log(actor_id);
CREATE INDEX au_idx4 ON audit_log(action);

CREATE TABLE suppliers(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT DEFAULT '',
    email TEXT,
    telephone TEXT NOT NULL,
    cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw_materials(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    quality_rank TEXT NOT NULL DEFAULT '',
    quantity NUMERIC NOT NULL DEFAULT 0,
    preffered_units TEXT NOT NULL DEFAULT '',
    descr TEXT,
    cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    descr TEXT NOT NULL,
    quantity NUMERIC NOT NULL DEFAULT 0,
    cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_raw_materials(
    id SERIAL NOT NULL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products,
    raw_material_id INTEGER NOT NULL REFERENCES raw_materials,
    proportion NUMERIC NOT NULL DEFAULT 0,
    --UNIQUE(product_id, raw_material_id)
    cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE process(
    id SERIAL NOT NULL PRIMARY KEY,
    raw_material_id INTEGER NOT NULL REFERENCES raw_materials,
    qty NUMERIC NOT NULL DEFAULT 0,       -- quantity of raw material used
    product_id INTEGER NOT NULL REFERENCES products,-- product for which this raw material was used.
    pdate DATE NOT NULL DEFAULT CURRENT_DATE,
    cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE clients(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE supplies(
    id SERIAL NOT NULL PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES suppliers,
    raw_material_id INTEGER NOT NULL REFERENCES raw_materials,
    sdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price NUMERIC NOT NULL DEFAULT 0,
    quantity NUMERIC NOT NULL DEFAULT 0,
    cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales_journal(
    id SERIAL NOT NULL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products,
    client_id INTEGER,
    quantity NUMERIC NOT NULL DEFAULT 0,
    price NUMERIC NOT NULL DEFAULT 0,
    cdate TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Data Follows
INSERT INTO user_roles(user_role, descr)
VALUES('Administrator','For the Administrators');

INSERT INTO user_role_permissions(user_role, sys_module,sys_perms)
VALUES
        ((SELECT id FROM user_roles WHERE user_role ='Administrator'),'Users','rmad');

INSERT INTO users(firstname,lastname,username,password,email,user_role,is_system_user)
VALUES
        ('Samuel','Sekiwere','admin',crypt('admin',gen_salt('bf')),'sekiskylink@gmail.com',
        (SELECT id FROM user_roles WHERE user_role ='Administrator'),'t');
