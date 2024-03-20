# UART Tx/Rx demo
import tkinter as tk
from tkinter import ttk
import serial
import threading


# A simple Information Window
class InformWindow:
    def __init__(self, informStr):
        self.window = tk.Tk()
        self.window.title("Information")
        self.window.geometry("220x60")
        label = tk.Label(self.window, text=informStr)
        buttonOK = tk.Button(self.window, text="OK", command=self.processButtonOK)
        label.pack(side=tk.TOP)
        buttonOK.pack(side=tk.BOTTOM)
        self.window.mainloop()

    def processButtonOK(self):
        self.window.destroy()


class mainGUI:
    def __init__(self):
        window = tk.Tk()
        window.title("GUI Bluetooth UART Tx/Rx Demo")
        self.uartState = False  # is uart open or not

        # a frame contains COM's information, and start/stop button
        frame_COMinf = tk.Frame(window)
        frame_COMinf.grid(row=1, column=1)

        labelCOM = tk.Label(frame_COMinf, text="COMx: ")
        self.COM = tk.StringVar(value="COM9")
        ertryCOM = tk.Entry(frame_COMinf, textvariable=self.COM)
        labelCOM.grid(row=1, column=1, padx=5, pady=3)
        ertryCOM.grid(row=1, column=2, padx=5, pady=3)

        labelBaudrate = tk.Label(frame_COMinf, text="Baudrate: ")
        self.Baudrate = tk.IntVar(value=9600)
        ertryBaudrate = tk.Entry(frame_COMinf, textvariable=self.Baudrate)
        labelBaudrate.grid(row=1, column=3, padx=5, pady=3)
        ertryBaudrate.grid(row=1, column=4, padx=5, pady=3)

        labelParity = tk.Label(frame_COMinf, text="Parity: ")
        self.Parity = tk.StringVar(value="NONE")
        comboParity = ttk.Combobox(frame_COMinf, width=17, textvariable=self.Parity)
        comboParity["values"] = ("NONE", "ODD", "EVEN", "MARK", "SPACE")
        comboParity["state"] = "readonly"
        labelParity.grid(row=2, column=1, padx=5, pady=3)
        comboParity.grid(row=2, column=2, padx=5, pady=3)

        labelStopbits = tk.Label(frame_COMinf, text="Stopbits: ")
        self.Stopbits = tk.StringVar(value="1")
        comboStopbits = ttk.Combobox(frame_COMinf, width=17, textvariable=self.Stopbits)
        comboStopbits["values"] = ("1", "1.5", "2")
        comboStopbits["state"] = "readonly"
        labelStopbits.grid(row=2, column=3, padx=5, pady=3)
        comboStopbits.grid(row=2, column=4, padx=5, pady=3)

        self.buttonSS = tk.Button(frame_COMinf, text="Start", command=self.processButtonSS)
        self.buttonSS.grid(row=3, column=4, padx=5, pady=3, sticky=tk.E)

        # serial object
        self.ser = serial.Serial()
        # serial read threading
        self.ReadUARTThread = threading.Thread(target=self.ReadUART)
        self.ReadUARTThread.start()

        frameRecv = tk.Frame(window)
        frameRecv.grid(row=2, column=1)
        labelOutText = tk.Label(frameRecv, text="Received Data:")
        labelOutText.grid(row=1, column=1, padx=3, pady=2, sticky=tk.W)
        frameRecvSon = tk.Frame(frameRecv)
        frameRecvSon.grid(row=2, column=1)
        scrollbarRecv = tk.Scrollbar(frameRecvSon)
        scrollbarRecv.pack(side=tk.RIGHT, fill=tk.Y)
        self.OutputText = tk.Text(frameRecvSon, wrap=tk.WORD, width=60, height=30, yscrollcommand=scrollbarRecv.set)
        self.OutputText.pack()

        frameTrans = tk.Frame(window)
        frameTrans.grid(row=3, column=1)
        labelInText = tk.Label(frameTrans, text="To Transmit Data:")
        labelInText.grid(row=1, column=1, padx=3, pady=2, sticky=tk.W)
        frameTransSon = tk.Frame(frameTrans)
        frameTransSon.grid(row=2, column=1)
        scrollbarTrans = tk.Scrollbar(frameTransSon)
        scrollbarTrans.pack(side=tk.RIGHT, fill=tk.Y)
        self.InputText = tk.Text(frameTransSon, wrap=tk.WORD, width=60, height=5, yscrollcommand=scrollbarTrans.set)
        self.InputText.pack()
        self.buttonSend = tk.Button(frameTrans, text="Send", command=self.processButtonSend)
        self.buttonSend.grid(row=3, column=1, padx=5, pady=3, sticky=tk.E)


        # 参数变量调整
        frameVar = tk.Frame(window)
        frameVar.grid(row=1, column=2)
        labelVarText = tk.Label(frameVar, text="Important parameters:")
        labelVarText.grid(row=1, column=1, padx=3, pady=2, sticky=tk.N)

        frameVarSon = tk.Frame(frameVar)
        frameVarSon.grid(row=2, column=1)

        labelTs = tk.Label(frameVarSon, text="Sp: ")
        self.Ts = tk.StringVar(value=150)
        EntryTs = tk.Entry(frameVarSon, textvariable = self.Ts)
        labelTs.grid(row=1, column=1, padx=5, pady=3)
        EntryTs.grid(row=1, column=2, padx=5, pady=3)

        labelXs = tk.Label(frameVarSon, text="Xs: ")
        self.Xs = tk.StringVar(value=0)
        EntryXs = tk.Entry(frameVarSon, textvariable = self.Xs)
        labelXs.grid(row=1, column=3, padx=5, pady=3)
        EntryXs.grid(row=1, column=4, padx=5, pady=3)

        labelXf = tk.Label(frameVarSon, text="Xf: ")
        self.Xf = tk.StringVar(value=60)
        EntryXf = tk.Entry(frameVarSon, textvariable=self.Xf)
        labelXf.grid(row=2, column=1, padx=5, pady=3)
        EntryXf.grid(row=2, column=2, padx=5, pady=3)

        labelH = tk.Label(frameVarSon, text="H: ")
        self.H = tk.StringVar(value=60)
        EntryH = tk.Entry(frameVarSon, textvariable=self.H)
        labelH.grid(row=2, column=3, padx=5, pady=3)
        EntryH.grid(row=2, column=4, padx=5, pady=3)

        labelR1 = tk.Label(frameVarSon, text="R1: ")
        self.R1 = tk.StringVar(value=1)
        EntryR1 = tk.Entry(frameVarSon, textvariable=self.R1)
        labelR1.grid(row=3, column=1, padx=5, pady=3)
        EntryR1.grid(row=3, column=2, padx=5, pady=3)

        labelR2 = tk.Label(frameVarSon, text="R2 ")
        self.R2 = tk.StringVar(value=1)
        EntryR2 = tk.Entry(frameVarSon, textvariable=self.R2)
        labelR2.grid(row=3, column=3, padx=5, pady=3)
        EntryR2.grid(row=3, column=4, padx=5, pady=3)

        labelR3 = tk.Label(frameVarSon, text="R3: ")
        self.R3 = tk.StringVar(value=1)
        EntryR3 = tk.Entry(frameVarSon, textvariable=self.R3)
        labelR3.grid(row=4, column=1, padx=5, pady=3)
        EntryR3.grid(row=4, column=2, padx=5, pady=3)

        labelR4 = tk.Label(frameVarSon, text="R4: ")
        self.R4 = tk.StringVar(value=1)
        EntryR4 = tk.Entry(frameVarSon, textvariable=self.R4)
        labelR4.grid(row=4, column=3, padx=5, pady=3)
        EntryR4.grid(row=4, column=4, padx=5, pady=3)

        # 动作组设计

        frameMotion = tk.Frame(window)
        frameMotion.grid(row=2, column=2)
        labelMotionText = tk.Label(frameMotion, text="Dog Motion")
        labelMotionText.grid(row=1, column=1, padx=3, pady=2, sticky=tk.N)

        frameMotionSon = tk.Frame(frameMotion)
        frameMotionSon.grid(row=2, column=1)

        self.buttonMotion00 = tk.Button(frameMotionSon, text="Trot", width=15, height=4, command=self.processButtonMotion00)
        self.buttonMotion00.grid(row=0, column=1, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion01 = tk.Button(frameMotionSon, text="Walk", width=15, height=4, command=self.processButtonMotion01)
        self.buttonMotion01.grid(row=0, column=2, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion02 = tk.Button(frameMotionSon, text="Step", width=15, height=4, command=self.processButtonMotion02)
        self.buttonMotion02.grid(row=0, column=3, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion03 = tk.Button(frameMotionSon, text="Stand", width=15, height=4, command=self.processButtonMotion03)
        self.buttonMotion03.grid(row=0, column=4, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion04 = tk.Button(frameMotionSon, text="Crab_L", width=15, height=4,
                                        command=self.processButtonMotion04)
        self.buttonMotion04.grid(row=1, column=1, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion05 = tk.Button(frameMotionSon, text="Round_L", width=15, height=4,
                                        command=self.processButtonMotion05)
        self.buttonMotion05.grid(row=1, column=2, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion06 = tk.Button(frameMotionSon, text="Round_R", width=15, height=4,
                                        command=self.processButtonMotion06)
        self.buttonMotion06.grid(row=1, column=3, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion07 = tk.Button(frameMotionSon, text="Crab_R", width=15, height=4,
                                        command=self.processButtonMotion07)
        self.buttonMotion07.grid(row=1, column=4, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion08 = tk.Button(frameMotionSon, text="Balance", width=15, height=4,
                                        command=self.processButtonMotion08)
        self.buttonMotion08.grid(row=2, column=1, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion09 = tk.Button(frameMotionSon, text="Dance", width=15, height=4,
                                        command=self.processButtonMotion09)
        self.buttonMotion09.grid(row=2, column=2, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion10 = tk.Button(frameMotionSon, text="Zero", width=15, height=4,
                                        command=self.processButtonMotion10)
        self.buttonMotion10.grid(row=2, column=3, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion11 = tk.Button(frameMotionSon, text="Power_down", width=15, height=4,
                                        command=self.processButtonMotion11)
        self.buttonMotion11.grid(row=2, column=4, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion12 = tk.Button(frameMotionSon, text="void", width=15, height=4,
                                        command=self.processButtonMotion12)
        self.buttonMotion12.grid(row=3, column=1, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion13 = tk.Button(frameMotionSon, text="void", width=15, height=4,
                                        command=self.processButtonMotion13)
        self.buttonMotion13.grid(row=3, column=2, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion14 = tk.Button(frameMotionSon, text="void", width=15, height=4,
                                        command=self.processButtonMotion14)
        self.buttonMotion14.grid(row=3, column=3, padx=5, pady=3, sticky=tk.E)

        self.buttonMotion15 = tk.Button(frameMotionSon, text="void", width=15, height=4,
                                        command=self.processButtonMotion15)
        self.buttonMotion15.grid(row=3, column=4, padx=5, pady=3, sticky=tk.E)


        # 运动状态调试

        frameState = tk.Frame(window)
        frameState.grid(row=3, column=2)
        labelStateText = tk.Label(frameState, text="Dog state")
        labelStateText.grid(row=1, column=1, padx=3, pady=2, sticky=tk.N)

        frameStateSon = tk.Frame(frameState)
        frameStateSon.grid(row=2, column=1)

        self.buttonTrot = tk.Button(frameStateSon, text="Trot",width=15, height=3, command=self.processButtonTrot)
        self.buttonTrot.grid(row=2, column=1, padx=5, pady=3, sticky=tk.E)

        self.buttonWalk = tk.Button(frameStateSon, text="Walk",width=15, height=3, command=self.processButtonWalk)
        self.buttonWalk.grid(row=2, column=2, padx=5, pady=3, sticky=tk.E)

        self.buttonCrab = tk.Button(frameStateSon, text="Crab", width=15, height=3, command=self.processButtonCrab)
        self.buttonCrab.grid(row=2, column=3, padx=5, pady=3, sticky=tk.E)

        self.buttonRound = tk.Button(frameStateSon, text="Round", width=15, height=3, command=self.processButtonRound)
        self.buttonRound.grid(row=2, column=4, padx=5, pady=3, sticky=tk.E)




        window.mainloop()

    def processButtonSS(self):
        # print(self.Parity.get())
        if (self.uartState):
            self.ser.close()
            self.buttonSS["text"] = "Start"
            self.uartState = False
        else:
            # restart serial port
            self.ser.port = self.COM.get()
            self.ser.baudrate = self.Baudrate.get()

            strParity = self.Parity.get()
            if (strParity == "NONE"):
                self.ser.parity = serial.PARITY_NONE
            elif (strParity == "ODD"):
                self.ser.parity = serial.PARITY_ODD
            elif (strParity == "EVEN"):
                self.ser.parity = serial.PARITY_EVEN
            elif (strParity == "MARK"):
                self.ser.parity = serial.PARITY_MARK
            elif (strParity == "SPACE"):
                self.ser.parity = serial.PARITY_SPACE

            strStopbits = self.Stopbits.get()
            if (strStopbits == "1"):
                self.ser.stopbits = serial.STOPBITS_ONE
            elif (strStopbits == "1.5"):
                self.ser.stopbits = serial.STOPBITS_ONE_POINT_FIVE
            elif (strStopbits == "2"):
                self.ser.stopbits = serial.STOPBITS_TWO

            try:
                self.ser.open()
            except:
                infromStr = "Can't open " + self.ser.port
                InformWindow(infromStr)

            if (self.ser.isOpen()):  # open success
                self.buttonSS["text"] = "Stop"
                self.uartState = True

    def processButtonSend(self):
        if (self.uartState):
            strToSend = self.InputText.get(1.0, tk.END)
            bytesToSend = strToSend[0:-1].encode(encoding='ascii')
            self.ser.write(bytesToSend)
            print(bytesToSend)
        else:
            infromStr = "Not In Connect!"
            InformWindow(infromStr)

    def ReadUART(self):
        # print("Threading...")
        while True:
            if (self.uartState):
                try:
                    ch = self.ser.read().decode(encoding='ascii')
                    print(ch, end='')
                    self.OutputText.insert(tk.END, ch)
                except:
                    infromStr = "Something wrong in receiving."
                    InformWindow(infromStr)
                    self.ser.close()  # close the serial when catch exception
                    self.buttonSS["text"] = "Start"
                    self.uartState = False

    def processButtonTrot(self):
        self.DogStateControlSend(0)
        return
    def processButtonWalk(self):
        self.DogStateControlSend(1)
        return
    def processButtonCrab(self):
        self.DogStateControlSend(2)
        return
    def processButtonRound(self):
        self.DogStateControlSend(3)
        return

    def processButtonMotion00(self):
        self.processButtonMotion(0)
        return

    def processButtonMotion01(self):
        self.processButtonMotion(1)
        return

    def processButtonMotion02(self):
        self.processButtonMotion(2)
        return

    def processButtonMotion03(self):
        self.processButtonMotion(3)
        return

    def processButtonMotion04(self):
        self.processButtonMotion(4)
        return

    def processButtonMotion05(self):
        self.processButtonMotion(5)
        return

    def processButtonMotion06(self):
        self.processButtonMotion(6)
        return

    def processButtonMotion07(self):
        self.processButtonMotion(7)
        return

    def processButtonMotion08(self):
        self.processButtonMotion(8)
        return

    def processButtonMotion09(self):
        self.processButtonMotion(9)
        return

    def processButtonMotion10(self):
        self.processButtonMotion(10)
        return

    def processButtonMotion11(self):
        self.processButtonMotion(11)
        return

    def processButtonMotion12(self):
        self.processButtonMotion(12)
        return

    def processButtonMotion13(self):
        self.processButtonMotion(13)
        return

    def processButtonMotion14(self):
        self.processButtonMotion(14)
        return

    def processButtonMotion15(self):
        self.processButtonMotion(15)
        return

    def processButtonMotion(self, MotionVar):
        if (self.uartState):
            FRAME_HEADER = 0x55;
            FRAME_LENGTH = 0x03;
            FRAME_DogMotion = 0x02;
            strToSend = chr(FRAME_HEADER)+ chr(FRAME_HEADER) + chr(FRAME_LENGTH) + chr(FRAME_DogMotion) + chr(MotionVar) +"\n\r"
            bytesToSend = strToSend[0:-1].encode(encoding='ascii')
            self.ser.write(bytesToSend)
            print(bytesToSend)
        else:
            infromStr = "Not In Connect!"
            InformWindow(infromStr)
        return

    def DogStateControlSend(self, dogStatevar):
        if (self.uartState):
            FRAME_HEADER = 0x55;
            FRAME_LENGTH = 0x0B;
            FRAME_DogState = 0x01;
            strToSend = chr(FRAME_HEADER)+ chr(FRAME_HEADER) + chr(FRAME_LENGTH) + chr(FRAME_DogState) + chr(dogStatevar) +' '\
                        + self.Ts.get()+' '+ self.Xs.get()+' '+self.Xf.get()+' '+self.H.get()+' '\
                        + self.R1.get()+' '+ self.R2.get()+' '+self.R3.get()+' '+self.R4.get()+' '+"\n\r"
            bytesToSend = strToSend[0:-1].encode(encoding='ascii')
            self.ser.write(bytesToSend)
            print(bytesToSend)
        else:
            infromStr = "Not In Connect!"
            InformWindow(infromStr)


mainGUI()
