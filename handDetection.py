import mediapipe as mp
import joblib
import numpy as np
from tensorflow.keras.models import load_model

class HandDetection:
    def __init__(self):
        #loading the model and label encoder
        self.model = load_model('handshape_feature_model_gold')
        label_encoder = joblib.load("label_encoder_gold.pkl")
        self.labels = label_encoder.classes_
        # loading and defining mediapipe
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands(False, max_num_hands=1, min_detection_confidence=0.4) #, min_tracking_confidence=0.5  
        self.list_letters_detection = {}

    def getHandResult(self, image):
        return self.hands.process(image)

    def get_index_loc(self, image):
        self.result_hands_frame =self.hands.process(image)

        if self.result_hands_frame.multi_hand_landmarks:
            hand_landmarks = self.result_hands_frame.multi_hand_landmarks[0]
            index_finger_tip = hand_landmarks.landmark[8]
            h, w, _ = image.shape
            x_pixel = int(index_finger_tip.x * w)
            y_pixel = int(index_finger_tip.y * h)
            return (x_pixel, y_pixel)
        return None

    def predict(self, image):
        label = ""

        self.result_hands_frame =self.hands.process(image)

        if self.result_hands_frame.multi_hand_landmarks:

            for hand_landmarks in self.result_hands_frame.multi_hand_landmarks:
                try:
                        feature_vector = np.array(extract_features(hand_landmarks)).reshape(1, -1)
                        prediction = self.model.predict(feature_vector, verbose=0)
                        class_id = np.argmax(prediction)
                        label = self.labels[class_id]
                except Exception as e:
                        print("Can't predict...", e)

        if label:
            self.list_letters_detection[label] = self.list_letters_detection.get(label, 0) + 1

        return label

    def getMostFrequency(self, frequencies_letter = 0.7):

        if(self.list_letters_detection):
            max_key = max(self.list_letters_detection, key=self.list_letters_detection.get)   
            is_frequency = self.list_letters_detection[max_key]/sum(self.list_letters_detection.values()) > frequencies_letter
            self.list_letters_detection = {}
            return (max_key, is_frequency)
        return("", 0)

# extract features of hand landmarks
def extract_features(landmarks):
    lm = [(pt.x, pt.y, pt.z) for pt in landmarks.landmark]

    def calc_distance(p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def calc_angle(a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        return np.arccos(np.clip(cosine_angle, -1.0, 1.0))

    def vector_angle_y(p1, p2):
        vec = np.array(p2) - np.array(p1)
        unit_y = np.array([0, -1])
        vec2d = vec[:2]
        cos_theta = np.dot(vec2d, unit_y) / (np.linalg.norm(vec2d) + 1e-6)
        return np.arccos(np.clip(cos_theta, -1.0, 1.0))

    # float values
    distances = [
        calc_distance(lm[4], lm[8]),
        calc_distance(lm[4], lm[12]),
        calc_distance(lm[4], lm[16]),
        calc_distance(lm[4], lm[20]),
        calc_distance(lm[12], lm[16]),
        calc_distance(lm[16], lm[20]),
        calc_distance(lm[0], lm[4]),
        calc_distance(lm[0], lm[20]),
        calc_distance(lm[8], lm[16]),
        calc_distance(lm[8], lm[20]),
        calc_distance(lm[8], lm[12]),
        calc_distance(lm[4], lm[0]),
        calc_distance(lm[4], lm[9]),
        calc_distance(lm[4], lm[10]),
        np.log1p(calc_distance(lm[8], lm[12])),
        np.log1p(calc_distance(lm[4], lm[10])),
        np.log1p(calc_distance(lm[8], lm[14]))
    ]

    # float values
    angles = [
        calc_angle(lm[6], lm[7], lm[8]),
        calc_angle(lm[10], lm[11], lm[12]),
        calc_angle(lm[14], lm[15], lm[16]),
        calc_angle(lm[18], lm[19], lm[20]),
        calc_angle(lm[2], lm[3], lm[4]),
        calc_angle(lm[8], lm[9], lm[12]),
        calc_angle(lm[5], lm[6], lm[7]),
        calc_angle(lm[17], lm[18], lm[19]),
        calc_angle(lm[5], lm[6], lm[8]),
        calc_angle(lm[2], lm[3], lm[4])
    ]

    # relative positions
    relative_positions = [
        lm[4][1] - lm[16][1],
        lm[8][1] - lm[12][1],
        lm[20][0] - lm[4][0],
        lm[20][1] - lm[4][1],
    ]

    # directions - float values
    dirctions = [
        np.degrees( calc_angle(lm[5], lm[6], lm[8])),
        np.degrees((vector_angle_y(lm[6], lm[8]) + vector_angle_y(lm[10], lm[12])) / 2)
    ]

    # binary value
    thumb_between_index_middle = (lm[4] < lm[6] and lm[4] > lm[10]) or (lm[4] > lm[6] and lm[4] < lm[10])    
    index_middle_dx = lm[12][0] - lm[8][0]
    crossing_sign = np.sign(index_middle_dx)
    crossing_distance = abs(index_middle_dx)
    bent_fingers = sum([1 for ang in angles[:-1] if np.degrees(ang) < 160])

    return (
        distances +
        angles +
        relative_positions+
        dirctions+
        [thumb_between_index_middle]+
        [index_middle_dx]+
        [crossing_sign]+
        [crossing_distance]+
        [bent_fingers]
    )