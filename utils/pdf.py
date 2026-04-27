from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Flowable

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self.report_name = kwargs.pop('report_name', 'DANFE')
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.desenhar_paginacao(total_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def desenhar_paginacao(self, total_pages):
        width, height = self._pagesize
        self.setFont("Times-Roman", 6)
        self.setFillColor(colors.black)

        texto = f"FOLHA {self._pageNumber}/{total_pages}"

        text_width = self.stringWidth(texto, "Times-Roman", 6)

        if self.report_name == 'DANFE':
            x = width/2 - text_width/2 + 7

            if self._pageNumber == 1:
                y = height - 166
            else:
                y = height - 97
        elif self.report_name == 'Orcamento':
            x = width/2 - text_width/2 + 270

            if self._pageNumber == 1:
                y = height-175
            else:
                y = height-20

        self.drawString(x, y, f"FOLHA {self._pageNumber}/{total_pages}")

class CheckBox(Flowable):
    def __init__(self, checked=False, size=9):
        Flowable.__init__(self)
        self.checked = checked
        self.size = size
        self.width = self.height = size

    def draw(self):
        self.canv.rect(0, 0, self.size, self.size)
        if self.checked:
            self.canv.line(2, 2, self.size-2, self.size-2)
            self.canv.line(2, self.size-2, self.size-2, 2)

class RadioButton(Flowable):
    def __init__(self, label, selected=False):
        Flowable.__init__(self)
        self.label = label
        self.selected = selected
        self.size = 10  # Tamanho do círculo

    def draw(self):
        c = self.canv
        y_offset = -11

        # Desenhar o círculo
        c.circle(self.size / 2, y_offset + self.size / 2, self.size / 2, stroke=1, fill=0)
        if self.selected:
            # Desenhar o ponto central se selecionado
            c.circle(self.size / 2, y_offset + self.size / 2, self.size / 4, stroke=0, fill=1)
        # Desenhar o rótulo
        c.drawString(self.size + 2, 10, self.label)