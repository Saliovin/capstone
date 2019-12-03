from marshmallow import fields, Schema
from sqlalchemy import or_
from . import db


class FileModel(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(128), nullable=False)
    filename = db.Column(db.String(128), nullable=False)
    sha1 = db.Column(db.String(128), nullable=False)
    md5 = db.Column(db.String(128), nullable=False)
    filetype = db.Column(db.String(128), nullable=False)

    def __init__(self, data):
        self.size = data.get('size')
        self.filename = data.get('filename')
        self.sha1 = data.get('sha1')
        self.md5 = data.get('md5')
        self.filetype = data.get('filetype')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_files():
        return FileModel.query.all()

    @staticmethod
    def get_one_file(hash_str):
        return FileModel.query.filter(or_(FileModel.md5 == hash_str,
                                          FileModel.sha1 == hash_str)).first()

    def __repr(self):
        return '<id {}>'.format(self.id)


class FileSchema(Schema):
    id = fields.Int(dump_only=True)
    size = fields.Str(required=True)
    filename = fields.Str(required=True)
    sha1 = fields.Str(required=True)
    md5 = fields.Str(required=True)
    filetype = fields.Str(required=True)
