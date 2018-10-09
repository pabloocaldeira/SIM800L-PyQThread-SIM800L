import serial
    def fn_SMS(self):
        SERIAL_PORT = "/dev/ttyS0"  # Rasp 3 UART Port
        global ser
        ser = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=5)

        ser.write("AT+CMGF=1\r")  # modo texto
        time.sleep(0.1)
        ser.write('AT+CMGDA="DEL ALL"\r')  # deleta todos SMS

        ser.write("AT+CMGS=\"")
        time.sleep(0.1)
        ser.write("+5553981075696")
        ser.write("\"\r")
        time.sleep(0.1)
        ser.write("Aguardando SMS")
        time.sleep(0.5)
        ser.write(chr(26))
        time.sleep(0.1)
        ser.write("")

        self.T_SMS = ThreadSMS()
        self.T_SMS.start()
        
class ThreadSMS(QtCore.QThread):
    TEXT = "vazio"
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.mRunning = True

    def run(self):
        global ser
        while self.mRunning:
            time.sleep(0.5)

            ser.write("AT+CMGR=1\r") #Modo Texto
            inbox = ser.read(ser.inWaiting()) #Faz a leitura da serial
            print("Aguardando...")
            try:
                self.TEXT = inbox.split('<')[1] #Tenta resgatar algum texto presente apos <
            except IndexError:
                self.TEXT = ""

            if "MECA" in self.TEXT.upper(): #Verifica se o texto "MECA" esta presente no SMS
                print ("SMS RECEBIDO")
                ser.write("AT+CMGF=1\r")  # set to text mode
                time.sleep(0.1)
                ser.write("AT+CMGS=\"") #enviar sms...
                time.sleep(0.1)
                ser.write("+5553981075696") #...para o numero
                ser.write("\"\r")
                time.sleep(0.1)
                ser.write("FEITO") #...texto do sms
                time.sleep(0.5)
                ser.write(chr(26)) #...ESC
                time.sleep(0.1)
                ser.write("")  #...linha em branco
                ser.write('AT+CMGDA="DEL ALL"\r')  # deleta os SMS da caixa de entrada
                time.sleep(0.1)

                ser.reset_input_buffer() # Limpa buffer de entrada da serial

    def stop(self):
        self.mRunning = False
