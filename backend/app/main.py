import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.cloud.sql.connector import Connector, IPTypes
import psycopg
from psycopg.errors import UniqueViolation


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Gym Management API",
    description="Backend API for the Gym Management System",
    version="1.0.0"
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CLOUD SQL CONNECTOR
# =========================================================

connector = Connector()


def get_connection():

    return connector.connect(
        os.environ["INSTANCE_CONNECTION_NAME"],
        "psycopg",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        db=os.environ["DB_NAME"],
        ip_type=IPTypes.PUBLIC,
    )


# =========================================================
# PYDANTIC MODELS
# =========================================================

class MemberCreate(BaseModel):
    name: str
    email: str
    phone: str


class MemberUpdate(BaseModel):
    name: str
    email: str
    phone: str
    status: str


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Gym Management API is running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# GET ALL MEMBERS
# =========================================================

@app.get("/api/members")
def get_members():

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    join_date,
                    status
                FROM members
                ORDER BY id;
            """)

            rows = cursor.fetchall()

            members = []

            for row in rows:

                members.append({
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "join_date": str(row[4]),
                    "status": row[5]
                })

            return {
                "members": members
            }

    finally:

        conn.close()


# =========================================================
# GET SINGLE MEMBER
# =========================================================

@app.get("/api/members/{member_id}")
def get_member(member_id: int):

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    join_date,
                    status
                FROM members
                WHERE id = %s;
            """, (member_id,))

            row = cursor.fetchone()

            if row is None:

                raise HTTPException(
                    status_code=404,
                    detail="Member not found"
                )

            return {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "join_date": str(row[4]),
                "status": row[5]
            }

    finally:

        conn.close()


# =========================================================
# CREATE MEMBER
# =========================================================

@app.post("/api/members", status_code=201)
def create_member(member: MemberCreate):

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            try:

                cursor.execute("""
                    INSERT INTO members (
                        name,
                        email,
                        phone
                    )
                    VALUES (%s, %s, %s)
                    RETURNING
                        id,
                        name,
                        email,
                        phone,
                        join_date,
                        status;
                """, (
                    member.name,
                    member.email,
                    member.phone
                ))

                row = cursor.fetchone()

                conn.commit()

                return {
                    "message": "Member created successfully",
                    "member": {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "phone": row[3],
                        "join_date": str(row[4]),
                        "status": row[5]
                    }
                }

            except UniqueViolation:

                conn.rollback()

                raise HTTPException(
                    status_code=409,
                    detail="A member with this email already exists"
                )

    finally:

        conn.close()


# =========================================================
# UPDATE MEMBER
# =========================================================

@app.put("/api/members/{member_id}")
def update_member(
    member_id: int,
    member: MemberUpdate
):

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            try:

                cursor.execute("""
                    UPDATE members
                    SET
                        name = %s,
                        email = %s,
                        phone = %s,
                        status = %s
                    WHERE id = %s
                    RETURNING
                        id,
                        name,
                        email,
                        phone,
                        join_date,
                        status;
                """, (
                    member.name,
                    member.email,
                    member.phone,
                    member.status,
                    member_id
                ))

                row = cursor.fetchone()

                if row is None:

                    conn.rollback()

                    raise HTTPException(
                        status_code=404,
                        detail="Member not found"
                    )

                conn.commit()

                return {
                    "message": "Member updated successfully",
                    "member": {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "phone": row[3],
                        "join_date": str(row[4]),
                        "status": row[5]
                    }
                }

            except UniqueViolation:

                conn.rollback()

                raise HTTPException(
                    status_code=409,
                    detail="A member with this email already exists"
                )

    finally:

        conn.close()


# =========================================================
# DELETE MEMBER
# =========================================================

@app.delete("/api/members/{member_id}")
def delete_member(member_id: int):

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""
                DELETE FROM members
                WHERE id = %s
                RETURNING id;
            """, (member_id,))

            row = cursor.fetchone()

            if row is None:

                conn.rollback()

                raise HTTPException(
                    status_code=404,
                    detail="Member not found"
                )

            conn.commit()

            return {
                "message": "Member deleted successfully",
                "member_id": row[0]
            }

    finally:

        conn.close()
