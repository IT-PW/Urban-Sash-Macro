import sys, os
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets
from fractions import Fraction
from fractions import Fraction

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle("Sash Cart Solution")
        Dialog.resize(492, 507)

        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(130, 390, 231, 85))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        
        self.title = QtWidgets.QLabel(Dialog)
        self.title.setGeometry(QtCore.QRect(60, 50, 411, 131))
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("Haettenschweiler")
        font.setPointSize(48)
        self.title.setFont(font)
        self.title.setObjectName("title")
        
        self.sash = QtWidgets.QLabel(Dialog)
        self.sash.setGeometry(QtCore.QRect(30, 160, 451, 180))
        self.sash.setAlignment(QtCore.Qt.AlignCenter)
        self.sash.setObjectName("sash")
        
        self.logo = QtWidgets.QLabel(Dialog)
        self.logo.setGeometry(QtCore.QRect(56, 10, 371, 81))
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        self.logo.setObjectName("logo")
        
        self.inputLineEdit = QtWidgets.QLineEdit(Dialog)
        self.inputLineEdit.setGeometry(QtCore.QRect(130, 56, 231, 90))
        self.inputLineEdit.setObjectName("inputLineEdit")
        
        self.outputTextEdit = QtWidgets.QTextEdit(Dialog)
        self.outputTextEdit.setGeometry(QtCore.QRect(130, 450, 231, 31))
        self.outputTextEdit.setReadOnly(True)
        self.outputTextEdit.setObjectName("outputTextEdit")
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        
        self.pushButton.clicked.connect(self.execute_process_file)

        #Radio button
        
        

    def execute_process_file(self):
        input_file_name = self.inputLineEdit.text()
        processed_data = self.process_file(input_file_name)
        
        
        self.write_processed_data(processed_data)

        self.outputTextEdit.setPlainText("Processing complete. Check the output file for the results.")

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Sash Cart Compiler", "Sash Cart Compiler"))
        self.pushButton.setText(_translate("Dialog", "Generate File!"))
        self.title.setText(_translate("Dialog", "Sash Cart Compiler"))
        self.sash.setText(_translate("Dialog", "Premium Windows, email us at help@premiumwindows.com"))
        self.logo.setText(_translate("Dialog", "Premium Windows, email us at help@premiumwindows.com"))


            
class MyDialog(QMainWindow, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        pixmap = QPixmap("images\Sash.jpg")
        self.sash.setPixmap(pixmap)
        self.sash.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)  
        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.sash)
        layout.addWidget(self.inputLineEdit)
        layout.addWidget(self.pushButton)
        layout.addWidget(self.outputTextEdit)
        layout.addWidget(self.logo)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
    
    
    def convert_to_fraction(self, decimal):
        float_value = float(decimal)
        
        # Convert the float value to a fraction rounded to the nearest 1/16
        fraction_value = round(float_value * 16) / 16
        
        # Extract the whole number and fraction parts
        whole_part = int(fraction_value)
        nearest_fraction = fraction_value - whole_part
        if nearest_fraction == 0.0:
            return f"{whole_part}"
        elif nearest_fraction == 0.0625:
            return f"{whole_part} 1/16"
        elif nearest_fraction == 0.125:
            return f"{whole_part} 1/8"
        elif nearest_fraction == 0.1875:
            return f"{whole_part} 3/16"
        elif nearest_fraction == 0.25:
            return f"{whole_part} 1/4"
        elif nearest_fraction == 0.3125:
            return f"{whole_part} 5/16"
        elif nearest_fraction == 0.375:
            return f"{whole_part} 3/8"
        elif nearest_fraction == 0.4375:
            return f"{whole_part} 7/16"
        elif nearest_fraction == 0.5:
            return f"{whole_part} 1/2"
        elif nearest_fraction == 0.5625:
            return f"{whole_part} 9/16"
        elif nearest_fraction == 0.625:
            return f"{whole_part} 5/8"
        elif nearest_fraction == 0.6875:
            return f"{whole_part} 11/16"
        elif nearest_fraction == 0.75:
            return f"{whole_part} 3/4"
        elif nearest_fraction == 0.8125:
            return f"{whole_part} 13/16"
        elif nearest_fraction == 0.875:
            return f"{whole_part} 7/8"
        else:
            return f"{whole_part} {nearest_fraction}"
        
       


    def process_file(self, filename):
        file_path = os.path.join("..", "Sash", filename)
        with open(file_path, 'r') as file:
            lines = file.readlines()

        
        # Remove the newline character from each line and split the fields by semicolon
        data = [line.strip().split(';') for line in lines]
        empty_spaces = []
        carts_and_slots = []
        
        # Sort the data based on the values in column 20 (index 19)
        sorted_cart = sorted(data, key=lambda x: float(x[19]))
        alt_car = sorted_cart[0][19]
        for row in sorted_cart:
            if "/" not in row[18]:
                row[18] = self.convert_to_fraction((row[18]))
            
        for row in sorted_cart:
            barcode = row[23]
            cart = row[19]
            slot = row[20]
            temp_slot = 0
            temp_car = 0
            row[4] = 0


            

            for temp1 in sorted_cart:
                #print(cart)
                if temp1[23] == barcode and temp1[4] == '1' and temp1[20] != slot:
                    temp_car = temp1[19]
                    temp_slot = temp1[20]
                    temp1[19] = cart
                    temp1[20] = slot
                    temp1[7] = cart
                    temp1[6] = slot
                    temp1[4] = 0
                    carts_and_slots = [temp_car, temp_slot]
                    empty_spaces.append(carts_and_slots)
                    
            
        if len(empty_spaces) > 0:
            numb = 0   
            index = empty_spaces[numb]
        
            for temp1 in sorted_cart:
                
                barcode = temp1[23]
                cart = temp1[19]
                slot = temp1[20]
                
                if temp1[19] != alt_car: 
                    for temp2 in sorted_cart:
                        if temp2[23] == barcode and temp2[4] == 0 and temp2[19] != alt_car:
                            temp2[19] = index[0]
                            temp2[20] = index[1]
                            temp2[7] =  index[0]
                            temp2[6] =  index[1]
                    numb += 2      
                    if numb < len(empty_spaces):
                        index = empty_spaces[numb]
                        
                    else:
                        # Handle the case when numb is out of range
                        print("numb is out of range:", numb)
                    
                
                
        data = sorted(sorted_cart, key=lambda x: float(x[0]))
        pardir = ".."
        new_file = data[0][5]+"-SH.txt"
        with open(os.path.join(os.pardir, new_file), "w") as f:
            for sublist in data:
                sublist[4] = '1'
                string_sublist = [str(item) for item in sublist]  # Convert each element to string
                line = ';'.join(string_sublist) + '\n'
                print(line)
                f.write(line)
        return data 

    def execute_process_file(self):
        input_file_name = self.inputLineEdit.text()
        processed_data = self.process_file(input_file_name)
        
        # Capture the output as a string
        output_text = ""
        for line in processed_data:
            output_text += ';'.join(map(str, line)) + '\n'

        # Set the output text in the QTextEdit
        self.outputTextEdit.setPlainText(output_text)
        self.outputTextEdit.append("Processing complete. Check the output file for the results.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MyDialog()
    dialog.show()
    sys.exit(app.exec_())        
    
   




