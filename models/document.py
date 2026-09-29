from datetime import datetime
from models.user import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(200),
        nullable=False
    )

    document_type = db.Column(
        db.String(100)
    )

    file_path = db.Column(
        db.String(500)
    )

    description = db.Column(
        db.Text
    )

    uploaded_at = db.Column(
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
        backref=db.backref("documents", lazy=True)
    )

    def __repr__(self):
        return f"<Document {self.name}>"