import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import time
import serial

# Arduino'nun bağlı olduğu seri portu belirtin
ser = serial.Serial('COM9', 9600)

cap = cv2.VideoCapture(0)
counter = 0
uyku = 0
detector = FaceMeshDetector()
plotY = LivePlot(540, 360, [10, 60])
idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
color = (0, 0, 255)
ratioList = []
start = 0
stop = 0
sonuc = 0
durum = True

while True:
    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)
    durum = True
    if faces:
        face = faces[0]

        for id in idList:
            cv2.circle(img, face[id], 5, color, cv2.FILLED)

        leftUp = face[159]
        leftDown = face[23]
        leftLeft = face[130]
        leftRight = face[243]

        lenghtVer, _ = detector.findDistance(leftUp, leftDown)
        lenghtHor, _ = detector.findDistance(leftLeft, leftRight)
        cv2.line(img, leftUp, leftDown, (0, 255, 0), 3)
        cv2.line(img, leftLeft, leftRight, (0, 255, 255), 3)
        ratio = int((lenghtVer / lenghtHor) * 100)
        ratioList.append(ratio)
        ratioavg = sum(ratioList) / len(ratioList)
        if len(ratioList) > 3:
            ratioList.pop(0)
        if ratioavg < 35 and counter == 0:
            if durum == True:
                start = time.time()

            uyku += 1
            color = (255, 0, 0)
            counter = 1
            ser.write(b'1')
        elif ratioavg >= 35 and counter != 0:
            counter = 0
            color = (0, 0, 255)
            ser.write(b'0')

        imgPlot = plotY.update(ratioavg, color)
        img = cv2.resize(img, (640, 360))
        imgPlot = cv2.resize(imgPlot, (640, 360))
        #imgStack = cv2.vconcat([img, imgPlot])

    cv2.putText(img, f'uyku:{uyku}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow("winname", img)
    cv2.waitKey(1)

cv2.destroyAllWindows()
cap.release()
ser.close()
