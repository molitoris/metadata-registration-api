from flask_restplus import Namespace, Resource, fields
from flask_restplus import reqparse, inputs

from api_service.model import Property
from api_service.api.api_ctrl_voc import ctrl_voc_model_id
from api_service.api.decorators import token_required


api = Namespace('Properties', description='Property related operations')

# ----------------------------------------------------------------------------------------------------------------------

property_add_model = api.model("Add Property", {
    'label': fields.String(description='A human readable description of the entry'),
    'name': fields.String(description='The unique name of the entry (in snake_case)'),
    'level': fields.String(description='The level the property is associated with (e.g. Study, Sample, ...)'),
    'vocabulary_type': fields.String(),
    'synonyms': fields.List(fields.String(description='Alternatives to the primary name')),
    'description': fields.String(description='A detailed description of the intended use', default=''),
    'deprecated': fields.Boolean(default=False)
})

cv_model = api.model("Vocabulary Type", {
    'data_type': fields.String(description="The data type of the entry"),
    'controlled_vocabulary': fields.Nested(ctrl_voc_model_id)
})

property_model = api.model('Property', {
    'label': fields.String(description='A human readable description of the entry'),
    'name': fields.String(description='The unique name of the entry (in snake_case)'),
    'level': fields.String(description='The level the property is associated with (e.g. Study, Sample, ...)'),
    'vocabulary_type': fields.Nested(cv_model),
    'synonyms': fields.List(fields.String(description='Alternatives to the primary name')),
    'description': fields.String(description='A detailed description of the intended use', default=''),
    'deprecated': fields.Boolean(default=False)
})

property_model_id = api.inherit('Property with id', property_model, {
    'id': fields.String(attribute='pk', description='The unique identifier of the entry'),
})


post_response_model = api.model("Post response", {
    'message': fields.String(),
    'id': fields.String(description="Id of inserted entry")
})

# ----------------------------------------------------------------------------------------------------------------------

@api.route('/')
class ApiProperties(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('deprecated',
                            type=inputs.boolean,
                            location="args",
                            default=False,
                            help="Boolean indicator which determines if deprecated entries should be returned as well",
                            )

    @api.marshal_with(property_model_id)
    @api.expect(parser=get_parser)
    def get(self):
        """ Fetch a list with all entries """

        # Convert query parameters
        args = self.get_parser.parse_args()
        include_deprecate = args['deprecated']

        if not include_deprecate:
            entries = Property.objects(deprecated=False).all()
        else:
            # Include entries which are deprecated
            entries = Property.objects().all()
        return list(entries)

    @token_required
    @api.expect(property_add_model)
    @api.response(201, "Success", post_response_model)
    def post(self, user):
        """ Add a new entry

            The name has to be unique and is internally used as a variable name. The passed string is
            preprocessed before it is inserted into the database. Preprocessing: All characters are converted to
            lower case, the leading and trailing white spaces are removed, and intermediate white spaces are replaced
            with underscores ("_").

            Do not pass a unique identifier since it is generated internally.

            synonyms (optional)

            deprecated (default=False)

            If a data type other than "cv" is added, the controlled_vocabullary is not considered.
        """

        entry = Property(**api.payload)

        # Ensure that a passed controlled vocabulary is valid
        validate_controlled_vocabulary(entry)

        entry = entry.save()
        return {"message": "Add entry '{}'".format(entry.name),
                "id": str(entry.id)}, 201


@api.route('/id/<id>')
@api.param('id', 'The property identifier')
class ApiProperty(Resource):

    delete_parser = reqparse.RequestParser()
    delete_parser.add_argument('complete',
                               type=inputs.boolean,
                               default=False,
                               help="Boolean indicator to remove an entry instead of deprecating it (cannot be undone)"
                               )

    @api.marshal_with(property_model_id)
    def get(self, id):
        """Fetch an entry given its unique identifier"""
        return Property.objects(id=id).get()

    @token_required
    @api.expect(property_model)
    def put(self, user, id):
        """ Update entry given its unique identifier """
        entry = Property.objects(id=id).first()
        entry.update(**api.payload)
        return {'message': "Update entry '{}'".format(entry.name)}

    @token_required
    @api.expect(parser=delete_parser)
    def delete(self, user, id):
        """ Deprecates an entry given its unique identifier """

        parser = reqparse.RequestParser()
        parser.add_argument('complete', type=inputs.boolean, default=False)
        args = parser.parse_args()

        force_delete = args['complete']

        entry = Property.objects(id=id).get()
        if not force_delete:
            entry.update(deprecated=True)
            return {'message': "Deprecate entry '{}'".format(entry.name)}
        else:
            entry.delete()
            return {'message': "Delete entry '{}'".format(entry.name)}


def validate_controlled_vocabulary(entry):
    if entry.vocabulary_type and entry.vocabulary_type.data_type != "cv":
        entry.vocabulary_type.controlled_vocabulary = None

