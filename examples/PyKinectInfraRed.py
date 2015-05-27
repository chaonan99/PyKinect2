from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

import ctypes
import _ctypes
import pygame
import sys
import numpy as np


if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread

# colors for drawing different bodies 
SKELETON_COLORS = [pygame.color.THECOLORS["red"], 
                  pygame.color.THECOLORS["blue"], 
                  pygame.color.THECOLORS["green"], 
                  pygame.color.THECOLORS["orange"], 
                  pygame.color.THECOLORS["purple"], 
                  pygame.color.THECOLORS["yellow"], 
                  pygame.color.THECOLORS["violet"]]


class InfraRedRuntime(object):
    def __init__(self):
		pygame.init()

		# Used to manage how fast the screen updates
		self._clock = pygame.time.Clock()

		# Loop until the user clicks the close button.
		self._done = False

		# Used to manage how fast the screen updates
		self._clock = pygame.time.Clock()

		# Kinect runtime object, we want only color and body frames 
		self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Infrared)

		# back buffer surface for getting Kinect infrared frames, 8bit grey, width and height equal to the Kinect color frame size
		self._frame_surface = pygame.Surface((self._kinect.infrared_frame_desc.Width, self._kinect.infrared_frame_desc.Height), 0, 24)
		# here we will store skeleton data 
		self._bodies = None
		
		# Set the width and height of the screen [width, height]
		self._infoObject = pygame.display.Info()
		self._screen = pygame.display.set_mode((self._kinect.infrared_frame_desc.Width, self._kinect.infrared_frame_desc.Height), 
											   pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

		pygame.display.set_caption("Kinect for Windows v2 Infrared")


    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):
        joint0State = joints[joint0].TrackingState;
        joint1State = joints[joint1].TrackingState;

        # both joints are not tracked
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked): 
            return

        # both joints are not *really* tracked
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            return

        # ok, at least one is good 
        start = (jointPoints[joint0].x, jointPoints[joint0].y)
        end = (jointPoints[joint1].x, jointPoints[joint1].y)

        try:
            pygame.draw.line(self._frame_surface, color, start, end, 8)
        except: # need to catch it due to possible invalid positions (with inf)
            pass

    def draw_body(self, joints, jointPoints, color):
        # Torso
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft);
    
        # Right Arm    
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight);

        # Left Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft);

        # Right Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight);

        # Left Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft);


    def draw_infrared_frame(self, frame, target_surface):
		if frame is None:  # some usb hub do not provide the infrared image
						   # it works with Kinect studio though
			return
		target_surface.lock()
		f8=np.uint8(frame.clip(1,4000)/16.)
		frame8bit=np.dstack((f8,f8,f8))
		address = self._kinect.surface_as_array(target_surface.get_buffer())
		ctypes.memmove(address, frame8bit.ctypes.data, frame8bit.size)
		del address
		target_surface.unlock()

    def run(self):
		# -------- Main Program Loop -----------
		while not self._done:
			# --- Main event loop
			for event in pygame.event.get(): # User did something
				if event.type == pygame.QUIT: # If user clicked close
					self._done = True # Flag that we are done so we exit this loop

				elif event.type == pygame.VIDEORESIZE: # window resized
					self._screen = pygame.display.set_mode(event.dict['size'], 
											   pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
					
			# --- Game logic should go here
			# --- Getting frames and drawing  
			if self._kinect.has_new_infrared_frame():
				frame = self._kinect.get_last_infrared_frame()
				self.draw_infrared_frame(frame, self._frame_surface)
				frame = None

			# --- Cool! We have a body frame, so can get skeletons
			if self._kinect.has_new_body_frame(): 
				self._bodies = self._kinect.get_last_body_frame()

			# --- draw skeletons to _frame_surface
			if self._bodies is not None: 
				for i in range(0, self._kinect.max_body_count):
					body = self._bodies.bodies[i]
					if not body.is_tracked: 
						continue 
					
					joints = body.joints 
					# convert joint coordinates to color space 
					joint_points = self._kinect.body_joints_to_color_space(joints)
					self.draw_body(joints, joint_points, SKELETON_COLORS[i])

			# --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
			# --- (screen size may be different from Kinect's color frame size) 
			surface_to_draw = pygame.transform.scale(self._frame_surface, (512,424));
			self._screen.blit(self._frame_surface, (0,0))
			surface_to_draw = None
			pygame.display.update()

			# --- Go ahead and update the screen with what we've drawn.
			pygame.display.flip()

			# --- Limit to 60 frames per second
			self._clock.tick(60)

		# Close our Kinect sensor, close the window and quit.
		self._kinect.close()
		pygame.quit()


__main__ = "Kinect v2 InfraRed"
game =InfraRedRuntime();
game.run();

