import cv2
import numpy as np
import typing  

class SingleCamDistanceMeasure(object):
	# 1 cm = 0.39 inch, original size h x w 
	INCH = 0.39
	RefSizeDict = { 
					"person" : (160*INCH, 50*INCH), 
					"bicycle" : (98*INCH, 65*INCH),
					"motorbike" : (100*INCH, 100*INCH),
					"car" : (150*INCH, 180*INCH ),
					"bus" : (319*INCH, 250*INCH), 
					"truck" : (346*INCH, 250*INCH), 
				 }

	def __init__(self, object_list=["person", "bicycle", "car", "motorbike", "bus", "truck"] ):
		self.object_list = object_list
		self.f = 240 # focal length
		self.distance_points = []

	def __isInsidePolygon(self, pt, poly ):
		"""
		Judgment point is within the polygon range.

		Args:
			pt: the object points.
			poly: is a polygonal points. [[x1, y1], [x2, y2], [x3, y3] ... [xn, yn]]

		Returns:
			total number of all feature vector.
		"""

		c = False
		i = -1
		l = len(poly)
		j = l - 1
		while i < l - 1:
			i += 1
			if((poly[i][0]<=pt[0] and pt[0] < poly[j][0])or(
				poly[j][0]<=pt[0] and pt[0]<poly[i][0] )):
				if(pt[1]<(poly[j][1]-poly[i][1]) * (pt[0]-poly[i][0])/(
					poly[j][0]-poly[i][0])+poly[i][1]):
					c = not c
			j=i
		return c

	def calcDistance(self, boxes) :
		"""
		Calculate the distance of the target object through the size of pixels.

		Args:
			boxes: coordinate information and labels of the target object.

		Returns:
		"""
		self.distance_points = []
		if ( len(boxes) != 0 )  :
			for box, _ in boxes:
				ymin, xmin, ymax, xmax, label = box
				if label in self.object_list and  ymax <= 650:
					point_x = (xmax + xmin) // 2
					point_y = ymax

					try :
						distance = (self.RefSizeDict[label][0] * self.f)/ (ymax - ymin)
						distance = distance/12*0.3048 # 1ft = 0.3048 m
						self.distance_points.append([point_x, point_y, distance])
					except :
						pass
 
	def calcCollisionPoint(self, poly):
		"""
		Determine whether the target object is within the main lane lines.

		Args:
			poly: is a polygonal points. [[x1, y1], [x2, y2], [x3, y3] ... [xn, yn]]

		Returns:
			[Xcenter, Ybottom, distance]
		"""

		if ( len(self.distance_points) != 0 and len(poly) )  :
			for x, y, d in self.distance_points:
				if (self.__isInsidePolygon( (x, y), np.squeeze(poly) )) :
					return [x, y, d]
		return None

	def DrawDetectedOnFrame(self, frame_show) :
		if ( len(self.distance_points) != 0 )  :
			for x, y, d in self.distance_points:
				cv2.circle(frame_show, (x, y), 4, (0, 255 , 0), thickness=-1)

				t1=0.5
				t2=0.2
				t3=0.3
				V0=11.11
				a=-(V0*V0)/(2*(d-V0*(t1+t2+t3)))

				unitd= 'm'
				unita='m/s'

				
				if d < 0:
					text_distance = ' {} {}'.format( "unknown", unitd)
					text_deceleration = ' {} {}'.format( "unknown", unita)
				else :
					text_distance = ' {:.2f} {}'.format(d, unitd)
					text_deceleration = ' -{:.1f} {}'.format(a, unita)
				
				if (d > 3) :
					fontScale = 0.5
				elif ( 1.5 < d <= 3) :
					fontScale = 0.8
				elif (d <= 1.5) :
					fontScale = 1
				else :
					fontScale = 0.8

				

				# get coords based on boundary
				textsize_distance = cv2.getTextSize(text_distance, 0, fontScale=fontScale, thickness=3)[0]
				textsize_deceleration = cv2.getTextSize(text_deceleration, 0, fontScale=fontScale, thickness=3)[0]
				
				textX_distance = int((x - textsize_distance[0]/2))
				textY_distance = int((y + textsize_distance[1]))

				textX_deceleration = int((x- textsize_distance[0]/2 - 20))
				textY_deceleration = int((y + textsize_deceleration[1] + 25))


				cv2.putText(frame_show, text_distance, (textX_distance + 1, textY_distance + 5), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, fontScale=fontScale,  
							color=(0, 255 , 0), thickness=2)				
				cv2.putText(frame_show, text_deceleration, (textX_deceleration +1 , textY_deceleration +5 ), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, fontScale=fontScale,  
							color=(0, 255 , 0), thickness=2)
