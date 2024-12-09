from azure.cosmos import exceptions
# from modules.db.db_connectivity import database
from modules.utils.generate_log_file import logger

def insert_into_azure_cosmos(item,container_name,partition_key_name,container_id_name):
    try:
        container = database.get_container_client(container_name)
        
        # Check if the container exists
        try:
            container.read()
            logger.info(f"Container '{container_name}' exists.")
        except exceptions.CosmosResourceNotFoundError:
            # If the container does not exist, create it
            logger.info(f"Container '{container_name}' does not exist. Creating container.")
            container_properties = {
                'id': container_id_name,
                'partition_key': {'paths': [f'/{partition_key_name}']}  # Adjust partition key as necessary
            }
            database.create_container_if_not_exists(**container_properties)
            logger.info(f"Container '{container_name}' created successfully.")

        
        # Insert the item into Cosmos DB container
        logger.info('Insertion item : '+str(item))
        container.create_item(body=item)
        logger.info("Data inserted successfully")
        return True
    except Exception as e:
        logger.exception("Error inserting data : " + str(e))
        return False

def query_item(query,parameters,container_name):
    try:
        container = database.get_container_client(container_name)
        # Execute the query
        query_results = container.query_items(query=query,parameters=parameters,enable_cross_partition_query=True)
        # for i in query_results:
        #     logger.info("Items in quer_results : "+str(i))
        # logger.info("Item queried successfully")
        # logger.info(query_results)
        return query_results
    except Exception as e:
        logger.exception("An error occurred : " + str(e))
        return None

def patch_item(patch_list,patch_item_id,partition_key_value,container_name):
    try:
        container = database.get_container_client(container_name)
        container.patch_item(item=patch_item_id, partition_key=partition_key_value, patch_operations=patch_list)
        patched_item = container.read_item(item=patch_item_id, partition_key=partition_key_value)
        logger.info("Item patched successfully")
        return patched_item
    except Exception as e:
        logger.exception("An error occurred : " + str(e))
        return None

def upsert_item(item_id, upsertData,partition_key, container_name):
    try:
        container = database.get_container_client(container_name)
        upserted_item = container.upsert_item({'id': item_id,'partition_key':partition_key, **upsertData})
        logger.info("Item upserted successfully")
        return upserted_item
    except Exception as e:
        logger.exception("An error occurred : " + str(e))
        return None

def delete_item(item_id, partition_key, container_name):
    try:
        container = database.get_container_client(container_name)
        container.delete_item(item=item_id, partition_key=partition_key)
        return True
    except Exception as e:
        logger.exception("An error occurred while deleting item: " + str(e))
        return None



