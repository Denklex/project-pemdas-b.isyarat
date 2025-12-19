import cv2 #import open cv
import math #hitung jarak antar titik
import mediapipe as mp #import mediapipe


# DETEKSI TANGAN
class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mpHands = mp.solutions.hands #mengambil modul mp
        self.hands = self.mpHands.Hands(
            static_image_mode=mode,
            max_num_hands=maxHands,
            model_complexity=1,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon
        )#deteksi tgn
        self.mpDraw = mp.solutions.drawing_utils #gambar track
        self.results = None #penyimpanan deteksi sementara

    def findHands(self, img, draw=True): #deteksi tgn
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  #warna utk mp
        self.results = self.hands.process(imgRGB)  #hasil dikirim ke mp untuk analisis

        if draw and self.results.multi_hand_landmarks: #gambar tgn
            for hand in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, hand, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPositions(self, img, draw=False):
        #membuat track tangan berisi {id,x,y}
        handsLM = [] #utk simpan data

        if self.results and self.results.multi_hand_landmarks: #when tgn detect
            for handLms in self.results.multi_hand_landmarks: #ambil tiap tgn
                lmList = [] #utk simpan data
                h, w, c = img.shape #tinggi lebar gbr
                for i, lm in enumerate(handLms.landmark): #utk tiap titik jri
                    cx, cy = int(lm.x * w), int(lm.y * h) #posisi presentase ke pxl
                    lmList.append([i, cx, cy]) #simpn idttk,x,y
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (0, 255, 0), -1)
                handsLM.append(lmList) #simpan data tgn

        return handsLM


# FUNGSI GESTUR TANGAN

def dist(a, b): #menghitung jarak 2 titik (rene descrates)
    return math.dist((a[1], a[2]), (b[1], b[2])) #menghitung a-b (d = √[(x₂ - x₁)² + (y₂ - y₁)²])


def finger_state(lm):
    #buka/tutup jari
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
    f = finger_state(lm) #status jari 0/1
    d = distances_dict(lm) #jarak
#20 gesture
    # Ok
    if (
        d[(4, 8)] < 30 and
        d[(0, 12)] > 70 and
        d[(8, 5)] > 30 and
        d[(4, 12)] > 60 and
        d[(8, 20)] > 60 and
        d[(20, 0)] > 70
    ):
        return "Ok/F"

    #C
    if (
        d[(8, 12)] < 30 and
        d[(16, 12)] < 30 and
        d[(20, 16)] < 30 and
        d[(4, 8)] > 40 and
        d[(0, 20)] > 90 and
        d[(4, 20)] > 60
    ):
        return "C"
    #D
    if (
        d[(16, 20)] < 30 and
        d[(16, 12)] < 30 and
        d[(4, 12)] < 30 and
        d[(4, 20)] > 60
    ):
        return "D"
    #E
    if (
        d[(16, 20)] < 30 and
        d[(16, 12)] < 30 and
        d[(8, 12)] < 30 and
        d[(8, 5)] < 30 and
        d[(9, 12)] < 30 and
        d[(16, 13)] < 30 and
        d[(4, 12)] > 50 and
        d[(4, 8)] < 40
    ):
        return "E"
    if f == [0, 0, 0, 0, 1]: return "I/J"
    #G
    if (
        d[(8, 4)] < 40 and
        d[(8, 12)] > 40 and
        d[(8, 16)] > 40 and
        d[(8, 20)] > 40 and
        d[(16, 20)] < 30 and
        d[(16, 12)] < 30 and
        d[(12, 0)] < 40
    ):
        return "G/Q"
    #H
    if (
        d[(8, 4)] < 40 and
        d[(8, 12)] < 30 and
        d[(16, 20)] < 30 and
        d[(16, 4)] < 30 and
        d[(12, 0)] > 50
    ):
        return "H"
    if f == [1, 1, 0, 0, 0]: return "L"
    #0
    if (
        d[(8, 12)] < 30 and
        d[(16, 12)] < 30 and
        d[(20, 16)] < 30 and
        d[(4, 8)] < 30

    ):
        return "0"
    if f == [1, 0, 0, 0, 1]: return "Y"
    if f == [1, 1, 0, 0, 1]: return "i love you"

    if f == [1, 0, 0, 0, 0]: return "Benar"
    if f == [1, 1, 1, 1, 1]: return "Halo/Lima"
    if f == [0, 1, 0, 0, 0]: return "Satu/X/Z"
    if f == [0, 1, 1, 0, 0]: return "Dua/P/U/V/R"
    if f == [1, 1, 1, 0, 0]: return "Tiga/K"
    if f == [0, 1, 1, 1, 1]: return "Empat/B"
    if f == [0, 1, 1, 1, 0]: return "Enam/W"
    if f == [0, 1, 1, 0, 1]: return "Tujuh"
    if f == [0, 1, 0, 1, 1]: return "Delapan"
    if f == [0, 0, 1, 1, 1]: return "Sembilan"
    # abjad
    if f == [0, 0, 0, 0, 0]: return "A/M/N/S/T"
    return None


def gesture_two_hands(l1, l2):
    f1, f2 = finger_state(l1), finger_state(l2)

    if f1 == [1, 0, 0, 0, 0] and f2 == [1, 0, 0, 0, 0]:
        return "Bagus"

    return None


# MAIN

def main():
    cap = cv2.VideoCapture(0) #buka kamera
    detector = HandDetector(maxHands=2, detectionCon=0.75) #deteksi tgn

    while True:
        success, img = cap.read() #1 img form cam
        if not success:
            break

        img = detector.findHands(img) #detect
        hands = detector.findPositions(img, draw=False) #ambil data

        # text
        gesture_text = "berikan gestur" if len(hands) == 0 else None #whn hnd dtect

        if len(hands) == 1:
            gesture_text = gesture_one_hand(hands[0])

        if len(hands) == 2:
            gesture_text = gesture_two_hands(hands[0], hands[1])

        if gesture_text: # tampilan teks detect
            cv2.putText(img, gesture_text, (5, 50),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)


        #Teks Q for exit
        cv2.putText(img, "Klik tombol Q untuk keluar",
                    (5, img.shape[0] - 10),
                    cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 0, 255), 2)

        cv2.imshow("image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): #tekan q for exit
            break

    cap.release() #tutup camera & layar
    cv2.destroyAllWindows()


if __name__ == "__main__": #gui connect
    main()
