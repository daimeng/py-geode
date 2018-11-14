from starlette.applications import Starlette
from starlette.graphql import GraphQLApp
from starlette.responses import JSONResponse

from graphql.execution.executors.asyncio import AsyncioExecutor
from gql.schema import schema

import uvicorn


app = Starlette()
app.add_route('/', GraphQLApp(schema=schema, executor=AsyncioExecutor()))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
