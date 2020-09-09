class DataRowsHeaders:
    GPS_SPEED = 'gps_speed'
    GPS_LAT = 'gps_lat'
    GPS_LONG = 'gps_long'
    TIMESTAMP = 'timestamp'
    GPS_SAT_NUM = 'gps_sat_num'
    GPS_POSITION_ERROR = 'gps_position_error'


class GeneralConsts:
    SPEED_ERROR = 'speed_error'
    TIME_ERROR = 'time_error'
    TOTAL_TIME = 'total_time'
    CALCULATED_SPEED = 'calculated_speed'
    CALCULATED_DELTA_TIME = 'delta_time'


class PlotConsts:
    # Longitude to Latitude graph
    GPS_LONG_FINE = 'gps_long_fine'
    GPS_LAT_FINE = 'gps_lat_fine'
    GPS_LONG_ERROR = 'gps_long_error'
    GPS_LAT_ERROR = 'gps_lat_error'

    # Time to Speed graph
    CALCULATED_SPEED_FINE = "calculated_speed_fine"
    CALCULATED_SPEED_FINE_TIME = "calculated_speed_fine_time"
    CALCULATED_SPEED_ERROR = "calculated_speed_error"
    CALCULATED_SPEED_ERROR_TIME = "calculated_speed_error_time"
    GPS_SPEED = "gps_speed"
    GPS_SPEED_TIME = "gps_speed_time"

    # Time to Delta-Time graph
    CALCULATED_DELTA_TIME = "calculated_time_delta"
    CALCULATED_DELTA_TIME_TIME = "calculated_time_delta_time"
    CALCULATED_DELTA_TIME_ERROR = "calculated_time_delta_error"
    CALCULATED_DELTA_TIME_ERROR_TIME = "calculated_time_delta_time_error"



class DBArguments:
    HOST = 'HOST'
    DB_USER = 'DB_USER'
    PASSWORD = 'PASSWORD'
    DB = 'DB'


STRFTIME_COLON_SEPARATED = '%Y-%m-%d %H:%M:%S'
STRFTIME_DASH_SEPARATED = '%Y-%m-%d %H-%M-%S'


LONG_TO_LAT_PATH = 'G:/Shared drives/Technologies/Development/GNSS Quality Evaluation graphs/Longitude to Latitude/'
TIME_TO_SPEED_PATH = 'G:/Shared drives/Technologies/Development/GNSS Quality Evaluation graphs/Time to Speed/'
TIME_TO_DELTA_TIME_PATH = 'G:/Shared drives/Technologies/Development/GNSS Quality Evaluation graphs/Time to Delta Time/'
