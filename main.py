import os
import pymysql

from constants import DataRowNames, DBArguments, LONG_TO_LAT_PATH, TIME_TO_SPEED_PATH
from utils import initialize_logger

from datetime import datetime
from pathlib import Path
from decimal import Decimal
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from math import sin, cos, sqrt, atan2, radians

START_TIME = '2020-09-04 08:14:00'
END_TIME = '2020-09-04 08:25:40'


load_dotenv()
logger = initialize_logger()


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
        query = cls._GET_RUN_DATA_FOR_SPECIFIC_TIMESTAMP
        query_arguments = {'start_time': start_time, 'end_time': end_time}

        data = cls._execute_query(query, **query_arguments)
        cls._cast_decimal_to_float(data)

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


class DataEvaluator:
    def __init__(self, min_speed_threshold=10, speed_error_threshold=0.3, kmh_to_ms=3600/1000):
        self.min_speed_threshold = min_speed_threshold
        self.speed_error_threshold = speed_error_threshold
        self.kmh_to_ms = kmh_to_ms

    def run(self, data_rows_list):
        if data_rows_list:
            previous_lat = data_rows_list[0][DataRowNames.GPS_LAT]
            previous_long = data_rows_list[0][DataRowNames.GPS_LONG]
            previous_timestamp = data_rows_list[0][DataRowNames.TIMESTAMP]
            session_start_time = data_rows_list[0][DataRowNames.TIMESTAMP]

            data_rows_list[0][DataRowNames.TOTAL_TIME] = 0
        else:
            raise Exception("No data found in the provided time range")

        for row_index, data_row in enumerate(data_rows_list[1:], start=1):
            current_lat = data_row[DataRowNames.GPS_LAT]
            current_long = data_row[DataRowNames.GPS_LONG]
            current_timestamp = data_row[DataRowNames.TIMESTAMP]

            delta_distance = self._calculate_delta_distance(previous_lat, previous_long, current_lat, current_long)
            delta_time = self._calculate_delta_time(current_timestamp, previous_timestamp)

            total_time = self._calculate_delta_time(current_timestamp, session_start_time)
            data_row[DataRowNames.TOTAL_TIME] = total_time

            calculated_speed = self._calculate_delta_distance_to_delta_time(delta_distance, delta_time)
            data_row[DataRowNames.CALCULATED_SPEED] = calculated_speed

            self._check_speed_error(data_row, calculated_speed, row_index)
            previous_lat, previous_long, previous_timestamp = current_lat, current_long, current_timestamp

        return data_rows_list

    @staticmethod
    def _calculate_delta_distance(previous_lat, previous_long, current_lat, current_long):
        radius = 6373.0

        previous_lat = radians(previous_lat)
        previous_long = radians(previous_long)
        current_lat = radians(current_lat)
        current_long = radians(current_long)

        longitude_distance = current_long - previous_long
        latitude_distance = current_lat - previous_lat

        a = sin(latitude_distance / 2) ** 2 + cos(previous_lat) * cos(current_lat) * sin(longitude_distance / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return radius * c * 1000

    @staticmethod
    def _calculate_delta_time(current_timestamp, older_timestamp):
        return (current_timestamp - older_timestamp).total_seconds()

    def _calculate_delta_distance_to_delta_time(self, delta_distance, delta_time):
        if delta_time > 0:
            return (delta_distance / delta_time) * self.kmh_to_ms

        return 9999999999

    def _check_speed_error(self, data_row, calculated_speed, row_index):
        gps_speed = data_row[DataRowNames.GPS_SPEED]

        if gps_speed > self.min_speed_threshold:
            speed_error = abs(gps_speed - calculated_speed) / gps_speed
            if speed_error > self.speed_error_threshold:
                logger.info("Speed error found for data row: {}, speed_error = {}, speed_error_threshold = {}".format(
                    row_index, speed_error, self.speed_error_threshold)
                )
                data_row[DataRowNames.SPEED_ERROR] = True


def _plot_long_to_lat(data_rows_list):
    plt.figure()
    plt.title = 'Longitude to Latitude'
    plt.xlabel('Long')
    plt.ylabel('Lat')
    plt.grid(True)

    data = {"gps_long_fine": [], "gps_lat_fine": [], "gps_long_error": [], "gps_lat_error": []}
    for data_row in data_rows_list:
        if data_row.get(DataRowNames.SPEED_ERROR):
            data["gps_long_error"].append(data_row[DataRowNames.GPS_LONG])
            data["gps_lat_error"].append(data_row[DataRowNames.GPS_LAT])
        else:
            data["gps_long_fine"].append(data_row[DataRowNames.GPS_LONG])
            data["gps_lat_fine"].append(data_row[DataRowNames.GPS_LAT])
    plt.scatter(data['gps_long_fine'], data['gps_lat_fine'], s=1, c=range(0, len(data['gps_long_fine'])), cmap='Blues')
    plt.scatter(data['gps_long_error'], data['gps_lat_error'], s=1, color='r')

    if Path(LONG_TO_LAT_PATH).exists():
        start_time = datetime.strptime(START_TIME, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H-%M-%S')
        end_time = datetime.strptime(END_TIME, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H-%M-%S')
        file_name_path = LONG_TO_LAT_PATH + '{} - {}.png'.format(start_time, end_time)
        plt.savefig(fname=file_name_path, dpi=1200)

    plt.show()


def _plot_time_to_speed(data_rows_list):
    plt.figure()
    plt.title = 'Time to Speed'
    plt.xlabel('Time')
    plt.ylabel('Speed')
    plt.grid(True)

    data = {
        "calculated_speed_fine": [],
        "calculated_speed_fine_time": [],
        "calculated_speed_error": [],
        "calculated_speed_error_time": [],
        "gps_speed": [],
        "gps_speed_time": [],
    }
    for index, data_row in enumerate(data_rows_list):
        if index == 0:
            continue

        if data_row.get(DataRowNames.SPEED_ERROR):
            data["calculated_speed_error"].append(data_row[DataRowNames.CALCULATED_SPEED])
            data["calculated_speed_error_time"].append(data_row[DataRowNames.TOTAL_TIME])
        else:
            data["calculated_speed_fine"].append(data_row[DataRowNames.CALCULATED_SPEED])
            data["calculated_speed_fine_time"].append(data_row[DataRowNames.TOTAL_TIME])

        data["gps_speed"].append(data_row[DataRowNames.GPS_SPEED])
        data["gps_speed_time"].append(data_row[DataRowNames.TOTAL_TIME])

    plt.scatter(data['gps_speed_time'], data['gps_speed'], s=1, color='b')
    plt.scatter(data['calculated_speed_fine_time'], data['calculated_speed_fine'], s=1, color='g')
    plt.scatter(data['calculated_speed_error_time'], data['calculated_speed_error'], s=1, color='r')

    if Path(TIME_TO_SPEED_PATH).exists():
        start_time = datetime.strptime(START_TIME, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H-%M-%S')
        end_time = datetime.strptime(END_TIME, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H-%M-%S')
        file_name_path = TIME_TO_SPEED_PATH + '{} - {}.png'.format(start_time, end_time)
        plt.savefig(fname=file_name_path, dpi=1200)

    plt.show()


if __name__ == '__main__':
    run_data_by_time_range = DBQuery().get_run_data_by_time_range(start_time=START_TIME, end_time=END_TIME)
    evaluated_run_data = DataEvaluator().run(data_rows_list=run_data_by_time_range)
    _plot_long_to_lat(evaluated_run_data)
    _plot_time_to_speed(evaluated_run_data)
