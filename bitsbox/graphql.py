from flask import Blueprint, render_template
from flask_graphql import GraphQLView
import graphene
from graphene import relay

from sqlalchemy.orm import joinedload

from graphene_sqlalchemy import (
    SQLAlchemyObjectType, SQLAlchemyConnectionField, get_session
)
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

#    @classmethod
#    def get_query(cls, context):
#        return CollectionModel.query.options(
#            joinedload(CollectionModel.drawer))

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    layouts = SQLAlchemyConnectionField(Layout)
    cabinets = SQLAlchemyConnectionField(Cabinet)
    collections = SQLAlchemyConnectionField(Collection)

#    cabinets_by_name = SQLAlchemyConnectionField(
#        Cabinet, name=graphene.String())
#
#    def resolve_cabinets_by_name(self, args, context, info):
#        return CabinetModel.query.filter(CabinetModel.name==args['name'])

class CreateCabinet(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        layout_id = relay.GlobalID(required=True)

    cabinet = graphene.Field(Cabinet)

    @classmethod
    def mutate_and_get_payload(cls, input, context, info):
        name = input.get('name', '')
        if name == '':
            raise ValueError('name must not be blank')

        node = relay.Node.get_node_from_global_id(
            input.get('layout_id'), context, info)
        if not isinstance(node, LayoutModel):
            raise ValueError('layout must be specified')

        cabinet = CabinetModel.create_from_layout(
                db.session, layout=node, name=name)
        db.session.commit()

        print(cabinet.id, cabinet.name)

        return CreateCabinet(cabinet=cabinet)

class Mutation(graphene.ObjectType):
    create_cabinet = CreateCabinet.Field()

schema = graphene.Schema(
    query=Query, mutation=Mutation,
)

graphql_blueprint = Blueprint('graphql', __name__)
graphql_blueprint.add_url_rule(
    '/', 'graphql', view_func=GraphQLView.as_view('graphql', schema=schema))

graphiql_blueprint = Blueprint(
    'graphiql', __name__, template_folder='templates/graphiql')

@graphiql_blueprint.route('/')
def index():
    return render_template('graphiql.html')
