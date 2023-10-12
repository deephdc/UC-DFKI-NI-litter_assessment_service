from webargs import validate
from marshmallow import Schema, fields

class PredictArgsSchema(Schema):
    class Meta:
        ordered = True

    input= fields.Field(
        required=True,
        type="file",
        location="form",
        description="Input the image you want to analyse")

    PLD_plot = fields.Bool(
        required = False,
        load_default=True,
        metadata={"enum": [True, False]})

    PLQ_plot = fields.Bool(
        required = False,
        load_default=True,
        metadata={"enum": [True, False]})

    accept = fields.Str(
        location="headers",
        validate=validate.OneOf(['zip']),
        description='Returns zip file with results')

if __name__=='__main__':
    args=PredictArgsSchema()
