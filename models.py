from pagination import lit

def auth_user(db, username, password):
    sql = ("SELECT id,firstname,lastname FROM users WHERE username = '%s' AND password = "
            "crypt('%s', password)")
    res = db.query(sql % (username, password))
    if not res:
        return False,"Wrong username or password"
    else:
        return True,res[0]
