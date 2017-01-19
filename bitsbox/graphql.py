from flask import Blueprint, render_template
from flask_graphql import GraphQLView
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from .model import (
    db, Layout as LayoutModel, Cabinet as CabinetModel
)

class Cabinet(SQLAlchemyObjectType):
    class Meta:
        model = CabinetModel
        interfaces = (relay.Node, )

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_cabinets = SQLAlchemyConnectionField(Cabinet)

schema = graphene.Schema(query=Query)

graphql_blueprint = Blueprint('graphql', __name__)
graphql_blueprint.add_url_rule(
    '/', 'graphql', view_func=GraphQLView.as_view('graphql', schema=schema))

graphiql_blueprint = Blueprint(
    'graphiql', __name__, static_folder='static/graphiql',
    static_url_path='/static',
    template_folder='templates/graphiql')

@graphiql_blueprint.route('/')
def index():
    return render_template('index.html')
