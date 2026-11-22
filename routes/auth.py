from fastapi import (
    APIRouter,
    HTTPException
)
from database import get_db
from jose import jwt
from datetime import (
    datetime,
    timedelta
)

router = APIRouter()

# Secret key
SECRET_KEY = "movie_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


@router.get("/")
def auth_home():
    return {
        "message":
        "Auth route working"
    }


# -----------------------------
# REGISTER USER
# -----------------------------
@router.post("/register")
def register(user: dict):

    username = user.get("username")
    password = user.get("password")

    conn = get_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (username, password)
            VALUES (%s, %s)
            """,
            (
                username,
                password
            )
        )

        conn.commit()

        return {
            "message":
            "User registered successfully"
        }

    except:

        return {
            "message":
            "User already exists"
        }

    finally:
        conn.close()


# -----------------------------
# LOGIN USER
# -----------------------------
@router.post("/login")
def login(user: dict):

    username = user.get("username")
    password = user.get("password")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=%s
        AND password=%s
        """,
        (
            username,
            password
        )
    )

    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    expire = (
        datetime.utcnow()
        + timedelta(days=7)
    )

    token = jwt.encode(
        {
            "sub": username,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message":
        "Login successful",
        "token":
        token
    }

    # Create token
    expire = (
        datetime.utcnow()
        + timedelta(days=7)
    )

    token = jwt.encode(
        {
            "sub":
            username,
            "exp":
            expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message":
        "Login successful",
        "token":
        token
    }


# -----------------------------
# LOGOUT USER
# -----------------------------
@router.post("/logout")
def logout():

    return {
        "message":
        "Logged out successfully"
    }