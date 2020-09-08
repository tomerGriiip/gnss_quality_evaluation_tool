import csv
from math import sin, cos, sqrt, atan2, radians
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np


KMH_2_MS = 3600/1000


console = "RedBox"
# console = "Arduino"

# file_str = "raw_gps_car 20_8_20 4 - bad.log"
# file_str = "raw_gps_car 25_8_2020 2.log"
file_str = r"C:\Users\User\Desktop\Projects\GNSS Quality Evaluation Tool\raw_gps_car.log"
# file_str = "teraterm3.log"



output_file = "hamoshava car.log"
# file_str ="HaMoshava scooter.csv"
# headers_lst = ["time_log","time_utc","time_GPS","speed","lat","lon","vert","sat","pos_error","course","hdop"]

BEGIN_TIME = datetime.strptime('2020-08-20 09:30:00','%Y-%m-%d %H:%M:%S')
END_TIME =  datetime.strptime('2020-08-20 09:40:00','%Y-%m-%d %H:%M:%S')


# --------------------   hamoshava data   ---------------------------------#


x_cor_min = 34.8640
x_cor_max = 34.8654
y_cor_min = 32.1053
y_cor_max = 32.1061

# x_cor_min = 34.8640
# x_cor_max = 34.8654
# y_cor_min = 32.102
# y_cor_max = 32.103



# --------------------   office data   ---------------------------------#
# 32.10527,34.897938
#
#
# x_cor_min = 34.8978
# x_cor_max = 34.8980
# y_cor_min = 32.1051
# y_cor_max = 32.1054



if console == "RedBox":
    headers_dic = {
        "time_log": 0,
        "time_utc": 1,
        "time_GPS": 2,
        "speed": 3,
        "lat": 4,
        "lon": 5,
        "vert": 6,
        "sat": 7,
        "pos_error": 8,
        "course": 9,
        "hdop": 10
    }


if console == "Arduino":
    headers_dic = {
        "time_utc": 0,
        "speed": 1,
        "lat": 2,
        "lon": 3
    }









class csv_data():
    def __init__(self, file_str):

        self.err_marg = 0.5
        self.err_min_speed = 10


        self.lat = 0
        self.lon = 0
        self.gps_dx = 0
        self.gps_speed = 0
        self.t_sum = 0
        self.first_row = True

        self.lat_lst= [0]
        self.lon_lst = [0]
        self.gps_speed_lst = [0]
        self.t_lst = [0]
        self.dx_lst = [0]
        self.dxdt_lst = [0]
        self.t_session_lst = [0]
        self.time_sample_lst = [0]
        self.lat_err = [0]
        self.lon_err = [0]
        self.t_err = [0]
        self.dxdt_err = [0]
        self.t_session_err =[0]


        with open(file_str, 'rt')as f:
            self.data = csv.reader(f)
            ii=0
            for row in self.data:
                # print("data: {}".format(row))
                self.last_lat = self.lat
                self.last_lon= self.lon
                try:
                    self.temp_time = row[headers_dic["time_GPS"]]
                    self.temp_date_time = row[headers_dic["time_utc"]]
                    self.time_utc = datetime.strptime(row[headers_dic["time_utc"]],'%Y-%m-%d %H:%M:%S.%f')
                    self.lat = float(row[headers_dic["lat"]])
                    self.lon =float(row[headers_dic["lon"]])
                    self.gps_speed = float(row[headers_dic["speed"]])
                    self.data_check = True
                    if self.lat == 0.0:
                        print (" no fix data")
                        self.data_check = False
                    # print (self.time_utc)
                except:
                    print ("Error in data")
                    self.data_check = False
                    pass

                if self.data_check == True:
                    if console == "RedBox":
                        self.merged_time = self.merge_TS(self.temp_time,self.temp_date_time)
                        self.time_sample = self.merged_time

                    if console == "Arduino":
                        self.time_sample = self.time_utc

                # print("data: {}, {}, {}".format(self.temp_date_time, self.temp_time,self.merged_time))
                # print(self.time_utc)


                    if (self.time_sample > BEGIN_TIME) and ((self.time_sample < END_TIME)):
                        if self.data_check == True:
                            if self.first_row == True:
                                self.first_row = False
                                self.t_session_start = self.time_sample

                        duration = self.time_sample - self.t_session_start

                        self.t_session = duration.total_seconds()
                        self.t_session_lst.append(self.t_session)
                        self.gps_dx = self.cor_distance(self.last_lat,self.last_lon,self.lat,self.lon)
                        self.gps_dt = self.t_session_lst[-1] -self.t_session_lst[-2]
                        self.t_sum = self.t_sum + self.gps_dt
                        try:
                            self.dxdt= self.gps_dx/self.gps_dt*KMH_2_MS
                        except:
                            self.dxdt = 99999
                        self.lat_lst.append(self.lat)
                        self.lon_lst.append(self.lon)
                        self.t_lst.append(self.time_sample)
                        self.dx_lst.append(self.gps_dx)
                        self.dxdt_lst.append(self.dxdt)
                        self.gps_speed_lst.append(self.gps_speed)
                        self.time_sample_lst.append(self.time_sample)
                        self.check_speed_err()

                        # print("{},{},{},{}".format(self.time_utc,self.gps_speed,self.lat,self.lon))





                # self.t_gps =row[headers_dic["time_GPS"]]


                # print ("{},{},{},{},{}".format(ii,self.t_gps,self.lat,self.lon,self.gps_dx))

                ii=ii+1
                if ii == 100000000:
                    self.lat_lst = self.lat_lst[1:]
                    self.lon_lst = self.lon_lst[1:]
                    break


    def proccess_data(self):
        print("proccess")

    def cor_distance (self,lat1,lon1,lat2,lon2):
        R = 6373.0
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return  R * c * 1000

    def check_speed_err (self):
        if self.gps_speed > self.err_min_speed:
            speed_error = sqrt((self.gps_speed-self.dxdt)**2)/self.gps_speed
            if speed_error > self.err_marg :

                self.lat_err.append(self.lat)
                self.lon_err.append(self.lon)
                self.t_err.append(self.t_sum)
                self.dxdt_err.append(self.dxdt)
                self.t_session_err.append(self.t_session)


        return

    def csv_export(self):
        with open(output_file, mode='w') as out_file:
            out_file = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator='\n')
            print("exporting csv")
            out_file.writerow(['UTC time','session time', 'lat', 'lon', 'dx', 'dx/dt', 'GPS speed'])
            for ii in range (0,len(self.gps_speed_lst)-1):
                if ii > 2:
                    out_file.writerow([self.time_sample_lst[ii],self.t_session_lst[ii],self.lon_lst[ii],self.lat_lst[ii],self.dx_lst[ii],self.dxdt_lst[ii],self.gps_speed_lst[ii]])


    def merge_TS(self,val_time,val_date_time):
        new_time = "{} {}".format(val_date_time[:10],val_time)
        # print ("{},{},{}".format(val_time,val_date_time,new_time))
        try:
            time_out = datetime.strptime(new_time,'%Y-%m-%d %H:%M:%S.%f')
        except:
            new_time = "{}{}".format(new_time,".000000")
            time_out = datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S.%f')

        return time_out

    def plot_data(self):
        print(self.t_session_lst)






        fig = plt.figure()

        ax = fig.add_axes([0, 0, 1, 1])

        # ax.scatter(self.t_lst, self.dxdt_lst, color='r')
        # ax.scatter(self.t_lst, self.gps_speed_lst, color='b')
        t = np.arange(len(self.lon_lst))
        t = t/max(t)
        print(len(self.lon_lst))
        print(len(self.t_session_lst))
        # ax.scatter(self.lon_lst, self.lat_lst, s=1, c=t, cmap='Blues')
        ax.scatter(self.lon_lst, self.lat_lst, s=1, color='b')
        ax.scatter(self.lon_err, self.lat_err, s=10, color='r')


        # ax.scatter([0,10,100],[0,10,100], color='r')
        ax.set_xlabel('time')
        ax.set_ylabel('speed')
        print("now")

        plt.xlim(x_cor_min, x_cor_max)
        plt.ylim(y_cor_min, y_cor_max)

        ax.xaxis.grid(True)
        ax.yaxis.grid(True)


        plt.show()

        fig2 = plt.figure()
        ax2 = fig2.add_axes([0, 0, 1, 1])
        ax2.scatter(self.t_session_lst, self.dxdt_lst, s=1, color='g')
        ax2.scatter(self.t_session_lst, self.gps_speed_lst, s=1, color='b')
        ax2.scatter(self.t_session_err, self.dxdt_err, s=1, color='r')



        plt.xlim(0, max(self.t_session_lst)*1.2)
        plt.ylim(0, 200)

        ax2.xaxis.grid(True)
        ax2.yaxis.grid(True)

        plt.show()







if __name__ == "__main__":

    # with open(file_str,'rt')as f:
    #   data = csv.reader(f)
    #   ii=0;
    #   for row in data:
    #         try:
    #             print(row[5])
    #             print("line{}, data: {}".format(ii,row))
    #             ii=ii+1
    #         except:
    #             pass


    test_data = csv_data(file_str)
    test_data.proccess_data()
    test_data.plot_data()
    test_data.csv_export()

