from datetime import datetime
from models.user import db


class Hearing(db.Model):
    __tablename__ = "hearings"

    id = db.Column(db.Integer, primary_key=True)

    hearing_date = db.Column(db.Date, nullable=False)

    court = db.Column(db.String(200))

    judge = db.Column(db.String(150))

    hearing_type = db.Column(db.String(100))

    purpose = db.Column(db.Text)

    status = db.Column(
        db.String(50),
        default="Scheduled",
        nullable=False
    )

    notes = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False
    )

    case = db.relationship(
        "Case",
        backref=db.backref("hearings", lazy=True)
    )

    def __repr__(self):
        return f"<Hearing {self.hearing_date}>"