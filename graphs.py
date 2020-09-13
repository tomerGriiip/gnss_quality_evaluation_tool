import logging
import matplotlib.pyplot as plt

from pathlib import Path
from statistics import pstdev

from utils.constants import PlotConsts, DataRowsHeaders, GeneralConsts, LONG_TO_LAT_PATH, TIME_TO_SPEED_PATH, \
    TIME_TO_DELTA_TIME_PATH

logger = logging.getLogger('utils.utils')


class GraphsBuilder:
    def __init__(self, start_time, end_time, upload_graphs):
        self.start_time = start_time
        self.end_time = end_time
        self.upload_graphs = upload_graphs

    def plot_long_to_lat(self, data_rows_list):
        plt.figure()
        graph_name = 'Longitude to Latitude'
        plt.title(graph_name)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True)

        data = {
            PlotConsts.GPS_LONG_FINE: [],
            PlotConsts.GPS_LAT_FINE: [],
            PlotConsts.GPS_LONG_ERROR: [],
            PlotConsts.GPS_LAT_ERROR: []
        }
        for data_row in data_rows_list:
            if data_row.get(GeneralConsts.SPEED_ERROR):
                data[PlotConsts.GPS_LONG_ERROR].append(data_row[DataRowsHeaders.GPS_LONG])
                data[PlotConsts.GPS_LAT_ERROR].append(data_row[DataRowsHeaders.GPS_LAT])
            else:
                data[PlotConsts.GPS_LONG_FINE].append(data_row[DataRowsHeaders.GPS_LONG])
                data[PlotConsts.GPS_LAT_FINE].append(data_row[DataRowsHeaders.GPS_LAT])

        logger.info("Creating Longitude to Latitude graph")
        # Changes the color of each coordinate from light blue to deep blue according to the progress.
        color_change = len(data[PlotConsts.GPS_LONG_FINE])
        plt.scatter(
            data[PlotConsts.GPS_LONG_FINE], data[PlotConsts.GPS_LAT_FINE], s=1, c=range(color_change), cmap='Blues'
        )
        plt.scatter(data[PlotConsts.GPS_LONG_ERROR], data[PlotConsts.GPS_LAT_ERROR], s=1, color='r')

        self._upload_to_drive(LONG_TO_LAT_PATH, graph_name)

        plt.show()

    def plot_time_to_speed(self, data_rows_list):
        plt.figure()
        graph_name = 'Time to Speed'
        plt.title(graph_name)
        plt.xlabel('Time')
        plt.ylabel('Speed')
        plt.grid(True)

        data = {
            PlotConsts.CALCULATED_SPEED_FINE: [],
            PlotConsts.CALCULATED_SPEED_FINE_TIME: [],
            PlotConsts.CALCULATED_SPEED_ERROR: [],
            PlotConsts.CALCULATED_SPEED_ERROR_TIME: [],
            PlotConsts.GPS_SPEED: [],
            PlotConsts.GPS_SPEED_TIME: [],
        }
        for index, data_row in enumerate(data_rows_list):
            if index == 0:
                continue

            if data_row.get(GeneralConsts.SPEED_ERROR):
                data[PlotConsts.CALCULATED_SPEED_ERROR].append(data_row[GeneralConsts.CALCULATED_SPEED])
                data[PlotConsts.CALCULATED_SPEED_ERROR_TIME].append(data_row[GeneralConsts.TOTAL_TIME])
            else:
                data[PlotConsts.CALCULATED_SPEED_FINE].append(data_row[GeneralConsts.CALCULATED_SPEED])
                data[PlotConsts.CALCULATED_SPEED_FINE_TIME].append(data_row[GeneralConsts.TOTAL_TIME])

            data[PlotConsts.GPS_SPEED].append(data_row[DataRowsHeaders.GPS_SPEED])
            data[PlotConsts.GPS_SPEED_TIME].append(data_row[GeneralConsts.TOTAL_TIME])

        logger.info("Creating Time to Speed graph")
        plt.scatter(data[PlotConsts.GPS_SPEED_TIME], data[PlotConsts.GPS_SPEED], s=1, color='b')
        plt.scatter(data[PlotConsts.CALCULATED_SPEED_FINE_TIME], data[PlotConsts.CALCULATED_SPEED_FINE], s=1, color='g')
        plt.scatter(
            data[PlotConsts.CALCULATED_SPEED_ERROR_TIME], data[PlotConsts.CALCULATED_SPEED_ERROR], s=1, color='r'
        )

        self._upload_to_drive(TIME_TO_SPEED_PATH, graph_name)

        plt.show()

    def plot_time_to_time_delta(self, data_rows_list):
        plt.figure()
        graph_name = 'Time to Delta-Time'
        plt.xlabel('Time')
        plt.ylabel('Delta-Time')
        plt.grid(True)

        data = {
            PlotConsts.CALCULATED_DELTA_TIME: [],
            PlotConsts.CALCULATED_DELTA_TIME_TIME: [],
            PlotConsts.CALCULATED_DELTA_TIME_ERROR: [],
            PlotConsts.CALCULATED_DELTA_TIME_ERROR_TIME: [],
        }
        for index, data_row in enumerate(data_rows_list):
            if index == 0:
                continue

            if data_row.get(GeneralConsts.TIME_ERROR):
                data[PlotConsts.CALCULATED_DELTA_TIME_ERROR].append(data_row[GeneralConsts.CALCULATED_DELTA_TIME])
                data[PlotConsts.CALCULATED_DELTA_TIME_ERROR_TIME].append(data_row[GeneralConsts.TOTAL_TIME])
            else:
                data[PlotConsts.CALCULATED_DELTA_TIME].append(data_row[GeneralConsts.CALCULATED_DELTA_TIME])
                data[PlotConsts.CALCULATED_DELTA_TIME_TIME].append(data_row[GeneralConsts.TOTAL_TIME])

        logger.info("Creating Time to Delta-Time graph")
        plt.scatter(data[PlotConsts.CALCULATED_DELTA_TIME_TIME], data[PlotConsts.CALCULATED_DELTA_TIME], s=1, color='b')
        plt.scatter(
            data[PlotConsts.CALCULATED_DELTA_TIME_ERROR_TIME],
            data[PlotConsts.CALCULATED_DELTA_TIME_ERROR],
            s=1,
            color='r'
        )

        # Calculate the standard deviation of the Delta-Time
        standard_deviation = round(pstdev(data[PlotConsts.CALCULATED_DELTA_TIME]), 10)
        plt.title(graph_name + ' - Standard Deviation: ' + str(standard_deviation))

        self._upload_to_drive(TIME_TO_DELTA_TIME_PATH, graph_name)

        plt.show()

    def _upload_to_drive(self, path_to_upload_to, graph_name):
        if Path(path_to_upload_to).exists() and self.upload_graphs:
            file_name_path = path_to_upload_to + '{} - {}.png'.format(self.start_time, self.end_time)

            logger.info("Uploading {} graph to google drive".format(graph_name))
            plt.savefig(fname=file_name_path, dpi=1200, format='png')
