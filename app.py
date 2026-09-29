from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory
)

from config import Config

from models.user import db, User
from models.client import Client
from models.case import Case
from models.hearing import Hearing
from models.document import Document

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required
)

import os


# ============================================================
# APPLICATION SETUP
# ============================================================

app = Flask(__name__)

app.config.from_object(Config)


# ============================================================
# FILE UPLOAD CONFIGURATION
# ============================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


# ============================================================
# DATABASE SETUP
# ============================================================

db.init_app(app)


# ============================================================
# LOGIN MANAGER
# ============================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return redirect(url_for("login"))


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():

    client_count = Client.query.count()
    case_count = Case.query.count()
    hearing_count = Hearing.query.count()
    document_count = Document.query.count()

    return render_template(
        "dashboard.html",
        client_count=client_count,
        case_count=case_count,
        hearing_count=hearing_count,
        document_count=document_count
    )


# ============================================================
# CLIENTS
# ============================================================

@app.route("/clients", methods=["GET", "POST"])
@login_required
def clients():

    message = None

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        new_client = Client(
            name=name,
            email=email,
            phone=phone,
            address=address
        )

        db.session.add(new_client)
        db.session.commit()

        message = "Client added successfully!"

    all_clients = Client.query.all()

    return render_template(
        "clients.html",
        clients=all_clients,
        message=message
    )


# ============================================================
# EDIT CLIENT
# ============================================================

@app.route(
    "/clients/edit/<int:client_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_client(client_id):

    client = Client.query.get_or_404(client_id)

    if request.method == "POST":

        client.name = request.form["name"]
        client.email = request.form["email"]
        client.phone = request.form["phone"]
        client.address = request.form["address"]

        db.session.commit()

        return redirect(
            url_for("clients")
        )

    return render_template(
        "edit_client.html",
        client=client,
        message=None
    )


# ============================================================
# DELETE CLIENT
# ============================================================

@app.route(
    "/clients/delete/<int:client_id>",
    methods=["POST"]
)
@login_required
def delete_client(client_id):

    client = Client.query.get_or_404(client_id)

    cases = Case.query.filter_by(
        client_id=client.id
    ).all()

    for case in cases:

        Hearing.query.filter_by(
            case_id=case.id
        ).delete()

        documents = Document.query.filter_by(
            case_id=case.id
        ).all()

        for document in documents:

            if document.file_path:

                file_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    document.file_path
                )

                if os.path.exists(file_path):
                    os.remove(file_path)

            db.session.delete(document)

        db.session.delete(case)

    db.session.delete(client)

    db.session.commit()

    return redirect(
        url_for("clients")
    )


# ============================================================
# CASES
# ============================================================

@app.route("/cases", methods=["GET", "POST"])
@login_required
def cases():

    message = None

    if request.method == "POST":

        case_number = request.form["case_number"]
        cnr_number = request.form["cnr_number"]
        title = request.form["title"]
        case_type = request.form["case_type"]
        court = request.form["court"]
        filing_date = request.form["filing_date"]
        status = request.form["status"]

        client_id = int(
            request.form["client_id"]
        )

        description = request.form["description"]

        existing_case = Case.query.filter_by(
            case_number=case_number
        ).first()

        if existing_case:

            message = "Case number already exists!"

        else:

            if cnr_number:

                existing_cnr = Case.query.filter_by(
                    cnr_number=cnr_number
                ).first()

                if existing_cnr:
                    message = "CNR number already exists!"

            if message is None:

                new_case = Case(
                    case_number=case_number,
                    cnr_number=cnr_number,
                    title=title,
                    case_type=case_type,
                    court=court,
                    filing_date=filing_date,
                    status=status,
                    client_id=client_id,
                    description=description
                )

                db.session.add(new_case)
                db.session.commit()

                message = "Case added successfully!"

    all_cases = Case.query.all()
    all_clients = Client.query.all()

    return render_template(
        "cases.html",
        cases=all_cases,
        clients=all_clients,
        message=message
    )


# ============================================================
# EDIT CASE
# ============================================================

@app.route(
    "/cases/edit/<int:case_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_case(case_id):

    case = Case.query.get_or_404(case_id)

    clients = Client.query.all()

    message = None

    if request.method == "POST":

        case_number = request.form["case_number"]
        cnr_number = request.form["cnr_number"]
        title = request.form["title"]
        case_type = request.form["case_type"]
        court = request.form["court"]
        filing_date = request.form["filing_date"]
        status = request.form["status"]

        client_id = int(
            request.form["client_id"]
        )

        description = request.form["description"]

        existing_case = Case.query.filter(
            Case.case_number == case_number,
            Case.id != case_id
        ).first()

        if existing_case:

            message = "Case number already exists!"

        elif cnr_number:

            existing_cnr = Case.query.filter(
                Case.cnr_number == cnr_number,
                Case.id != case_id
            ).first()

            if existing_cnr:
                message = "CNR number already exists!"

        if message is None:

            case.case_number = case_number
            case.cnr_number = cnr_number
            case.title = title
            case.case_type = case_type
            case.court = court
            case.filing_date = filing_date
            case.status = status
            case.client_id = client_id
            case.description = description

            db.session.commit()

            return redirect(
                url_for("cases")
            )

    return render_template(
        "edit_case.html",
        case=case,
        clients=clients,
        message=message
    )


# ============================================================
# DELETE CASE
# ============================================================

@app.route(
    "/cases/delete/<int:case_id>",
    methods=["POST"]
)
@login_required
def delete_case(case_id):

    case = Case.query.get_or_404(case_id)

    Hearing.query.filter_by(
        case_id=case.id
    ).delete()

    documents = Document.query.filter_by(
        case_id=case.id
    ).all()

    for document in documents:

        if document.file_path:

            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                document.file_path
            )

            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(document)

    db.session.delete(case)

    db.session.commit()

    return redirect(
        url_for("cases")
    )


# ============================================================
# HEARINGS
# ============================================================

@app.route("/hearings", methods=["GET", "POST"])
@login_required
def hearings():

    message = None

    if request.method == "POST":

        case_id = int(
            request.form["case_id"]
        )

        hearing_date = request.form["hearing_date"]
        court = request.form["court"]
        judge = request.form["judge"]
        hearing_type = request.form["hearing_type"]
        purpose = request.form["purpose"]
        status = request.form["status"]
        notes = request.form["notes"]

        new_hearing = Hearing(
            case_id=case_id,
            hearing_date=hearing_date,
            court=court,
            judge=judge,
            hearing_type=hearing_type,
            purpose=purpose,
            status=status,
            notes=notes
        )

        db.session.add(new_hearing)
        db.session.commit()

        message = "Hearing added successfully!"

    all_hearings = Hearing.query.all()
    all_cases = Case.query.all()

    return render_template(
        "hearings.html",
        hearings=all_hearings,
        cases=all_cases,
        message=message
    )


# ============================================================
# EDIT HEARING
# ============================================================

@app.route(
    "/hearings/edit/<int:hearing_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_hearing(hearing_id):

    hearing = Hearing.query.get_or_404(
        hearing_id
    )

    cases = Case.query.all()

    if request.method == "POST":

        hearing.case_id = int(
            request.form["case_id"]
        )

        hearing.hearing_date = request.form[
            "hearing_date"
        ]

        hearing.court = request.form["court"]
        hearing.judge = request.form["judge"]

        hearing.hearing_type = request.form[
            "hearing_type"
        ]

        hearing.purpose = request.form["purpose"]
        hearing.status = request.form["status"]
        hearing.notes = request.form["notes"]

        db.session.commit()

        return redirect(
            url_for("hearings")
        )

    return render_template(
        "edit_hearing.html",
        hearing=hearing,
        cases=cases,
        message=None
    )


# ============================================================
# DELETE HEARING
# ============================================================

@app.route(
    "/hearings/delete/<int:hearing_id>",
    methods=["POST"]
)
@login_required
def delete_hearing(hearing_id):

    hearing = Hearing.query.get_or_404(
        hearing_id
    )

    db.session.delete(hearing)
    db.session.commit()

    return redirect(
        url_for("hearings")
    )


# ============================================================
# DOCUMENTS
# ============================================================

@app.route("/documents", methods=["GET", "POST"])
@login_required
def documents():

    message = None

    if request.method == "POST":

        case_id = int(
            request.form["case_id"]
        )

        name = request.form["name"]
        document_type = request.form["document_type"]
        description = request.form["description"]

        uploaded_file = request.files.get("file")

        if uploaded_file and uploaded_file.filename:

            filename = uploaded_file.filename

            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            uploaded_file.save(file_path)

            new_document = Document(
                case_id=case_id,
                name=name,
                document_type=document_type,
                file_path=filename,
                description=description
            )

            db.session.add(new_document)
            db.session.commit()

            message = "Document uploaded successfully!"

        else:

            message = "Please select a file!"

    all_documents = Document.query.all()
    all_cases = Case.query.all()

    return render_template(
        "documents.html",
        documents=all_documents,
        cases=all_cases,
        message=message
    )


# ============================================================
# VIEW UPLOADED DOCUMENT
# ============================================================

@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# ============================================================
# DELETE DOCUMENT
# ============================================================

@app.route(
    "/documents/delete/<int:document_id>",
    methods=["POST"]
)
@login_required
def delete_document(document_id):

    document = Document.query.get_or_404(
        document_id
    )

    if document.file_path:

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            document.file_path
        )

        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(document)
    db.session.commit()

    return redirect(
        url_for("documents")
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid email or password!"
        )

    return render_template(
        "login.html"
    )


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        role = request.form.get(
            "role",
            "lawyer"
        )

        # Validate required fields

        if not name or not email or not password:

            return "Please fill in all required fields!"

        # Check duplicate email

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            return (
                "Email already registered! "
                "Please use another email."
            )

        # Allowed roles

        allowed_roles = [
            "lawyer",
            "staff",
            "admin"
        ]

        if role not in allowed_roles:

            role = "lawyer"

        # Hash password

        hashed_password = generate_password_hash(
            password,
            method="pbkdf2:sha256"
        )

        # Create user

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        # After successful registration,
        # go back to login

        return redirect(
            url_for("login", registered="1")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )