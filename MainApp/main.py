from unicodedata import name
import cv2
from random import randint
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from os import listdir

Builder.load_string("""
<MenuScreen>:
    imagen: 
    GridLayout:
        cols:2
    
        Button:
            text:'Scrap'
            on_press: root.sm_u('scrap')

        Button:
            text:'Crear formato'
            on_press: root.sm_u('new_format')

        Button:
            text:'Convertir pdfs'
            on_press: root.sm_u('pdf_convert')

<LoginScreen>
    GridLayout:
        rows:2
        GridLayout:
            cols:2
            rows:2             
            Label:
                text:'Usuario'
            TextInput:
                id:1
                text:'text'
            Label:
                text:'Contraseña'
            TextInput:
                id:2
                text:'text'
        Button:
            text:'Entrar'
            on_press: root.sm_u()

<PdfConvertScreen>
    GridLayout:
        rows:2
        Button:
            text:'Convertir PDFs'
            on_press: root.pdf_convert()

<NewFormatScreen>
    GridLayout:
        rows:3

        GridLayout:
            cols:2
            Label:
                text:'Nombre del archivo jpg:'

            TextInput:
                id:file

        GridLayout:
            cols:3
            Label:
                text:'Nombre del formato:'

            TextInput:
                id:format

        GridLayout:
            cols:3
            Button:
                text:'Crear'
                on_press: root.new_format()

            Button:
                text:'Reiniciar'

            
            Button:
                text:'Guardar'
<ScrapScreen>
    GridLayout:
        rows:2

        GridLayout:
            cols:2
            Label:
                text:'Formato .csv:'

            TextInput:
                id:format

        Button:
            text:'Scrap'
            on_press: root.scrap()
""")

class LoginScreen(Screen):
    def sm_u(self):
        self.manager.current = 'menu'

class PdfConvertScreen(Screen):
    def pdf_convert(self):
        from pdf2image import convert_from_path

        path = "documentos/pdfs"
        pdfs = listdir(path)
        to_path = "documentos/jpgs"

        for pdf in pdfs:
            pages = convert_from_path(f"{path}/{pdf}", 350)

            image_name = f"{to_path}/{pdf}.jpg"  
            pages[0].save(image_name, "JPEG")
        
        self.manager.current = 'menu'

class NewFormatScreen(Screen):
    def new_format(self):
        format = self.ids.format.text
        file = self.ids.file.text
        path=f"documentos/jpgs/{file}"
        f = open(f"formatos/{format}.csv", 'a')

        def create_rec():
            cv2.rectangle(imagen,(first[0], first[1]),(last[0], last[1]),(0,0,255),3)
            cv2.imshow('', imagen)


        def click_event(event, x, y, flags, params):
            if event == cv2.EVENT_LBUTTONDOWN:
                first[0] = x
                first[1] = y

                cv2.circle(imagen,(first[0], first[1]),1,(0,0,255),20)
                cv2.imshow('', imagen)

            if event == cv2.EVENT_RBUTTONDOWN:
                last[0] = x
                last[1] = y

                f.write(str(first[0]) + 
                ';' + str(first[1]) + 
                ';' + str(last[0]) + ';' +
                str(last[1]) + '\n')
            
                create_rec()

        first = [0, 0]
        last = [0, 0]

        imagen = cv2.imread(path)
        cv2.imshow('', imagen)
        cv2.setMouseCallback('', click_event)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        f.close()
    
        self.manager.current = 'menu'

class ScrapScreen(Screen):
    def scrap(self):
        import pytesseract
        import os

        format = f"formatos/{self.ids.format.text}"
        PATH_JPG = "documentos/jpgs"
        BASE = "base de datos/facturas.csv"

        jpg=PATH_JPG
        base=BASE

        def organizar(text):
            x = ""
            for i in text:
                if i != '':
                    x += i
                
                else:
                    break

            return x

        jpgs = os.listdir(jpg)

        coords = []
        f = open(format, 'r')
        lines = f.readlines()

        for i in lines:
            i = i.split(';')
            i[0] = int(i[0])
            i[1] = int(i[1])
            i[2] = int(i[2])
            i[3] = int(i[3][:-1])
            coords.append(i)

        f = open(base, 'a')

        for i in jpgs:
            imagen = cv2.imread(f"{jpg}/{i}")
            
            for c in coords:
                cv2.rectangle(imagen,(c[0], c[1]),(c[2], c[3]),(0,0,255),3)
                text = pytesseract.image_to_string(imagen[c[1]:c[3], c[0]:c[2]]).split('\n')
                text = organizar(text)

                f.write(text)

                if c != coords[-1]:
                    f.write(";")

            f.write("\n")
        f.close()

        self.manager.current = 'menu'

class MenuScreen(Screen):
    def sm_u(self, screen):
        self.manager.current = screen

class MainApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(PdfConvertScreen(name='pdf_convert'))
        sm.add_widget(NewFormatScreen(name='new_format'))
        sm.add_widget(ScrapScreen(name='scrap'))
        
        sm.current = 'scrap'

        return sm

if __name__ == '__main__':
    MainApp().run()