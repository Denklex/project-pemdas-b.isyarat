import cv2
import time
import math
import mediapipe as mp

# DETEKSI TANGAN

class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=mode,
            max_num_hands=maxHands,
            model_complexity=1,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if draw and self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, hand, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPositions(self, img, draw=False):
        """membuat track tangan berisi {id,x,y}"""
        handsLM = []

        if self.results and self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                lmList = []
                h, w, c = img.shape
                for i, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([i, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (0, 255, 0), -1)
                handsLM.append(lmList)
        return handsLM

# FUNGSI GESTUR TANGAN

def dist(a, b):
    return math.dist((a[1], a[2]), (b[1], b[2]))

def finger_state(lm):
    """menentukan buka/tutup jari"""
    result = []
    # jempol
    result.append(1 if lm[4][1] > lm[3][1] else 0)
    # 4 jari
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        result.append(1 if lm[tip][2] < lm[pip][2] else 0)

    return result

def distances_dict(lm):
    d = {}
    for i in range(21):
        for j in range(21):
            if i != j:
                d[(i, j)] = dist(lm[i], lm[j])
    return d

def gesture_one_hand(lm):
    f = finger_state(lm)
    d = distances_dict(lm)

    # Ok
    if d[(4, 8)] < 30:
        return "Ok"

    # I Love You
    if (
        d[(4, 8)] > 60 and
        d[(8, 12)] > 70 and
        d[(20, 16)] > 50 and
        d[(12, 16)] < 40
    ):
        return "I Love You"

    # angka
    if f == [1, 0, 0, 0, 0]: return "Benar"
    if f == [1, 1, 1, 1, 1]: return "Halo/Lima"
    if f == [0, 1, 0, 0, 0]: return "Satu"
    if f == [0, 1, 1, 0, 0]: return "Dua"
    if f == [1, 1, 1, 0, 0]: return "Tiga"
    if f == [0, 1, 1, 1, 1]: return "Empat"
    if f == [0, 1, 1, 1, 0]: return "Enam"
    if f == [0, 1, 1, 0, 1]: return "Tujuh"
    if f == [0, 1, 0, 1, 1]: return "Delapan"
    if f == [0, 0, 1, 1, 1]: return "Sembilan"

    return None

def gesture_two_hands(l1, l2):
    f1, f2 = finger_state(l1), finger_state(l2)

    if f1 == [1, 0, 0, 0, 0] and f2 == [1, 0, 0, 0, 0]:
        return "Bagus"

    return None

# MAIN

def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(maxHands=2, detectionCon=0.75)
    pTime = 0

    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.findHands(img)
        hands = detector.findPositions(img, draw=False)

        # text
        gesture_text = "berikan gestur" if len(hands) == 0 else None

        if len(hands) == 1:
            gesture_text = gesture_one_hand(hands[0])

        if len(hands) == 2:
            gesture_text = gesture_two_hands(hands[0], hands[1])

        if gesture_text:
            cv2.putText(img, gesture_text, (5, 50),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

        # FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f"FPS: {int(fps)}", (460, 30),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)

        cv2.imshow("image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()
