import colander
import deform.widget

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('substanced')

class CSRFToken(colander.SchemaNode):

    schema_type = colander.String
    widget = deform.widget.HiddenWidget()
    
    def validator(self, node, value):
        request = self.bindings['request']
        token = request.session.get_csrf_token()
        if value != token:
            raise colander.Invalid(
                node,
                _('Invalid cross-site scripting token'),
                value
                )

    def after_bind(self, node, kw):
        token = kw['request'].session.get_csrf_token()
        self.default = token
        
class RemoveCSRFMapping(colander.Mapping):
    def deserialize(self, node, cstruct):
        result = colander.Mapping.deserialize(self, node, cstruct)
        if result is colander.null:
            return result
        result.pop('_csrf_token_', None)
        return result
                   
class Schema(colander.Schema):
    """
    A ``colander.Schema`` subclass which generates and validates a CSRF token
    automatically.  You must use it like so:

    .. code-block:: python

      from substanced.schema import Schema
      import colander

      class MySchema(Schema):
          my_value = colander.SchemaNode(colander.String())

      And in your application code, *bind* the schema, passing the request
      as a keyword argument:

      .. code-block:: python

        def aview(request):
            schema = MySchema().bind(request=request)

      In order for the CRSFSchema to work, you must configure a *session
      factory* in your Pyramid application.  This is usually done by
      Substance D itself, but may not be done for you in extremely custom
      configurations.
    """
    schema_type = RemoveCSRFMapping
    _csrf_token_ = CSRFToken()
