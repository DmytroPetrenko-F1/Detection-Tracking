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

            # Трекінг об'єктів
            results = self.model.track(frame, persist=True, verbose=False, imgsz=640)

            # Отримання кадру з рамками
            annotated_frame = results[0].plot()

            # Відображення вікна
            cv2.imshow("Vyriy Edge Tracker [WSL2]", annotated_frame)

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