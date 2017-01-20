from flask import Blueprint, render_template
from flask_graphql import GraphQLView
import graphene
from graphene import relay

from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene_sqlalchemy.converter import (
    convert_sqlalchemy_type, convert_json_to_string
)

from .model import (
    db, Layout as LayoutModel, Cabinet as CabinetModel,
    LayoutItem as LayoutItemModel, Location as LocationModel,
    Drawer as DrawerModel, Collection as CollectionModel,
    JSONEncodedDict
)

# Tell graphene sqlalchemy about our custom JSON type
convert_sqlalchemy_type.register(JSONEncodedDict)(convert_json_to_string)

class Cabinet(SQLAlchemyObjectType):
    class Meta:
        model = CabinetModel
        interfaces = (relay.Node, )

class Layout(SQLAlchemyObjectType):
    class Meta:
        model = LayoutModel
        interfaces = (relay.Node, )

class LayoutItem(SQLAlchemyObjectType):
    class Meta:
        model = LayoutItemModel
        interfaces = (relay.Node, )

class Location(SQLAlchemyObjectType):
    class Meta:
        model = LocationModel
        interfaces = (relay.Node, )

class Drawer(SQLAlchemyObjectType):
    class Meta:
        model = DrawerModel
        interfaces = (relay.Node, )

class Collection(SQLAlchemyObjectType):
    class Meta:
        model = CollectionModel
        interfaces = (relay.Node, )

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_cabinets = SQLAlchemyConnectionField(Cabinet)
    all_collections = SQLAlchemyConnectionField(Collection)
    cabinets_by_name = SQLAlchemyConnectionField(
        Cabinet, name=graphene.String())

    def resolve_cabinets_by_name(self, args, context, info):
        return CabinetModel.query.filter(CabinetModel.name==args['name'])

schema = graphene.Schema(
    query=Query,
    types=[Query, Cabinet, Layout, Location, LayoutItem, Drawer, Collection]
)

graphql_blueprint = Blueprint('graphql', __name__)
graphql_blueprint.add_url_rule(
    '/', 'graphql', view_func=GraphQLView.as_view('graphql', schema=schema))

graphiql_blueprint = Blueprint(
    'graphiql', __name__, static_folder='graphiql/static',
    template_folder='graphiql/templates')

@graphiql_blueprint.route('/')
def index():
    return render_template('graphiql.html')
