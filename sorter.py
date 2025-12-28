import cv2
import numpy as np
import serial, time

# === Serial to Arduino ===
# actualcom = input("Enter COM port (e.g., COM11): ") [This somehow doesn't work reliably]
ser = serial.Serial("COM11", 9600)
steel_count = 0

cap = cv2.VideoCapture(0)

# ---- Parallelogram ROI over belt ----
TOP_LEFT     = (230,   0)
TOP_RIGHT    = (420,   0)
BOTTOM_RIGHT = (480, 480)
BOTTOM_LEFT  = (170, 480)

# ---- HSV ranges (no aluminum class) ----
RED1_LOW  = np.array([0, 120, 80])
RED1_HIGH = np.array([10, 255, 255])
RED2_LOW  = np.array([170, 120, 80])
RED2_HIGH = np.array([180, 255, 255])

YEL_LOW  = np.array([20, 150, 120])
YEL_HIGH = np.array([35, 255, 255])

SAND_LOW  = np.array([10, 40, 80])
SAND_HIGH = np.array([25, 200, 220])

STEEL_LOW  = np.array([90, 30, 80])
STEEL_HIGH = np.array([130, 140, 255])

last_label = None
cooldown_frames = 0


def classify_circle(roi_hsv, roi_mask):
    masks = {}

    m_red1 = cv2.inRange(roi_hsv, RED1_LOW, RED1_HIGH)
    m_red2 = cv2.inRange(roi_hsv, RED2_LOW, RED2_HIGH)
    masks["R"] = cv2.bitwise_or(m_red1, m_red2)

    masks["Y"] = cv2.inRange(roi_hsv, YEL_LOW, YEL_HIGH)
    masks["S"] = cv2.inRange(roi_hsv, SAND_LOW, SAND_HIGH)
    masks["T"] = cv2.inRange(roi_hsv, STEEL_LOW, STEEL_HIGH)

    scores = {
        lbl: cv2.countNonZero(cv2.bitwise_and(m, m, mask=roi_mask))
        for lbl, m in masks.items()
    }

    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]
    second_best = sorted(scores.values(), reverse=True)[1]

    if best_score < 800 or best_score < 1.5 * second_best:
        return None, masks
    return best_label, masks


def main():
    global steel_count, last_label, cooldown_frames

    # ---- build static polygon mask once ----
    ret, frame0 = cap.read()
    if not ret:
        print("Camera not available")
        return

    h0, w0 = frame0.shape[:2]
    poly_mask = np.zeros((h0, w0), dtype=np.uint8)
    pts = np.array(
        [TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT], dtype=np.int32
    )
    cv2.fillPoly(poly_mask, [pts], 255)

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # apply belt polygon mask
        belt_only = cv2.bitwise_and(frame, frame, mask=poly_mask)

        hsv = cv2.cvtColor(belt_only, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(belt_only, cv2.COLOR_BGR2GRAY)

        # ignore dark belt; tweak threshold if needed
        _, obj_mask = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(
            obj_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        label = None
        color_masks = {}

        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            if area > 2000:  # ignore small blobs
                (x, y), radius = cv2.minEnclosingCircle(c)
                if radius > 20:
                    x, y, r = int(x), int(y), int(radius)

                    # optional: only accept objects near vertical middle
                    if h0 * 0.2 < y < h0 * 0.8:
                        # ROI around circle
                        x0, y0, x1, y1 = x - r, y - r, x + r, y + r
                        h, w = frame.shape[:2]
                        x0, y0 = max(x0, 0), max(y0, 0)
                        x1, y1 = min(x1, w), min(y1, h)

                        roi_hsv = hsv[y0:y1, x0:x1].copy()
                        roi_mask = np.zeros(roi_hsv.shape[:2], np.uint8)
                        cv2.circle(
                            roi_mask,
                            (roi_hsv.shape[1] // 2, roi_hsv.shape[0] // 2),
                            min(roi_hsv.shape[0], roi_hsv.shape[1]) // 2 - 2,
                            255,
                            -1,
                        )

                        label, color_masks = classify_circle(roi_hsv, roi_mask)

                        if label:
                            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                            cv2.putText(
                                frame,
                                label,
                                (x - 20, y - 20),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 0),
                                2,
                            )

        # send to Arduino with cooldown; send 'N' when nothing
        if cooldown_frames == 0:
            if label:
                send_label = label

                if label == "T":  # steel-like object
                    steel_count += 1
                    if steel_count == 1:
                        send_label = "T"  # real steel: sort
                    else:
                        send_label = "U"  # unknown/likely aluminum: dump

                if send_label != last_label:
                    ser.write((send_label + "\n").encode("ascii"))
                    last_label = send_label
                    cooldown_frames = 10

            elif label is None and last_label != "N":
                ser.write(b"N\n")
                last_label = "N"
                cooldown_frames = 5

        if cooldown_frames > 0:
            cooldown_frames -= 1

        # draw polygon outline
        cv2.polylines(
            frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2
        )

        # show main frame + masks
        cv2.imshow("Camera + ROI", frame)

        if color_masks:
            cv2.imshow("Mask_Red", color_masks["R"])
            cv2.imshow("Mask_Yellow", color_masks["Y"])
            cv2.imshow("Mask_Sand", color_masks["S"])
            cv2.imshow("Mask_Steel", color_masks["T"])
        else:
            black = np.zeros((100, 100), dtype=np.uint8)
            cv2.imshow("Mask_Red", black)
            cv2.imshow("Mask_Yellow", black)
            cv2.imshow("Mask_Sand", black)
            cv2.imshow("Mask_Steel", black)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    ser.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()