from flask import Flask, request, jsonify, render_template_string
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import logging
import time
import keyboard

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the volume interface
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Inline HTML Template
html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="Author" content="Niranga Nayanajithan" />
  <link rel="icon" href="1.jpeg" type="image/x-icon">
  <title>Mobile Mouse</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      background-color: #f0f0f0;
      color: #333;
      background-image: url("1.jpeg");
    }

    h1 {
      margin-top: 20px;
    }

    header h1 {
      font-size: 45px;
      margin: 0;
      padding: 2px;
    }

    .button-container {
      display: flex;
      gap: 10px; /* Space between buttons */
    }

    #loginBtn, #Support {
      background-color: #520d6b;
      color: white;
      border: none;
      padding: 10px 150px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 10px;
      transition: background-color 0.3s ease;
      
    }

    #loginBtn:hover, #Support:hover {
      background-color:  #1d0320;
    }


    button {
      margin: 10px;
      padding: 10px 20px;
      font-size: 16px;
      border: none;
      background-color: #4CAF50;
      color: white;
      cursor: pointer;
      border-radius: 5px;
      transition: background-color 0.3s;
    }

    button:hover {
      background-color: #45a049;
    }

    #joystick-container, #scroll-joystick-container {
      position: relative;
      margin: 20px auto;
      background-color: lightgray;
      border-radius: 50%;
      touch-action: none;
      border: 2px solid #ccc;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }

    #joystick-container {
      width: 200px;
      height: 200px;
    }

    #scroll-joystick-container {
      width: 100px;
      height: 100px;
    }

    #joystick, #scroll-joystick {
      position: absolute;
      background-color: #888;
      border-radius: 50%;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      touch-action: none;
      transition: transform 0.1s, background-color 0.3s;
      box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
    }

    #joystick {
      width: 60px;
      height: 60px;
    }

    #scroll-joystick {
      width: 40px;
      height: 40px;
    }

    #joystick:active, #scroll-joystick:active {
      background-color: #555;
    }

    #control-panel {
      text-align: center;
    }

    .control-buttons {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      margin-top: 20px;
    }

    .control-buttons button {
      margin: 5px;
      padding: 10px 20px;
      font-size: 16px;
    }

    #volume-slider {
      width: 200px;
      margin: 20px auto;
      appearance: none;
      height: 10px;
      background: #ddd;
      outline: none;
      opacity: 0.7;
      transition: opacity 0.2s;
    }

    #volume-slider:hover {
      opacity: 1;
    }

    #volume-slider::-webkit-slider-thumb {
      appearance: none;
      width: 20px;
      height: 20px;
      background: #4CAF50;
      cursor: pointer;
      border-radius: 50%;
      box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
    }

    #volume-slider::-moz-range-thumb {
      width: 20px;
      height: 20px;
      background: #4CAF50;
      cursor: pointer;
      border-radius: 50%;
      box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
    }
  </style>
</head>
<body>
  <header>
    <h1>Mobile Mouse</h1>
    <div class="button-container">
      <button id="Support">Contact</button>
    </div>
  </header>

  <button id="connect-mobile">Connect Mobile</button>

  <div id="control-panel" style="display: none;">
    <div id="joystick-container">
      <div id="joystick"></div>
    </div>
    <div id="scroll-joystick-container" style="display: none;">
      <div id="scroll-joystick"></div>
    </div>
    <div id="connected-message" style="display: none;">Connected</div>
    <div class="control-buttons">
      <button id="click" style="display: none;">Click</button>
      <button id="double-click" style="display: none;">Double Click</button>
      <button id="right-click" style="display: none;">Right Click</button>
      <button id="keyboard">Keyboard</button>
      <button id="backspace">Backspace</button>

    </div>
    <input type="range" id="volume-slider" min="0" max="1" step="0.01" value="0.5">
  </div>

  <script>
    let joystick = document.getElementById('joystick');
    let joystickContainer = document.getElementById('joystick-container');
    let scrollJoystick = document.getElementById('scroll-joystick');
    let scrollJoystickContainer = document.getElementById('scroll-joystick-container');
    let active = false;
    let moveInterval = null;

    joystick.addEventListener('touchstart', function(e) {
      e.preventDefault();
      active = true;
      startMoving(e.touches[0], joystick, joystickContainer, sendMouseMovement);
    });

    joystick.addEventListener('touchmove', function(e) {
      e.preventDefault();
      if (active) {
        startMoving(e.touches[0], joystick, joystickContainer, sendMouseMovement);
      }
    });

    joystick.addEventListener('touchend', function(e) {
      e.preventDefault();
      stopMoving(joystick);
      active = false;
    });

    scrollJoystick.addEventListener('touchstart', function(e) {
      e.preventDefault();
      active = true;
      startMoving(e.touches[0], scrollJoystick, scrollJoystickContainer, sendScrollMovement);
    });

    scrollJoystick.addEventListener('touchmove', function(e) {
      e.preventDefault();
      if (active) {
        startMoving(e.touches[0], scrollJoystick, scrollJoystickContainer, sendScrollMovement);
      }
    });

    scrollJoystick.addEventListener('touchend', function(e) {
      e.preventDefault();
      stopMoving(scrollJoystick);
      active = false;
    });

    function startMoving(touch, joystick, container, sendMovement) {
      let rect = container.getBoundingClientRect();
      let x = touch.clientX - rect.left - rect.width / 2;
      let y = touch.clientY - rect.top - rect.height / 2;
      let angle = Math.atan2(y, x);
      let distance = Math.min(rect.width / 2, Math.hypot(x, y));
      joystick.style.transform = `translate(${distance * Math.cos(angle) - joystick.offsetWidth / 2}px, ${distance * Math.sin(angle) - joystick.offsetHeight / 2}px)`;

      if (moveInterval) clearInterval(moveInterval);
      moveInterval = setInterval(() => {
        sendMovement(x / rect.width, y / rect.height);
      }, 50); // Reduced interval for smoother updates
    }

    function stopMoving(joystick) {
      joystick.style.transform = 'translate(-50%, -50%)';
      if (moveInterval) clearInterval(moveInterval);
    }

    function sendMouseMovement(x, y) {
      fetch('/move_mouse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ x, y }),
      });
    }

    function sendScrollMovement(x, y) {
      fetch('/scroll_mouse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ x, y }),
      });
    }

    document.getElementById('connect-mobile').addEventListener('click', () => {
      document.getElementById('control-panel').style.display = 'block';
      document.getElementById('scroll-joystick-container').style.display = 'block';
      document.getElementById('click').style.display = 'inline-block';
      document.getElementById('double-click').style.display = 'inline-block';
      document.getElementById('right-click').style.display = 'inline-block';
      document.getElementById('keyboard').style.display = 'inline-block';
      document.getElementById('backspace').style.display = 'inline-block';
    });

    document.getElementById('click').addEventListener('click', () => {
      fetch('/click', { method: 'POST' });
    });

    document.getElementById('double-click').addEventListener('click', () => {
      fetch('/double_click', { method: 'POST' });
    });
    document.getElementById('backspace').addEventListener('click', () => {
      fetch('/backspace', { method: 'POST' });
      });

    document.getElementById('right-click').addEventListener('click', () => {
      fetch('/right_click', { method: 'POST' });
    });
      document.getElementById('keyboard').addEventListener('click', () => {
      let keyboard = document.createElement('input');
      keyboard.type = 'text';
      keyboard.style.position = 'absolute';
      keyboard.style.left = '-9999px';
      document.body.appendChild(keyboard);
      keyboard.focus();
      
      keyboard.addEventListener('input', () => {
        fetch('/keyboard_input', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ input: keyboard.value }),
        });
        keyboard.value = ''; // Clear the input after sending
      });
      
      // Clean up
      keyboard.addEventListener('blur', () => {
        document.body.removeChild(keyboard);
      });
    });

    document.getElementById('volume-slider').addEventListener('input', (event) => {
      fetch('/set_volume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ volume: event.target.value }),
      });

    });
  </script>
    <footer>
        <p>&copy; <a href="https://www.linkedin.com/in/niranga-nayanajith-548a0a302/" target="_blank">2N Tech</a>. All rights reserved.</p>
    </footer>  
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_code)

@app.route('/move_mouse', methods=['POST'])
def move_mouse():
    data = request.get_json()
    x, y = data['x'], data['y']
    screen_width, screen_height = pyautogui.size()
    move_x = int(x * screen_width * 0.1)  # Scale the movement
    move_y = int(y * screen_height * 0.1)  # Scale the movement
    pyautogui.move(move_x, move_y)
    return jsonify(status='success')

@app.route('/scroll_mouse', methods=['POST'])
def scroll_mouse():
    data = request.get_json()
    x, y = data['x'], data['y']
    scroll_amount = int(y * 10)  # Scale the scroll movement
    pyautogui.scroll(scroll_amount)
    return jsonify(status='success')

@app.route('/click', methods=['POST'])
def click():
    pyautogui.click()
    return jsonify(status='success')

@app.route('/double_click', methods=['POST'])
def double_click():
    pyautogui.doubleClick()
    return jsonify(status='success')

@app.route('/right_click', methods=['POST'])
def right_click():
    pyautogui.rightClick()
    return jsonify(status='success')

@app.route('/set_volume', methods=['POST'])
def set_volume():
    data = request.get_json()
    volume_level = float(data['volume'])
    volume.SetMasterVolumeLevelScalar(volume_level, None)
    return jsonify(status='success')
@app.route('/keyboard_input', methods=['POST'])
def keyboard_input():
    data = request.get_json()
    text = data.get('input', '')
    for char in text:
        keyboard.write(char)  # Simulate keypresses
    return jsonify(status='success')
@app.route('/backspace', methods=['POST'])
def backspace():
    keyboard.press_and_release('backspace')
    return jsonify(status='success')



if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

