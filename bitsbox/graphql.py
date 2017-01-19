import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from .models import (
    db_session, Layout as LayoutModel, Cabinet as CabinetModel
)

class Layout(SQLAlchemyObjectType):
    class Meta:
        model = LayoutModel
        interfaces = (relay.Node, )

class Cabinet(SQLAlchemyObjectType):
    class Meta:
        model = CabinetModel
        interfaces = (relay.Node, )

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_cabinets = SQLAlchemyConnectionField(Cabinet)
    all_layouts = SQLAlchemyConnectionField(Cabinet)

schema = graphene.Schema(query=Query)

