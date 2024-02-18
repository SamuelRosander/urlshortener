import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from os import environ


def setup_db():
    HOST = environ["COSMOS_HOST"]
    MASTER_KEY = environ["COSMOS_MASTER_KEY"]
    DATABASE_ID = "urlshortener"
    CONTAINER_ID = "links"
    CONTAINER_ID2 = "users"
    container = {}

    client = cosmos_client.CosmosClient(
        HOST, {'masterKey': MASTER_KEY},
        user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)

    try:
        db = client.create_database(id=DATABASE_ID)
        print('Database with id \'{0}\' created'.format(DATABASE_ID))
    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(DATABASE_ID)
        print('Database with id \'{0}\' was found'.format(DATABASE_ID))

    try:
        container["links"] = db.create_container(
            id=CONTAINER_ID,
            partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID))
    except exceptions.CosmosResourceExistsError:
        container["links"] = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    try:
        container["users"] = db.create_container(
            id=CONTAINER_ID2,
            partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID2))
    except exceptions.CosmosResourceExistsError:
        container["users"] = db.get_container_client(CONTAINER_ID2)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID2))

    return container
