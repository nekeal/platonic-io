from platonic_io.recognition_engine import FrameWorker, Master

master = Master("/home/bartek/Downloads/3.mp4", "/home/bartek/Downloads/3_out.avi", 3)
master.start()