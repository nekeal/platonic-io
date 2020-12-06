from platonic_io.recognition_engine import FrameWorker, Master
from time import sleep

master = Master("/home/bartek/Downloads/platonic_test_cut_cut.mp4", "/home/bartek/Downloads/3_out.avi", 3)
master.start()

while master.is_alive():
    print("LOG: " + master.get_log())
    print("PROGRESS: " + str(master.get_progress()))
    sleep(1)
print("LOG: " + master.get_log())
print("PROGRESS: " + str(master.get_progress()))