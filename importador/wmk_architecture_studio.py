"""WMK Architecture Studio: revisão visual de vetorização. Interface pt-BR."""
from __future__ import annotations

import copy
import json
import math
import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from PIL import Image, ImageTk
from wmk_detector_planta import carregar_imagem, detectar_linhas, exportar_dxf, salvar_previa

BASE = Path(__file__).resolve().parent
BRAND = BASE / 'assets' / 'logo-wmk-architecture-64.png'
OUTPUT_BASE = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else BASE


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('WMK Architecture Studio | Importador de plantas')
        self.geometry('1250x840')
        self.minsize(850, 600)
        self.configure(bg='#0c1728')
        self.origem: Path | None = None
        self.original: Image.Image | None = None
        self.resultado: dict | None = None
        self.mm_px: float | None = None
        self.modo = tk.StringVar(value='auto')
        self.status = tk.StringVar(value='Abra uma planta para começar. Resultado preliminar: confira cada linha.')
        self.resumo = tk.StringVar(value='Sem análise')
        self.calibrando: list[tuple[float,float]] | None = None
        self.adicionando: list[tuple[float,float]] | None = None
        self.out_dir = OUTPUT_BASE / 'projetos_gerados'
        self._zoom = 1.0
        self._off = (0.0, 0.0)
        self._image_ref = None
        self._style()
        self._widgets()
        if BRAND.exists():
            try:
                self.iconphoto(True, tk.PhotoImage(file=str(BRAND)))
            except tk.TclError:
                pass

    def _style(self):
        style = ttk.Style(self)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('Wmk.TFrame', background='#0c1728')
        style.configure('Wmk.TLabel', foreground='#e3f4fa', background='#0c1728', font=('Segoe UI', 10))
        style.configure('Title.TLabel', foreground='#1de0e6', background='#0c1728', font=('Segoe UI', 18, 'bold'))
        style.configure('Wmk.TButton', padding=(9, 6), font=('Segoe UI', 10))

    def _widgets(self):
        bar = ttk.Frame(self, style='Wmk.TFrame', padding=10)
        bar.pack(fill='x')
        ttk.Label(bar, text='WMK ARCHITECTURE STUDIO', style='Title.TLabel').pack(side='left')
        ttk.Label(bar, text='  |  CAD → BIM · revisão humana', style='Wmk.TLabel').pack(side='left')
        ttk.Button(bar, text='Abrir JPG / PNG / PDF', style='Wmk.TButton', command=self.abrir).pack(side='right')
        tools = ttk.Frame(self, style='Wmk.TFrame', padding=(10, 2, 10, 8))
        tools.pack(fill='x')
        ttk.Label(tools, text='Detecção:', style='Wmk.TLabel').pack(side='left')
        ttk.Combobox(tools, textvariable=self.modo, values=['auto','laranja','escuro'], width=10,
                     state='readonly').pack(side='left', padx=4)
        self.btn = ttk.Button(tools, text='1. Reconhecer linhas', command=self.reconhecer)
        self.btn.pack(side='left', padx=4)
        ttk.Button(tools, text='2. Calibrar escala', command=self.calibrar).pack(side='left', padx=4)
        ttk.Button(tools, text='Adicionar linha', command=self.adicionar).pack(side='left', padx=4)
        ttk.Button(tools, text='3. Salvar DXF revisado', command=self.salvar).pack(side='left', padx=4)
        ttk.Button(tools, text='Pasta de saída', command=self.abrir_pasta).pack(side='left', padx=4)
        self.cv = tk.Canvas(self, bg='#122738', bd=0, highlightthickness=0, cursor='crosshair')
        self.cv.pack(fill='both', expand=True, padx=10, pady=5)
        self.cv.bind('<Configure>', lambda _e: self.redesenhar())
        self.cv.bind('<Button-1>', self.clicar)
        foot = ttk.Frame(self, style='Wmk.TFrame', padding=(10, 3, 10, 8))
        foot.pack(fill='x')
        ttk.Label(foot, textvariable=self.resumo, style='Wmk.TLabel').pack(anchor='w')
        ttk.Label(foot, textvariable=self.status, style='Wmk.TLabel').pack(anchor='w')
        ttk.Label(foot, text='WMK — Walney Moreira Klein — walneyk@hotmail.com | Base: CADCraft / BIMCraft, com créditos preservados',
                  style='Wmk.TLabel').pack(anchor='w')

    def abrir(self):
        path = filedialog.askopenfilename(title='Escolha a planta', filetypes=[
            ('Plantas', '*.jpg *.jpeg *.png *.bmp *.pdf'), ('Todos', '*.*')])
        if not path:
            return
        try:
            import cv2
            a = carregar_imagem(path)
            self.original = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))
        except Exception as exc:
            messagebox.showerror('Falha na leitura', str(exc))
            return
        self.origem = Path(path)
        self.resultado = None
        self.mm_px = None
        self.status.set(f'Imagem aberta: {self.origem.name}. Clique em Reconhecer linhas.')
        self.resumo.set('Referência carregada; nada foi convertido ainda')
        self.redesenhar()

    def reconhecer(self):
        if self.original is None:
            messagebox.showwarning('Sem imagem', 'Abra uma planta primeiro.')
            return
        self.btn.configure(state='disabled')
        self.status.set('Analisando segmentos; nenhuma alteração na planta original...')
        from PIL import Image as PILImage
        image = self.original.copy()
        mode = self.modo.get()
        def task():
            try:
                import cv2
                import numpy as np
                bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                found = detectar_linhas(bgr, mode)
                self.after(0, lambda: self.concluido(found))
            except Exception as exc:
                self.after(0, lambda err=str(exc): self.falha(err))
        threading.Thread(target=task, daemon=True).start()

    def concluido(self, found):
        self.btn.configure(state='normal')
        self.resultado = found
        self.status.set('CLIQUE numa linha verde para excluir; clique na vermelha para recuperar. Salve somente após revisar.')
        self.atualizar_contagem()
        self.redesenhar()

    def falha(self, msg):
        self.btn.configure(state='normal')
        self.status.set('Falha: ' + msg)
        messagebox.showerror('Falha no reconhecimento', msg)

    def atualizar_contagem(self):
        if not self.resultado:
            return
        n = len(self.resultado['linhas'])
        act = sum(x.get('ativo', True) for x in self.resultado['linhas'])
        unit = f'{self.mm_px:.5f} mm/pixel' if self.mm_px else 'escala NÃO definida'
        self.resumo.set(f'{n} linhas detectadas | {act} selecionadas | {n-act} descartadas | {unit} | modo: {self.resultado["modo_usado"]}')

    def redesenhar(self):
        self.cv.delete('all')
        if self.original is None:
            return
        iw, ih = self.original.size
        cw, ch = max(2,self.cv.winfo_width()-12), max(2,self.cv.winfo_height()-12)
        z = min(cw/iw, ch/ih)
        ox, oy = (self.cv.winfo_width()-iw*z)/2, (self.cv.winfo_height()-ih*z)/2
        self._zoom, self._off = z, (ox,oy)
        show = self.original.resize((max(1,round(iw*z)), max(1,round(ih*z))), Image.Resampling.LANCZOS)
        self._image_ref = ImageTk.PhotoImage(show)
        self.cv.create_image(ox,oy,anchor='nw',image=self._image_ref)
        if self.resultado:
            for index, x in enumerate(self.resultado['linhas']):
                active=x.get('ativo', True)
                a,b=x['inicio_px'],x['fim_px']
                self.cv.create_line(ox+a[0]*z,oy+a[1]*z,ox+b[0]*z,oy+b[1]*z,
                    width=3 if active else 2, fill='#02ea70' if active else '#f55a59',
                    dash=() if active else (6,4),tags=f'seg{index}')
        for seq,color in [(self.calibrando,'#ffeb3b'),(self.adicionando,'#02e7fe')]:
            if seq:
                for p in seq:
                    x,y=ox+p[0]*z,oy+p[1]*z
                    self.cv.create_oval(x-5,y-5,x+5,y+5,outline=color,width=2)

    def _pt(self, event):
        if self.original is None:
            return None
        x=(event.x-self._off[0])/self._zoom
        y=(event.y-self._off[1])/self._zoom
        w,h=self.original.size
        return (x,y) if 0<=x<=w and 0<=y<=h else None

    def clicar(self, event):
        pt=self._pt(event)
        if pt is None:
            return
        if self.calibrando is not None:
            self.calibrando.append(pt)
            if len(self.calibrando)==2:
                points=self.calibrando
                self.calibrando=None
                length=math.dist(*points)
                if length<10:
                    messagebox.showerror('Escala', 'Escolha dois pontos mais afastados.')
                else:
                    metres=simpledialog.askfloat('Escala real', 'Distância real entre os pontos, em METROS:',minvalue=.001)
                    if metres is not None:
                        self.mm_px=metres*1000/length
                        self.status.set(f'Escala confirmada: {self.mm_px:.5f} mm/pixel. Confira outra medida conhecida.')
                        self.atualizar_contagem()
            self.redesenhar()
            return
        if self.adicionando is not None:
            self.adicionando.append(pt)
            if len(self.adicionando)==2:
                a,b=self.adicionando; self.adicionando=None
                if self.resultado is not None and math.dist(a,b)>3:
                    self.resultado['linhas'].append(dict(inicio_px=list(a),fim_px=list(b),orientacao='manual',
                        pontuacao_heuristica=0,conexoes=0,ativo=True,revisado=True))
                    self.atualizar_contagem()
            self.redesenhar()
            return
        if self.resultado is None:
            return
        def dist_seg(p,a,b):
            dx,dy=b[0]-a[0],b[1]-a[1]
            t=max(0,min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/max(dx*dx+dy*dy,1)))
            return math.dist(p,(a[0]+t*dx,a[1]+t*dy))
        lines=self.resultado['linhas']
        options=sorted(((dist_seg(pt,s['inicio_px'],s['fim_px']),i) for i,s in enumerate(lines)))
        if options and options[0][0] <= max(7,7/self._zoom):
            i=options[0][1]
            lines[i]['ativo']=not lines[i].get('ativo',True)
            lines[i]['revisado']=True
            self.atualizar_contagem();self.redesenhar()

    def calibrar(self):
        if self.original is None:
            messagebox.showinfo('Escala','Abra uma imagem primeiro.');return
        self.calibrando=[];self.adicionando=None
        self.status.set('Clique nos dois extremos de uma cota conhecida e digite a distância REAL em metros.')

    def adicionar(self):
        if self.resultado is None:
            messagebox.showinfo('Segmentos','Clique em Reconhecer primeiro.');return
        self.adicionando=[];self.calibrando=None
        self.status.set('Clique no início e no fim da linha que deseja acrescentar.')

    def salvar(self):
        if self.origem is None or self.resultado is None or self.original is None:
            messagebox.showwarning('Sem análise','Abra e analise uma planta primeiro.');return
        active=sum(int(s.get('ativo',True)) for s in self.resultado['linhas'])
        if not active:
            messagebox.showwarning('Nenhuma linha','Nenhuma linha selecionada para exportar.');return
        dest=self.out_dir/self.origem.stem
        dest.mkdir(parents=True,exist_ok=True)
        data=copy.deepcopy(self.resultado)
        data.update(origem=self.origem.name,mm_por_pixel=self.mm_px,
                    unidades='milimetros' if self.mm_px else 'indefinidas',
                    segmentos_aceitos=active,segmentos_descartados=len(data['linhas'])-active,
                    advertencia='Revisão gráfica manual não equivale a validação profissional.')
        base=dest/self.origem.stem
        try:
            exportar_dxf(data,base.with_suffix('.dxf'),self.mm_px,apenas_ativos=True)
            (base.with_suffix('.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
            import cv2, numpy as np
            cv= cv2.cvtColor(np.array(self.original),cv2.COLOR_RGB2BGR)
            salvar_previa(cv,data,dest/(self.origem.stem+'_previa.png'))
        except Exception as e:
            messagebox.showerror('Erro ao salvar',str(e));return
        self.status.set(f'Projeto salvo: {dest}')
        messagebox.showinfo('DXF revisado salvo', f'{active} linhas exportadas em DXF/JSON/PNG.\nPasta: {dest}\n'+
                            ('Escala verificada pelo usuário.' if self.mm_px else 'AVISO: escala em milímetros NÃO definida.'))

    def abrir_pasta(self):
        self.out_dir.mkdir(parents=True,exist_ok=True)
        if os.name=='nt':
            os.startfile(str(self.out_dir))
        else:
            messagebox.showinfo('Pasta',str(self.out_dir))


if __name__ == '__main__':
    App().mainloop()
