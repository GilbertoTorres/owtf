from marshmallow import Schema, fields

class WriteReportSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    content = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

wreport_schema = WriteReportSchema()

