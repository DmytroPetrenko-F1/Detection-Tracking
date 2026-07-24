import cv2
import torch
from ultralytics import YOLO

class EdgeTracker:
    def __init__(self, camera_id=0, model_name="yolov8n.pt"):
        # Перевірка CUDA
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"[ІНФО] Використовується пристрій: {self.device.upper()}")

        # Ініціалізація моделі
        self.model = YOLO(model_name)
        self.model.to(self.device)
        
        # Ініціалізація захоплення через V4L2
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
        
        # КРИТИЧНО ДЛЯ WSL2: Встановлюємо формат стиснення MJPEG до вибору роздільної здатності
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        # Встановлюємо оптимальну роздільну здатність
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            raise RuntimeError("[ПОМИЛКА] Не вдалося відкрити камеру. Перевір usbipd.")

        # Перевіримо, які параметри реально застосувалися
        w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"[ІНФО] Камера успішно налаштована на роздільну здатність: {int(w)}x{int(h)}")

    def run(self):
        print("[ІНФО] Запуск відеопотоку... Натисни 'q' у вікні відео для виходу.")
        empty_frames = 0
        
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                empty_frames += 1
                if empty_frames > 10:
                    print("[ПОМИЛКА] Занадто багато порожніх кадрів. Вихід.")
                    break
                print("[ПОПЕРЕДЖЕННЯ] Кадр ще не готовий, чекаємо...")
                cv2.waitKey(100) # Чекаємо 100мс
                continue
                
            empty_frames = 0 # Скидаємо лічильник, якщо кадр успішний
            
            frame_center_x = frame.shape[1] // 2
            frame_center_y = frame.shape[0] // 2

            # Трекінг об'єктів (0 - людина, 15 - кіт)
            results = self.model.track(frame, persist=True, verbose=False, imgsz=640, classes=[0, 15])

            # Малюємо власний інтерфейс прямо на frame
            for box in results[0].boxes.xyxy:
                x1, y1, x2, y2 = map(int, box.cpu().numpy())
                # Обчислюємо центр
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                # Малюємо приціл (коло)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), 2)
                
                error_x = cx - frame_center_x
                error_y = cy - frame_center_y
                
                cv2.line(frame, (frame_center_x, frame_center_y), (cx, cy), (255, 0, 0), 1)
                cv2.putText(frame, f"Error: {error_x}, {error_y}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # За бажанням: можна намалювати ще й лінію до центру або координати
                cv2.putText(frame, f"Target: {cx}, {cy}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Виводимо чистий frame (БЕЗ .plot())
            cv2.imshow("Vyriy Edge Tracker [WSL2]", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.cleanup()

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("[ІНФО] Роботу завершено.")

if __name__ == "__main__":
    tracker = EdgeTracker(camera_id=0)
    tracker.run()