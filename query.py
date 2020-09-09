import logging
import os
import pymysql

from decimal import Decimal
from dotenv import load_dotenv

from utils.constants import DBArguments

load_dotenv()
logger = logging.getLogger('utils.utils')


class DBQuery:
    _CURSOR_CLASS = pymysql.cursors.DictCursor
    _CHARSET = 'utf8mb4'
    _DB_CONNECTION = pymysql.connect(
        host=os.getenv(DBArguments.HOST),
        user=os.getenv(DBArguments.DB_USER),
        password=os.getenv(DBArguments.PASSWORD),
        db=os.getenv(DBArguments.DB),
        charset=_CHARSET,
        cursorclass=_CURSOR_CLASS
    )

    _GET_RUN_DATA_FOR_SPECIFIC_TIMESTAMP = """
    SELECT 
        gpsLat AS gps_lat,
        gpsLong AS gps_long,
        speed AS gps_speed,
        Timestamp AS timestamp,
        gpsSatNum AS gps_sat_num,
        gpsPosError AS gps_position_error
    FROM
        driverlapsrundata
    WHERE
        Timestamp >= %(start_time)s
            AND Timestamp <= %(end_time)s
    ORDER BY Timestamp ASC
    """

    @classmethod
    def get_run_data_by_time_range(cls, start_time, end_time):
        logger.info("Querying data")

        query = cls._GET_RUN_DATA_FOR_SPECIFIC_TIMESTAMP
        query_arguments = {'start_time': start_time, 'end_time': end_time}

        data = cls._execute_query(query, **query_arguments)
        cls._cast_decimal_to_float(data)

        logger.info("Done Querying data")
        return data

    @classmethod
    def _execute_query(cls, query, **query_arguments):
        cursor = cls._DB_CONNECTION.cursor()
        cursor.execute(query, query_arguments)

        data = cursor.fetchall()
        cursor.close()

        return data

    @staticmethod
    def _cast_decimal_to_float(data_rows_list):
        for data_row in data_rows_list:
            for key in data_row:
                value = data_row[key]
                if type(value) is Decimal:
                    data_row[key] = float(value)
