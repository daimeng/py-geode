import graphene

class Query(graphene.ObjectType):
    async def resolve_hello(self):
        pass

schema = graphene.Schema(query=Query)
