from database.connection import fetch_all, fetch_one

USER_SELECT = """
    SELECT u.user_id, u.last_name, u.first_name, u.second_name, u.login, r.name
    FROM users u
    JOIN roles r ON u.role_id = r.role_id
"""

def find_user_by_login(login):
    return fetch_one(USER_SELECT  + "WHERE login = %s", (login,))

def get_all_users():
    return fetch_all(USER_SELECT + "ORDER BY u.last_name, u.first_name")

def get_full_name(user):
    parts = [user["last_name"], user["first_name"], user["second_name"]]
    return " ".join(part for part in parts if part)