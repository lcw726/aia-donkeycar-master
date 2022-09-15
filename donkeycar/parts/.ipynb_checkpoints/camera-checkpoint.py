import os
import time
import numpy as np
from PIL import Image
import glob
import cv2

class BaseCamera:

    def run_threaded(self):
        return self.frame

class PiCamera(BaseCamera):
    def __init__(self, resolution=(120, 160), framerate=20):
        from picamera.array import PiRGBArray
        from picamera import PiCamera
        resolution = (resolution[1], resolution[0])
        # initialize the camera and stream
        self.camera = PiCamera() #PiCamera gets resolution (height, width)
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="rgb", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.on = True

        print('PiCamera loaded.. .warming camera')
        time.sleep(2)

    def compute_slope(line):
        x1, y1, x2, y2 = line[0]
        return (y2 - y1) / (x2 - x1 + np.finfo(float).eps)

    def compute_slope_tan(line):
        x1, y1, x2, y2 = line[0]
        return np.rad2deg(np.arctan2(y2 - y1, x2 - x1 + np.finfo(float).eps))

    def compute_bias(line):
        x1, y1, x2, y2 = line[0]
        return y1 - compute_slope(line) * x1

    def compute_intercept(line):
        x1, y1, x2, y2 = line[0]
        return (y2 - y1) / (x2 - x1 + np.finfo(float).eps)

    def yintercept(line):
        x1, y1, x2, y2 = line
        '''Get the y intercept of a line segment'''
        # if compute_slope(line) != None:
        x, y = x1,y1
        return y - compute_slope1(line) * x
        # else:
        #     return None

    def compute_slope1(line):
        x1, y1, x2, y2 = line
        return (y2 - y1) / (x2 - x1 + np.finfo(float).eps)

        # def yintercept(line):
        #     x1, y1, x2, y2 = line[0]
        #     '''Get the y intercept of a line segment'''
        #     # if compute_slope(line) != None:
        #     x, y = x1,y1
        #     return y - compute_slope(line) * x
        #     # else:
        #     #     return None


    def compute_lane_from_candidates(line_candidates, img_shape):
            """
            Compute lines that approximate the position of both road lanes.

            :param line_candidates: lines from hough transform
            :param img_shape: shape of image to which hough transform was applied
            :return: lines that approximate left and right lane position
            """

            pos_lines = [l for l in line_candidates if compute_slope(l) > 0]
            neg_lines = [l for l in line_candidates if compute_slope(l) < 0]

            # interpolate biases and slopes to compute equation of line that approximates left lane
            # median is employed to filter outliers
            neg_bias = np.median([compute_bias(l) for l in neg_lines]).astype(int)
            neg_slope = np.median([compute_slope(l) for l in neg_lines])
    #         print("neg_slope", neg_slope)
    #         print("neg_bias", neg_bias)
            x1, y1 = 0, neg_bias
            x2, y2 = -np.int32(np.round(neg_bias / neg_slope)), 0
            left_lane = x1, y1, x2, y2

            # interpolate biases and slopes to compute equation of line that approximates right lane
            # median is employed to filter outliers

            lane_right_bias = np.median([compute_bias(l) for l in pos_lines]).astype(int)
            lane_right_slope = np.median([compute_slope(l) for l in pos_lines])
    #         print("lane_right_bias", lane_right_bias)
    #         print("lane_right_slope", lane_right_slope)
            x1, y1 = 0, lane_right_bias
            x2, y2 = np.int32(np.round((img_shape[0] - lane_right_bias) / lane_right_slope)), img_shape[0]
            right_lane = x1, y1, x2, y2

            #print("lane_right_intercept", yintercept(left_lane))
            #print("lane_right_intercept", yintercept(right_lane))

            return left_lane, right_lane

    def run(self):
        f = next(self.stream)
        frame = f.array
        self.rawCapture.truncate(0)
        
        img_orig = frame
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(image, 40, 70)
        height, width = image.shape

        detected_lines = cv2.HoughLinesP(edges, 2, np.pi / 180, 1, minLineLength=15, maxLineGap=5)

        candidate_lines = []
        for line in detected_lines:
            # consider only lines with slope between 30 and 60 degrees
            if 0.5 <= np.abs(compute_slope(line)) <= 2:
                candidate_lines.append(line)

        for line in candidate_lines:
            x1, y1, x2, y2 = line[0]
            if y1 > 60:
                cv2.line(img_orig, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
        frame = img_orig
        
        return frame

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            if not self.on:
                break

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('stoping PiCamera')
        time.sleep(.5)
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()

class Webcam(BaseCamera):
    def __init__(self, resolution = (160, 120), framerate = 20):
        import pygame
        import pygame.camera

        super().__init__()

        pygame.init()
        pygame.camera.init()
        l = pygame.camera.list_cameras()
        self.cam = pygame.camera.Camera(l[0], resolution, "RGB")
        self.resolution = resolution
        self.cam.start()
        self.framerate = framerate

        # initialize variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.on = True

        print('WebcamVideoStream loaded.. .warming camera')

        time.sleep(2)

    def update(self):
        from datetime import datetime, timedelta
        import pygame.image
        while self.on:
            start = datetime.now()

            if self.cam.query_image():
                # snapshot = self.cam.get_image()
                # self.frame = list(pygame.image.tostring(snapshot, "RGB", False))
                snapshot = self.cam.get_image()
                snapshot1 = pygame.transform.scale(snapshot, self.resolution)
                self.frame = pygame.surfarray.pixels3d(pygame.transform.rotate(pygame.transform.flip(snapshot1, True, False), 90))

            stop = datetime.now()
            s = 1 / self.framerate - (stop - start).total_seconds()
            if s > 0:
                time.sleep(s)

        self.cam.stop()

    def run_threaded(self):
        return self.frame

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('stoping Webcam')
        time.sleep(.5)

class MockCamera(BaseCamera):
    """
    Fake camera. Returns only a single static frame
    """
    def __init__(self, resolution=(160, 120), image=None):
        if image is not None:
            self.frame = image
        else:
            self.frame = Image.new('RGB', resolution)

    def update(self):
        pass

    def shutdown(self):
        pass

class ImageListCamera(BaseCamera):
    """
    Use the images from a tub as a fake camera output
    """
    def __init__(self, path_mask='~/mycar/data/**/*.jpg'):
        self.image_filenames = glob.glob(os.path.expanduser(path_mask), recursive=True)

        def get_image_index(fnm):
            sl = os.path.basename(fnm).split('_')
            return int(sl[0])

        """
        I feel like sorting by modified time is almost always
        what you want. but if you tared and moved your data around,
        sometimes it doesn't preserve a nice modified time.
        so, sorting by image index works better, but only with one path.
        """
        self.image_filenames.sort(key=get_image_index)
        #self.image_filenames.sort(key=os.path.getmtime)
        self.num_images = len(self.image_filenames)
        print('%d images loaded.' % self.num_images)
        print( self.image_filenames[:10])
        self.i_frame = 0
        self.frame = None
        self.update()

    def update(self):
        pass

    def run_threaded(self):
        if self.num_images > 0:
            self.i_frame = (self.i_frame + 1) % self.num_images
            self.frame = Image.open(self.image_filenames[self.i_frame])

        return np.asarray(self.frame)

    def shutdown(self):
        pass
