import mysql.connector
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import secrets
from http.cookies import SimpleCookie

session = {}

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="appuser",
        password="app123",
        database="db_scalable1"
    )

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        params = parse_qs(url.query)
        action = params.get("action", [""])[0]
        if action == "test":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "success", "message": "Server berjalan!"}
            self.wfile.write(json.dumps(response).encode())
        elif action == "daftar_puisi":
            self.daftar_puisi()
        elif self.path == "/" or self.path == "/index.html":
            try:
                with open("index.html", "rb") as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == "/style.css":
            try:
                with open("style.css", "rb") as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/css")
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == "/script.js":
            try:
                with open("script.js", "rb") as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/javascript")
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Action tidak ditemukan"}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        url = urlparse(self.path)
        params = parse_qs(url.query)
        action = params.get("action", [""])[0]
        if action == "register":
            self.register()
        elif action == "login":
            self.login()
        elif action == "submit_puisi":
            self.submit_puisi()
        elif action == "daftar_puisi":
            self.daftar_puisi()
        elif action == "logout":
            self.logout()
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Action tidak ditemukan"}
            self.wfile.write(json.dumps(response).encode())

    def register(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        username = data.get("username")
        nama = data.get("nama")
        password = data.get("password")
        no_id = data.get("no_id")
        if not username or not nama or not password or not no_id:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Username, nama, password, and no_id harus diisi"}
            self.wfile.write(json.dumps(response).encode())
            return
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": "Username sudah digunakan"}
                self.wfile.write(json.dumps(response).encode())
                cursor.close()
                db.close()
                return
            cursor.execute("INSERT INTO users (username, nama, password, no_id) VALUES (%s, %s, %s, %s)", (username, nama, password, no_id))
            db.commit()
            cursor.close()
            db.close()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "success", "message": "User berhasil didaftarkan"}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(response).encode())

    def login(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Username and password harus diisi"}
            self.wfile.write(json.dumps(response).encode())
            return
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT id, username, password, nama, no_id FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            db.close()
            if user is None:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": "Username atau password salah"}
                self.wfile.write(json.dumps(response).encode())
                return
            user_id = user[0]
            stored_password = user[2]
            if password != stored_password:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": "Username atau password salah"}
                self.wfile.write(json.dumps(response).encode())
                return
            session_token = secrets.token_hex(16)
            session[session_token] = user_id
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Set-Cookie", f"session_token={session_token}; HttpOnly")
            self.end_headers()
            response = {"status": "success", "message": "Login berhasil", "nama": user[3]}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(response).encode())

    def get_session_token(self):
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return None
        cookie = SimpleCookie(cookie_header)
        cookie.load(cookie_header)
        if "session_token" not in cookie:
            return None
        session_id = cookie["session_token"].value
        user_id = session.get(session_id)
        return user_id

    def submit_puisi(self):
        user_id = self.get_session_token()
        if user_id is None:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Anda harus login terlebih dahulu"}
            self.wfile.write(json.dumps(response).encode())
            return
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        judul = data.get("judul")
        isi = data.get("isi")
        kategori = data.get("kategori")
        keyword = data.get("keyword")
        if not judul or not isi or not kategori:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Judul, isi, dan kategori puisi harus diisi"}
            self.wfile.write(json.dumps(response).encode())
            return
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("INSERT INTO puisi (user_id, judul, tgl_submit, isi, kategori, keyword) VALUES (%s, %s, CURDATE(), %s, %s, %s)", (user_id, judul, isi, kategori, keyword))
            db.commit()
            cursor.close()
            db.close()
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "success", "message": "Puisi berhasil disubmit"}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(response).encode())

    def daftar_puisi(self):
        user_id = self.get_session_token()
        if user_id is None:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Anda harus login terlebih dahulu"}
            self.wfile.write(json.dumps(response).encode())
            return
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id, judul, tgl_submit, isi, kategori, keyword FROM puisi WHERE user_id = %s ORDER BY tgl_submit DESC", (user_id,))
            puisi_list = cursor.fetchall()
            for item in puisi_list:
                item["tgl_submit"] = item["tgl_submit"].isoformat()
            cursor.close()
            db.close()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "success", "data": puisi_list}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(response).encode())

    def logout(self):
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Belum login atau session token tidak valid"}
            self.wfile.write(json.dumps(response).encode())
            return
        cookie = SimpleCookie(cookie_header)
        cookie.load(cookie_header)
        if "session_token" not in cookie:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Belum login atau session token tidak valid"}
            self.wfile.write(json.dumps(response).encode())
            return
        session_token = cookie["session_token"].value
        if session_token in session:
            del session[session_token]
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Set-Cookie", "session_token=; HttpOnly; Max-Age=0")
        self.end_headers()
        response = {"status": "success", "message": "Logout berhasil"}
        self.wfile.write(json.dumps(response).encode())

server = HTTPServer(("0.0.0.0", 8080), RequestHandler)
print("Server berjalan di port 8080")
server.serve_forever()