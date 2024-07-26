import serial
import time
from threading import Lock, Thread

class ArduinoData:
    def __init__(self, portVar, baudrate, timeout):
        self.name = portVar
        self.code = "#self.angle - current angle\n#self.target - target temperature (immutable)\n#temp - current temperature"
        self.statusLock = Lock()
        self.status = "Empty"
        self.ser = serial.Serial(portVar, baudrate, timeout=timeout)
        self.target = 2500
        self.angle = 0
        self.test()
        
    def test(self):
        t = Thread(target=self.check)
        t.start()
        
    def check(self):
        with self.statusLock:
            self.status = "Testing"
        time.sleep(5)
        try:
            cnt = 0
            for i in range(100):
                self.ser.write("test\n".encode())
                data = self.ser.readline().decode('utf-8').rstrip()
                if data == "test": cnt += 1
            with self.statusLock:
                if cnt < 100:
                    print(cnt)
                    self.status = "Error: data lost during transmission"
                else: self.status = "Success"
        except:
            with self.statusLock:
                self.status = "Error: could not transfer data"
    
    def control(self, temp):
        try:
            exec(self.code, globals(), {"temp": temp, "self": self})
            try:
                self.ser.write((f"set {self.angle}\n").encode())
                data = self.ser.readline().decode('utf-8').rstrip()
                print("data: " + data)
            except:
                self.status = "Error: could not transfer data" 
        except:
            self.status = "Error: code execution error"
        
                