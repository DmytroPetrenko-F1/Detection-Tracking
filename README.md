# WSL2: Ubuntu-22.04 

---

## Трансляція з камери та детекція обєктів YOLOv8

## Швидкий старт

### 1. Встановіть WSL2 та Ubuntu-22.04. [Документація.](https://ubuntu.com/wsl/docs/stable/tutorials/develop-with-ubuntu-wsl/#install-the-remote-development-extension) 

1. Встановлення WSL.
```bash
wsl --install
```
2. Встановлення Ubuntu.
```bash
wsl --install Ubuntu-24.04
```
Після встановлення дистрибутива Ubuntu вам буде запропоновано створити ім'я користувача та пароль. Сеанс Ubuntu розпочнеться автоматично.

### 2. Віддалений доступ через VS Code.
#### Ваш VS Code встановлений на Windows, але він вміє працювати як "клієнт", запускаючи весь код та термінали безпосередньо у Вашому новому середовищі Ubuntu.
1. Відкрийте VS Code у Windows.
2. Перейдіть до меню «Розширення» та встановіть Remote Development.
3. Відкрийте термінал Ubuntu (який налаштували раніше) і створіть папку для вашого проєкту:
```bash
#створення папки
mkdir ~/project
#перехід у папку
cd ~/project
```
4. Знаходячись у цій папці в терміналі Ubuntu, введіть команду:
```bash
code .
```
5. Ця команда відкриє вікно VS Code у Windows, але в лівому нижньому куті ви побачите синю плашку "WSL: Ubuntu". Тепер усі термінали, які ви відкриваєте у VS Code (Ctrl+~), будуть терміналами Linux, і файли зберігатимуться у файловій системі Ubuntu.


### 3. Доступ до камери через WSL2.
#### За замовчуванням WSL2 ізольований від USB-пристроїв Windows з міркувань безпеки. Щоб OpenCV зміг побачити веб-камеру як пристрій /dev/video0, потрібно встановити утиліту usbipd-win. На стороні Windows:
#### PowerShell
1. Відкрий PowerShell від імені адміністратора.
2. Встанови утиліту командою:
```bash
winget install --interactive --exact dorssel.usbipd-win
```
3. Після завершення встановлення перезапустіть PowerShell (знову від адміністратора).
4. Введіть команду, щоб побачити список усіх USB-пристроїв:
```bash
usbipd list
```
5. Знайдіть у списку свою камеру. Біля неї буде вказано BUSID (наприклад, 2-1 або 1-2).
6. Надайте спільний доступ для цього порту (робиться один раз) командою, замінивши BUSID на свій:
```bash
usbipd bind --busid 1-2
```
7. Прикріпіть камеру до WSL2 (цю команду потрібно буде вводити щоразу після перезавантаження комп'ютера, коли потрібно використовувати камеру):
```bash
usbipd attach --wsl --busid 1-2
```


### 4. На стороні Ubuntu (у терміналі VS Code):
1. Щоб Linux міг працювати з відеопристроями, встановимо додаткові драйвери. Виконайте у терміналі:
```bash
sudo apt update
sudo apt install linux-tools-virtual hwdata v4l-utils
```
2. Перевірте, чи з'явилася камера в системі:
```bash
ls -l /dev/video*
```
Якщо ви бачите файли /dev/video0 та /dev/video1 — камера успішно підключена.


# Початорк роботи
### 1. Встановлення системних бібліотек.
Оскільки це чиста Ubuntu, вам потрібно встановити системні бібліотеки GStreamer (для роботи з відеопотоком) та пакетний менеджер uv для швидкої роботи з Python.
Відкрий термінал у VS Code (той, що підключений до WSL) і виконай по черзі:
```bash
# Встановлення GStreamer та утиліт
sudo apt update
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools

# Встановлення uv (якщо ще не встановлено)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Оновлення шляхів (щоб uv став доступним)
source $HOME/.local/bin/env
```
### 2. Створення середовища та встановлення залежностей.
```bash
# Ініціалізація віртуального середовища
uv venv

# Активація середовища
source .venv/bin/activate

# Встановлення PyTorch з підтримкою CUDA для роботи на відеокарті
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Встановлення OpenCV та YOLO
uv pip install opencv-python ultralytics
```