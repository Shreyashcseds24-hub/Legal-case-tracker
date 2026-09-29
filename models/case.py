from datetime import datetime
from models.user import db


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(100), unique=True, nullable=False)
    cnr_number = db.Column(db.String(100), unique=True)
    title = db.Column(db.String(200), nullable=False)
    case_type = db.Column(db.String(100))
    court = db.Column(db.String(200))
    filing_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Pending")
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=False
    )

    client = db.relationship(
        "Client",
        backref=db.backref("cases", lazy=True)
    )

    def __repr__(self):
        return f"<Case {self.case_number}>"