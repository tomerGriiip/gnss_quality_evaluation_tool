import os
import pymysql

from decimal import Decimal
from dotenv import load_dotenv

import matplotlib.pyplot as plt
from math import sin, cos, sqrt, atan2, radians

START_TIME = '2020-09-04 06:20:00'
END_TIME = '2020-09-04 07:58:29'


load_dotenv()


class DBQuery:
    _CURSOR_CLASS = pymysql.cursors.DictCursor
    _DB_CONNECTION = pymysql.connect(
        host=os.getenv('HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('PASSWORD'),
        db=os.getenv('DB'),
        charset=os.getenv('CHARSET'),
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
    def __init__(self, min_speed_threshold=10, speed_error_threshold=0.5, kmh_to_ms=3600/1000):
        self.min_speed_threshold = min_speed_threshold
        self.speed_error_threshold = speed_error_threshold
        self.kmh_to_ms = kmh_to_ms

    def run(self, data_rows_list):
        if data_rows_list:
            previous_lat = data_rows_list[0]['gps_lat']
            previous_long = data_rows_list[0]['gps_long']
            previous_timestamp = data_rows_list[0]['timestamp']
        else:
            raise Exception("No data fount in the provided time range")

        for data_row in data_rows_list[1:]:
            current_lat = data_row['gps_lat']
            current_long = data_row['gps_long']
            current_timestamp = data_row['timestamp']

            delta_distance = self._calculate_delta_distance(previous_lat, previous_long, current_lat, current_long)
            delta_time = self._calculate_delta_time(current_timestamp, previous_timestamp)

            if delta_time > 0:
                calculated_speed = self._calculate_delta_distance_to_delta_time(delta_distance, delta_time)
            else:
                calculated_speed = 99999999

            self._check_speed_error(data_row, calculated_speed)
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
    def _calculate_delta_time(current_timestamp, previous_timestamp):
        return (current_timestamp - previous_timestamp).total_seconds()

    def _calculate_delta_distance_to_delta_time(self, delta_distance, delta_time):
        return (delta_distance / delta_time) * self.kmh_to_ms

    def _check_speed_error(self, data_row, calculated_speed):
        gps_speed = data_row['gps_speed']

        if gps_speed > self.min_speed_threshold:
            speed_error = abs(gps_speed - calculated_speed) / gps_speed
            if speed_error > self.speed_error_threshold:
                data_row['speed_error'] = True


def plot(data_rows_list):
    plt.figure()
    plt.title = 'Longitude to Latitude'
    plt.xlabel('Long')
    plt.ylabel('Lat')
    plt.grid(True)

    x_cor_min = 0.995 * (data_rows_list[0]['gps_long'])
    x_cor_max = 1.005 * (data_rows_list[len(data_rows_list) - 1]['gps_long'])
    y_cor_min = 0.995 * (data_rows_list[0]['gps_lat'])
    y_cor_max = 1.005 * (data_rows_list[len(data_rows_list) - 1]['gps_lat'])
    print(x_cor_min, x_cor_max, y_cor_min, y_cor_max)
    plt.xlim(x_cor_min, x_cor_max)
    plt.ylim(y_cor_min, y_cor_max)

    data = {"x_fine": [], "y_fine": [], "x_error": [], "y_error": []}
    for data_row in data_rows_list:
        if data_row.get('speed_error'):
            data["x_error"].append(data_row['gps_long'])
            data["y_error"].append(data_row['gps_lat'])
        else:
            data["x_fine"].append(data_row['gps_long'])
            data["y_fine"].append(data_row['gps_lat'])
    plt.scatter(data['x_fine'], data['y_fine'], s=1, color='b')
    plt.scatter(data['x_error'], data['y_error'], s=1, color='r')

    plt.show()


if __name__ == '__main__':
    raw_data_from_db = DBQuery().get_run_data_by_time_range(start_time=START_TIME, end_time=END_TIME)
    evaluated_data = DataEvaluator().run(data_rows_list=raw_data_from_db)
    plot(evaluated_data)
