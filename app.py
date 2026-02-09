from flask import Flask, render_template, request, redirect, url_for, session
import cv2
import numpy as np
import os

app = Flask(__name__)
app.secret_key = "weed_secret_key"

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            session["user"] = "admin"
            return redirect(url_for("home"))
    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------------- HOME / DETECTION ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files["image"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = cv2.imread(path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_green = np.array([25, 40, 40])
        upper_green = np.array([85, 255, 255])

        mask = cv2.inRange(hsv, lower_green, upper_green)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 600:
                x, y, w, h = cv2.boundingRect(cnt)
                if area < 4000:
                    label = "Weed"
                    color = (0, 0, 255)
                else:
                    label = "Crop"
                    color = (0, 255, 0)

                cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
                cv2.putText(img, label, (x, y-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        output_path = os.path.join(app.root_path, "static", "output.jpg")
        cv2.imwrite(output_path, img)

        return render_template("index.html", result=True)

    return render_template("index.html", result=False)

if __name__ == "__main__":
    app.run(debug=True)
