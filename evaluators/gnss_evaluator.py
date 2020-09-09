import logging

from geopy.distance import geodesic

from utils.constants import DataRowsHeaders, GeneralConsts


logger = logging.getLogger('utils.utils')


class GNSSEvaluator:
    def __init__(self, min_speed_threshold=10, speed_error_threshold=0.3):
        self.min_speed_threshold = min_speed_threshold
        self.speed_error_threshold = speed_error_threshold

    _KMH_TO_MS = 3600 / 1000

    def evaluate(self, data_rows_list):
        logger.info("Starting to evaluate GNSS data")
        if data_rows_list:
            previous_lat = data_rows_list[0][DataRowsHeaders.GPS_LAT]
            previous_long = data_rows_list[0][DataRowsHeaders.GPS_LONG]
            previous_timestamp = data_rows_list[0][DataRowsHeaders.TIMESTAMP]
            session_start_time = data_rows_list[0][DataRowsHeaders.TIMESTAMP]

            data_rows_list[0][GeneralConsts.TOTAL_TIME] = 0
        else:
            raise Exception("No data found in the provided time range")

        logger.info(
            "Starting to mark data rows with speed error, speed_error_threshold = {}".format(self.speed_error_threshold)
        )
        for row_index, data_row in enumerate(data_rows_list[1:], start=1):
            current_lat = data_row[DataRowsHeaders.GPS_LAT]
            current_long = data_row[DataRowsHeaders.GPS_LONG]
            current_timestamp = data_row[DataRowsHeaders.TIMESTAMP]

            delta_distance = geodesic((previous_lat, previous_long), (current_lat, current_long)).m
            delta_time = self._calculate_delta_time(current_timestamp, previous_timestamp)

            total_time = self._calculate_delta_time(current_timestamp, session_start_time)
            data_row[GeneralConsts.TOTAL_TIME] = total_time

            calculated_speed = self._calculate_delta_distance_to_delta_time(delta_distance, delta_time)
            data_row[GeneralConsts.CALCULATED_SPEED] = calculated_speed

            self._check_speed_error(data_row, calculated_speed, row_index)
            previous_lat, previous_long, previous_timestamp = current_lat, current_long, current_timestamp

        logger.info("Done marking data rows with speed error")
        logger.info("Done evaluating GNSS data")
        return data_rows_list

    @staticmethod
    def _calculate_delta_time(current_timestamp, older_timestamp):
        return (current_timestamp - older_timestamp).total_seconds()

    def _calculate_delta_distance_to_delta_time(self, delta_distance, delta_time):
        if delta_time > 0:
            return (delta_distance / delta_time) * self._KMH_TO_MS

        # Avoid division by zero, this data row will probably be marked as an error later on
        return 9999999999

    def _check_speed_error(self, data_row, calculated_speed, row_index):
        gps_speed = data_row[DataRowsHeaders.GPS_SPEED]

        if gps_speed > self.min_speed_threshold:
            speed_error = abs(gps_speed - calculated_speed) / gps_speed
            if speed_error > self.speed_error_threshold:
                logger.info("Speed error found for data row: {}, speed_error = {}, speed_error_threshold = {}".format(
                    row_index, speed_error, self.speed_error_threshold)
                )
                data_row[GeneralConsts.SPEED_ERROR] = True
