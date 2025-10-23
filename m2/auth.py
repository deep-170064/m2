# auth.py
from sqlalchemy import text
from db import get_engine
import getpass

# Disable bcrypt for now to use plain text passwords
USE_BCRYPT = False
print("🔐 Using plain text password authentication for development\n")

engine = get_engine()

# session state
current_user = None   # employee_id
current_role = None   # 'CASHIER' / 'MANAGER' / 'ADMIN'
current_name = None   # employee name (for greetings)


# ---------------- Utility: Password Handling ----------------
def hash_password(plain_password: str) -> str:
    """Return hashed password if bcrypt available; otherwise return plain."""
    if USE_BCRYPT:
        import bcrypt
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    else:
        return plain_password  # fallback (not secure)


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify password against stored value."""
    if USE_BCRYPT:
        import bcrypt
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), stored_password.encode('utf-8'))
        except Exception:
            return False
    else:
        # Plain text comparison - for development only
        result = plain_password == stored_password
        if not result:
            print(f"🔍 Debug: '{plain_password}' != '{stored_password}'")
        return result


# ----------------- Login -----------------
def login() -> bool:
    """Prompt for username & password and set session globals if successful."""
    global current_user, current_role, current_name
    try:
        print("\n=== Login ===")
        username = input("👤 Username: ").strip()
        password = getpass.getpass("🔑 Password: ").strip()

        if not username:
            print("❌ Username required.")
            return False

        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT employee_id, name, role, password
                FROM employees
                WHERE username = :uname
            """), {"uname": username})
            row = res.fetchone()

        if not row:
            print("❌ Invalid username.")
            return False

        emp_id, name, role, stored_password = row
        
        # Debug info
        print(f"🔍 Debug: Checking password for {username}")
        print(f"🔍 Debug: Role: {role}")
        print(f"🔍 Debug: Using bcrypt: {USE_BCRYPT}")

        if not verify_password(password, stored_password):
            print("❌ Wrong password.")
            print(f"💡 Try these credentials:")
            print(f"   - Admin: alicej / admin123")
            print(f"   - Manager: carold / manager123") 
            print(f"   - Cashier: emma / cashier123")
            return False

        current_user = emp_id
        current_role = role
        current_name = name
        print(f"\n✅ Welcome {current_name}! You are logged in as {current_role}.\n")
        return True

    except Exception as e:
        print("❌ Login error:", e)
        return False


# ----------------- Permission Check -----------------
def has_permission(allowed_roles):
    """Return True if current_role is in allowed_roles, else print denied and return False."""
    if current_role is None:
        print("🚫 Not logged in.")
        return False
    if current_role not in allowed_roles:
        print(f"🚫 Permission denied! {current_role} cannot perform this action.")
        return False
    return True


# ----------------- Logout -----------------
def logout():
    """Clear session data."""
    global current_user, current_role, current_name
    current_user = None
    current_role = None
    current_name = None
    print("✅ Logged out successfully.")


# Getter functions to access the global variables
def get_current_user():
    return current_user

def get_current_role():
    return current_role

def get_current_name():
    return current_name