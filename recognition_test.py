from platonic_io.recognition_engine import FrameWorker, Master

master = Master("/home/bartek/Downloads/platonic_test_cut.mp4", "/home/bartek/Downloads/sink.avi", 6)
master.start()