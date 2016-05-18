import threading
import time
import serial


class weight_reader (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.weight_lock = threading.Lock()
        self.last_weight = 0

    def run(self):
        serial_port = None
        while serial_port is None:
            serial_port = self.open_serial_port()
            time.sleep(0.5)

        while True:
            byte_buffer = serial_port.readline()

            if len(byte_buffer) > 0:
                # "ST,GS,+  9.525g   \r\n"
                the_line = byte_buffer.decode(encoding='ascii', errors='ignore')
                print("Read line from port: %s" % the_line[0:19])   # Last 2 characters are \r\n

                unit = the_line[14:18]
                if 'g' in unit:
                    weight = the_line[6:14]
                    weight = weight.replace("+", "").replace(" ", "")
                    weight = float(weight)

                    self.weight_lock.acquire()
                    self.last_weight = weight
                    self.weight_lock.release()

                    print("Parsed %sg" % weight)
                else:
                    print("Grams NOT detected in UNIT")

    def get_last_weight(self):
        self.weight_lock.acquire()
        ret = self.last_weight
        self.weight_lock.release()
        return ret

    @staticmethod
    def open_serial_port():
        com_port = "/dev/tty.usbserial-A104WBQ0"
        print("Attempting to open serial port %s " % com_port)
        ret = None
        try:
            ret = serial.Serial(com_port, 9600, bytesize=serial.SEVENBITS,
                                parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE,
                                timeout=1,  # Timeout while waiting for a readLine()
                                xonxoff=False, rtscts=False, dsrdtr=False)
            print("Opened " + ret.portstr + " serial port")
        except:
            print("Error opening com port %s" % com_port)

        return ret

    @staticmethod
    def scan_ports():
        print("Scanning ports...")
        for n,s in weight_reader.scan():
            print("(%d) %s" % (n,s))
        print("Port scan done.")

    # scan for available ports. return a list of tuples (num, name)
    @staticmethod
    def scan():
        available = []
        for i in range(256):
            try:
                s = serial.Serial(str(i))
                available.append((i, s.portstr))
                s.close()
            except serial.SerialException:
                pass

        return available