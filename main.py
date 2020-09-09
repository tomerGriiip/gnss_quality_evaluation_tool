import argparse

from utils.constants import STRFTIME_COLON_SEPARATED, STRFTIME_DASH_SEPARATED
from evaluators.gnss_evaluator import GNSSEvaluator
from graphs import GraphsBuilder
from query import DBQuery
from utils.utils import initialize_logger, convert_strftime_format


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    "-s",
    "--start_time",
    help="The beginning of the data's time frame, format for example: -s \"2020-09-04 08:14:00\"",
    dest="start_time",
    required=True,
)
parser.add_argument(
    "-e",
    "--end_time",
    help="The end of the data's time frame, format for example: -e \"2020-09-04 08:25:40\"",
    dest="end_time",
    required=True,
)
parser.add_argument(
    "-u",
    "--upload_graphs",
    help="A flag for whether upload the graphs to google drive or not, default is False",
    dest="upload_graphs",
    default=False,
)
args = parser.parse_args()


if __name__ == '__main__':
    logger = initialize_logger()
    logger.info("Starting to evaluate data for time range {} -> {}".format(args.start_time, args.end_time))

    # Get the data
    run_data_by_time_range = DBQuery().get_run_data_by_time_range(start_time=args.start_time, end_time=args.end_time)

    # Evaluate GNSS data for each data row
    evaluated_run_data = GNSSEvaluator().evaluate(run_data_by_time_range)

    converted_start_time = convert_strftime_format(args.start_time, STRFTIME_COLON_SEPARATED, STRFTIME_DASH_SEPARATED)
    converted_end_time = convert_strftime_format(args.end_time, STRFTIME_COLON_SEPARATED, STRFTIME_DASH_SEPARATED)

    # Build graphs according to evaluated data
    graphs_builder = GraphsBuilder(converted_start_time, converted_end_time, args.upload_graphs)
    graphs_builder.plot_long_to_lat(evaluated_run_data)
    graphs_builder.plot_time_to_speed(evaluated_run_data)

    logger.info("Done evaluating data".format(args.start_time, args.end_time))
