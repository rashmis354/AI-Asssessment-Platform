from modules.utils.generate_log_file import logger
from config.config import database_type, database_server, database_name, database_username, database_password
import threading
import psycopg2
import os
import datetime



logger.info(f"****** DB type initialization via config has been set to : postgres")

def FormatData(InputList):
    try:
        temp=[]
        for Input in InputList:
            if isinstance(Input, datetime.date):
                temp.append(Input.isoformat())
            else:
                temp.append(Input)
        return tuple(temp)
    except Exception as e:
        return InputList

class DBConnection():
    '''
    Database Connection module
    Author: Hexaware
    Description: To connect with database schemas and manipulate data/ insertion of data.
    '''

    def __init__ (self) :
        """
        Function Name: Class DBConnection Constructor
        Description : This function is used to initialize db credential.
        :Return : None
        """
        # logger.info(f"************************************************************")
        # logger.info(f"*************DB connection initialization start*************")
        # logger.info(f"************************************************************")
        self.database_server = database_server
        self.database_name = database_name
        self.database_username = database_username
        self.database_password = database_password
        # logger.info(f"DB credentials: database_server: {database_server}, database_name: {database_name}, \
        #     db_user_name: {database_username}")
        try:
            if database_type.lower() == 'postgres':
                self.cnxn = psycopg2.connect("dbname="+self.database_name+" user="+self.database_username+" password="+self.database_password+" host="+self.database_server)#+" port="+str(self.port_number))
                # logger.info(f"************************************************************")
                # logger.info(f"***********Connection instance: "+str(self.cnxn)+"************")
                # logger.info(f"************************************************************")

            self.cursor = self.cnxn.cursor()
            # logger.info(f"************************************************************")
            # logger.info(f"***********Cursor instance: "+str(self.cursor)+"************")
            # logger.info(f"************************************************************")
        except Exception as error_message:
            logger.exception("Exception Occured. DB Connection cannot be established! "+str(error_message))


    def execute_query(self, query, query_type, params = None) : #it should be renamed as execute_query, once the modification is done in all files, will replace it all together
        """
        Function Name: Class DBConnection:  executeQuery
        Description : This function is used to execute db query \
             with respct to query type eg: SELECT,UPDATE,INSERT.
        Param : query
        Param : query_type eg: SELECT,UPDATE,INSERT
        Return : Tuple->status,message,result
        """
        # logger.info(f"********************************************logge**********")

        thread_name = threading.current_thread().name
        # logger.info(f"Current execution query thread name: {thread_name}")
        try:
            status,message,result  = False,"Query yet to be executed",None
            logger.info(thread_name+" "+"Query-->"+ str (query))

            # if type(query) != str:
            #     error = "Query type is not of string data type"
            #     logger.exception()
            #     raise Exception(error)


            if query_type.upper() == "SELECT":
                self.cursor.execute(*query)
                self.cnxn.commit()
                output = self.cursor.fetchall()
                columnNames = [column[0] for column in self.cursor.description]
                data = []
                for record in output:
                    data.append(dict(zip(columnNames, record if "datetime" not in str(record) else FormatData(record))))
                status = True
                message = "Query Executed Successfully"
                result = data
                # logger.info("Query execution status ---> "+str(status))
                # logger.info("Message ---> "+str(message))
                # logger.info("Data ---> "+str(data))

            elif query_type.upper() == "INSERT":
                self.cursor.execute(query, params)
                n_records = self.cursor.rowcount
                self.cnxn.commit()
                logger.info(thread_name+" "+"Inserted Rows -- >" + str(n_records))
                status = True
                message = "Query Executed Successfully"
                result = n_records
                # logger.info("Query execution status ---> "+str(status))
                logger.info("Message ---> "+str(message))
                # logger.info("Data ---> "+str(n_records))

            elif query_type.upper() == "UPDATE":
                self.cursor.execute(*query)
                n_records = self.cursor.rowcount
                self.cnxn.commit()
                status = True
                message = "Query Executed Successfully"
                result = n_records
                # logger.info("Query execution status ---> "+str(status))
                logger.info("Message ---> "+str(message))
                # logger.info("Data ---> "+str(n_records))

            elif query_type.upper() == "DELETE":
                logger.info("##############DELETE####################")
                self.cursor.execute(*query)
                n_records = self.cursor.rowcount
                self.cnxn.commit()
                status = True
                message = "Query Executed Successfully"
                result = n_records
                # logger.info("Query execution status ---> "+str(status))
                logger.info("Message ---> "+str(message))
                # logger.info("Data ---> "+str(n_records))

            else:
                status = False
                message = "Invalid Query Type, Cannot execute Query"

            # logger.info(result)
            return status,message,result

        except Exception as error_message:
            logger.exception(thread_name+" "+"Exception Occured while executing the queries-- >"+str(error_message))
            message = "Exception -->{}".format(error_message)
            status = False
            return status,message,result

        # finally:
        #     logger.info(thread_name+" "+"--------DB thread operation done-----." )

    # getConnection and getCursor is used in utils.py for query execution, there as well need to make it how we use this module in rest of the modules, no need to explicitly write logic for query execution
    def getConnection(self):
        thread_name = threading.current_thread().name
        try:
            return self.cnxn
        except Exception as error_message:
            logger.exception(thread_name+" "+"Error while getting connection object -- >"+str(error_message))

    def getCursor(self):
        thread_name = threading.current_thread().name
        try:
            return self.cursor
        except Exception as error_message:
            logger.exception(thread_name+" "+"Error while getting connection object -- >"+str(error_message))


    def close_conn(self):
        thread_name = threading.current_thread().name
        try:
            self.cursor.close()
            self.cnxn.close()
            # logger.info("Connection to DB closed successfully")
        except Exception as error_message:
            logger.exception(thread_name+" "+"Exception occured . Connection cannot be closed -- >"+str(error_message))


if __name__ == '__main__':
    try:
        conn_obj = DBConnection()
        logger.info("Connection Successfull")
        logger.info("Connection is :"+ str(type(conn_obj.cnxn)))
        logger.info("Cursor is :"+ str(type(conn_obj.cursor)))
        conn_obj.closeConn()
    except Exception as error_message:
        logger.exception("Cannot established connection ->"+ str(error_message))