import serial

    """
    Ao clicar em um botao, eu chamo a funcao fn_SMS que envia um SMS para o meu numero
    Problemas: o código nesta seção não é executado de maneira paralela, ou seja, todo o resto (UI e Threads)
    ficam no aguardo do término da execução dessa função. É uma espera rápida, porém perceptível na interface gráfica.
    Mas está funcionando corretamente, pois o SMS chega pra mim.
    
    Após o envio deste SMS eu inicio uma thread que fica lendo a serial na espera de um recebimento de SMS. Isso sim está funcionano
    de maneira paralela.
    """

    def fn_SMS(self):
        SERIAL_PORT = "/dev/ttyS0"  # Rasp 3 UART Port
        global ser
        ser = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=5)

        ser.write("AT+CMGF=1\r")  # modo texto
        time.sleep(0.1)
        ser.write('AT+CMGDA="DEL ALL"\r')  # deleta todos SMS

        ser.write("AT+CMGS=\"")
        time.sleep(0.1)
        ser.write("+5553999999999")
        ser.write("\"\r")
        time.sleep(0.1)
        ser.write("Aguardando SMS")
        time.sleep(0.5)
        ser.write(chr(26))
        time.sleep(0.1)
        ser.write("")

        self.T_SMS = ThreadSMS()
        self.T_SMS.start()
        
        
"""
Meu problema dentro da Thread eh o seguinte:
Thread Inicia: OK
Aguardo por SMS: OK
Recebo o SMS: OK
Faco o reconhecimento do sms contendo "MECA": OK
Envio um SMS: OK
Limpo a serial: ? (acho que nao estou fazendo certo)
Continuo verificando a serial em looping... porem na leitura da serial, o SMS continua na serial e entrando
no 'if "MECA" in self.TEXT.upper():'

Existe uma maneira de eu limpar a serial, ou ainda fechar e abrir novamente?
"""        
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
                ser.write("+5553999999999") #...para o numero
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
