from dictionary import Dictionary
from UI import UI
from handDetection import HandDetection
import time

# global variables
count_del = 0
min_count_del = 5
suggestions = {}

# global variables for subtitles
subtitles = ""
length_chars_subtitles = 35
frequencies_letter = 0.8 # between 0.01 to 0.99 
current_word = ""
min_len_current_word = 3

# global variables for detection 
time_duration_detect = 1.5
start_time_detection = time.time()

# global variables for ui
is_process_box = False
selected_word = ""

# creating objects
words_dictionary = Dictionary()
ui = UI()
hand_detection = HandDetection()

def update_subtitles():
  global subtitles, count_del, start_time_detection, current_word, min_len_current_word,suggestions
  (max_key,is_frequency) = hand_detection.getMostFrequency(frequencies_letter)
  if len(subtitles) > length_chars_subtitles:
    subtitles = subtitles[1:]
  if is_frequency:
    if max_key == 'SPACE':
      max_key = ' '
      count_del = 0
    elif max_key == 'DEL':
      max_key=""
      count_del += 1
      if len(subtitles)>0:
        subtitles =  subtitles[:-1]                
        if count_del > min_count_del:
          subtitles = ""
          count_del = 0
    else:
      count_del = 0             
    subtitles += max_key
    current_word = subtitles.split()[-1] if subtitles.strip() else ''
  start_time_detection = current_time

def add_word_to_subtitles (word):
  global subtitles
  if(word):
    index_first_letter_last_word = subtitles.rstrip().rfind(" ") +1
    subtitles = subtitles [:index_first_letter_last_word]
    subtitles += word.upper()
    subtitles += " "

while True:
  ret, frame = ui.read()
  
  if not ret:
    break
  
  current_time = time.time()
  frame = ui.flip(frame)
  
  if not is_process_box:
    ui.set_current_letter(hand_detection.predict(frame))
  
  if current_time - start_time_detection >= time_duration_detect:
    update_subtitles()

  if len(current_word) >= min_len_current_word and subtitles[-1] != " ":
    suggestions = words_dictionary.suggest_words(current_word)
  else:
    suggestions = {}

  ui.set_width_height(frame)
  ui.set_suggestions(suggestions)
  ui.set_index_loc(hand_detection.get_index_loc(frame))
  ui.set_subtitles(subtitles)
  frame, is_process_box, selected_word = ui.refresh(frame)

  if(selected_word):
    add_word_to_subtitles (selected_word)
    selected_word = ""
    suggestions = {}
    current_word = ""

  ui.show("FRAME", frame)
  if ui.click() == 'q':
    break

ui.destroy()