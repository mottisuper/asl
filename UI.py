import cv2
import time 

#global variables
blink_speed = 0.5
wait_time_box = 0.10
width_process_box = 5

class UI:
  def __init__ (self):
    # running real time video and loading frames, the screen is resized also in maximum of window's size
    self.current_letter = ""
    self.subtitles = ""
    self.suggestions = {}
    self.is_index_in_box = False
    self.percent_box = 0
    self.current_box = None
    self.boxes = []
    self.last_time_box = time.time()
    self.height_frame = None
    self.width_frame = None
    self.width_main_screen = None
    self.width_current_letter = None
    self.width_subtitles = None
    self.width_box = None
    self.height_main_screen = None
    self.height_current_letter = None
    self.height_subtitles = None
    self.height_box = None
    self.top_left_main_screen = None
    self.top_left_current_letter = None
    self.top_left_subtitles = None
    self.bottom_right_main_screen = None
    self.bottom_right_current_letter = None
    self.bottom_right_subtitles = None
    self.cap = cv2.VideoCapture(0)
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cv2.namedWindow("FRAME", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("FRAME", 640, 480)
    cv2.setWindowProperty("FRAME", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

  @staticmethod
  def show(title, frame):
    cv2.imshow(title, frame)

  def read(self):
    return self.cap.read()
  @staticmethod
  def flip(frame):
    return cv2.flip(frame, 1)

  @staticmethod
  def click():
    key = cv2.waitKey(1) 
    if  key == ord('q'):
      return 'q' 
    return 'nothing'
  
  def destroy(self):
    self.cap.release()
    cv2.destroyAllWindows()

  def set_current_letter(self, letter):
    self.current_letter = letter
  
  def set_subtitles(self, subtitles):
    self.subtitles = subtitles

  @staticmethod
  def convert_to_rgb(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

  def set_index_loc(self,  index_loc):
      if index_loc is not None:
        x_index_finger_tip = index_loc[0]
        y_index_finger_tip = index_loc[1]
        self.boxes = []
        for i in range(0,len(self.suggestions)):
          top_left = (0 if i%2 == 0 else self.width_frame-self.width_box, 
                    0 if i<=1 else self.height_frame-self.height_subtitles-self.height_box)
          bottom_right = (top_left[0]+self.width_box, top_left[1]+self.height_box)
          self.boxes.append({"width": self.width_box,
                      "height": self.height_box, 
                      "top_left": top_left,
                      "bottom_right": bottom_right})
          if (self.boxes[i]["top_left"][0] <= x_index_finger_tip <= self.boxes[i]["bottom_right"][0] and
                  self.boxes[i]["top_left"][1] <= y_index_finger_tip <= self.boxes[i]["bottom_right"][1]):
            self.is_index_in_box = True
            self.current_box = i
            return True
        self.is_index_in_box = False
        self.current_box = None
        return False
  
  def set_suggestions(self, suggestions):
    self.suggestions = suggestions

  def set_width_height(self, frame):
    self.width_frame = frame.shape[1]
    self.height_frame = frame.shape[0]
    # variables of components' sizes and locations in screen
    self.width_main_screen = (frame.shape[1]//10)*4
    self.width_current_letter = (frame.shape[1]//10)*4
    self.width_subtitles = frame.shape[1]
    self.width_box = (frame.shape[1]//10)*3
    self.height_main_screen = (frame.shape[0]//10)*8
    self.height_current_letter = (frame.shape[0]//10)
    self.height_subtitles = (frame.shape[0]//10)
    self.height_box = (frame.shape[0]//10)*3
    self.top_left_main_screen = (self.width_box, 0)
    self.top_left_current_letter  = (self.width_box,self.height_main_screen)
    self.top_left_subtitles = (0,self.height_main_screen+self.height_current_letter)    
    self.bottom_right_main_screen = (self.width_box+self.width_main_screen, self.height_main_screen)
    self.bottom_right_current_letter = (self.width_box+self.width_current_letter,self.height_main_screen+self.height_current_letter)
    self.bottom_right_subtitles = (self.width_subtitles, self.height_main_screen+self.height_current_letter+self.height_subtitles)

  def refresh(self, frame):
    global wait_time_box, width_process_box
    is_process_box = False
    selected_word = ""
    self.set_width_height(frame)
    self.boxes = []

    for i in range(4):
      top_left = (0 if i%2 == 0 else frame.shape[1]-self.width_box, 
                  0 if i<=1 else frame.shape[0]-self.height_subtitles-self.height_box)
      bottom_right = (top_left[0]+self.width_box, top_left[1]+self.height_box)
      self.boxes.append({"width": self.width_box,
                    "height": self.height_box, 
                    "top_left": top_left,
                    "bottom_right": bottom_right})
    
    # showing current letter - background and letter  
    overlay_current_letter_box = frame.copy()
    top_left_overlay_current_letter_box = self.top_left_current_letter
    bottom_right_overlay_current_letter_box = self.bottom_right_current_letter
    color_overlay_current_letter_box = (0,0,0)
    alpha_overlay_current_letter_box = 0.5
    cv2.rectangle(overlay_current_letter_box, top_left_overlay_current_letter_box, bottom_right_overlay_current_letter_box, color_overlay_current_letter_box, -1)
    frame = cv2.addWeighted(overlay_current_letter_box, alpha_overlay_current_letter_box, frame, 1-alpha_overlay_current_letter_box,0, 0)
    font_current_letter = cv2.FONT_HERSHEY_PLAIN
    font_scale_current_letter = 2.0
    font_color_current_letter = (0,255,255)
    font_thickness_current_letter = 2
    font_line_current_letter = cv2.LINE_AA
    (text_width_current_letter, text_height_current_letter), _ = cv2.getTextSize(self.current_letter, font_current_letter, font_scale_current_letter, font_thickness_current_letter)
    text_x_current_letter = self.top_left_current_letter[0] + self.width_current_letter // 2 - text_width_current_letter // 2
    text_y_current_letter = self.top_left_current_letter[1] + self.height_current_letter // 2 + text_height_current_letter // 2  
    cv2.putText(frame, self.current_letter, (text_x_current_letter, text_y_current_letter), font_current_letter, font_scale_current_letter, font_color_current_letter, font_thickness_current_letter, font_line_current_letter)

    # showing subtitles
    if self.subtitles:
      cv2.rectangle(frame, self.top_left_subtitles, self.bottom_right_subtitles, (0,0,0), thickness=-1)
      margin_text_subtitles = 10
      text_width_subtitles = cv2.getTextSize(self.subtitles, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)[0][0]
      text_height_subtitles = cv2.getTextSize(self.subtitles, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)[0][1]
      y_centered = self.top_left_subtitles[1] + (self.height_subtitles + text_height_subtitles) // 2
      cv2.putText(frame, self.subtitles, (self.top_left_subtitles[0]+margin_text_subtitles, y_centered), 
              cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA) 
      
      #blink
      if (time.time() % (2*blink_speed)) <  blink_speed:    
        cv2.rectangle(frame, (self.top_left_subtitles[0]+text_width_subtitles+12,self.top_left_subtitles[1]+4),(self.top_left_subtitles[0]+text_width_subtitles+14, self.bottom_right_subtitles[1] -8), (255,255,255), thickness=-1)
    
    #showing boxes
    current_time_box = time.time()
    
    if len(self.suggestions)>0:
      for i in range(0,len(self.suggestions)):
        # showing semi-transparent blue background for box
        overlay = frame.copy()
        top_left_overlay = self.boxes[i]["top_left"]
        bottom_right_overlay = self.boxes[i]["bottom_right"]
        color_overlay = (255,0,0)
        alpha_overlay = 0.5
        font_scale = 1.2
        cv2.rectangle(overlay, top_left_overlay, bottom_right_overlay, color_overlay, -1)
        frame = cv2.addWeighted(overlay, alpha_overlay, frame, 1-alpha_overlay,0, 0)
        
        #showing blue background as progress bar for selected box
        if self.current_box == i:
          is_process_box = True
    
          if self.percent_box < 100:
            if current_time_box - self.last_time_box >= wait_time_box:
              self.percent_box += width_process_box
              self.last_time_box = current_time_box
          else:
            selected_word = self.suggestions[i]
            self.suggestions = {}
            self.percent_box = 0
            self.current_box = None
            is_process_box =  False
            break
    
          progress_width_box = int(self.width_box * self.percent_box / 100)
          progress_bottom_right = (self.boxes[i]["top_left"][0] + progress_width_box, self.boxes[i]["bottom_right"][1])
          cv2.rectangle(frame, self.boxes[i]["top_left"], progress_bottom_right, (255,0,0), thickness=-1)
        
        # putting text into the box, it rescales the width of text
        (text_width, text_height), _ = cv2.getTextSize(self.suggestions[i].upper(), cv2.FONT_HERSHEY_PLAIN, font_scale, 2)
     
        while text_width < self.boxes[i]["width"] * 0.5 and font_scale < 2.5:  
          font_scale += 0.05
          (text_width, text_height), _ = cv2.getTextSize(self.suggestions[i].upper(), cv2.FONT_HERSHEY_PLAIN, font_scale, 2)
        text_x = self.boxes[i]["top_left"][0] + (self.boxes[i]["width"] - text_width) // 2
        text_y = self.boxes[i]["top_left"][1] + (self.boxes[i]["height"] + text_height) // 2
        cv2.putText(frame, self.suggestions[i].upper(), (text_x, text_y), cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), 2, cv2.LINE_AA)

    return frame, is_process_box, selected_word