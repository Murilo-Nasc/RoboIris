# RoboIris

Repositório ROS 2 para o controle e operação do robô **RoboIris**, desenvolvido com motores de hoverboard, câmera, e nós personalizados. Este repositório contém todos os pacotes relacionados ao projeto, incluindo controle de movimento, detecção de objetos, comunicação com Arduino e captura de vídeo.

---

## 📦 Sobre

Este repositório foi criado para armazenar e organizar os pacotes ROS 2 utilizados no robô **RoboIris**, integrando funcionalidades de visão computacional, controle de motores, comunicação serial e mais.

---

## 📥 Importar o repositório

Para clonar o repositório:

```bash
git clone --recurse-submodules https://github.com/Murilo-Nasc/RoboIris.git
cd RoboIris
```

Como este workspace segue a estrutura padrão do ROS 2 (src/ contendo os pacotes), você deve compilar e "sourcear" o ambiente após clonar:

```source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

---

## 📦 Sobre os pacotes

### `arduino_bridge`
Comunicação serial entre o ROS 2 e o microcontrolador (Arduino ou similar). Utilizado para envio de comandos aos motores.

### `object_detector`
Pacote de visão computacional com detecção de objetos utilizando OpenCV ou YOLO.

### `face_detector`
Detecta rostos via câmera e envia eventos para o sistema de navegação ou interação.

### `ros2_v4l2_camera`
Pacote para publicar frames da câmera física via o tópico `/image_raw`.
