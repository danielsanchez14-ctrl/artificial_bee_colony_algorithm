import tkinter as tk
from tkinter import ttk # Para widgets temáticos

import numpy as np
import pandas as pd
import customtkinter as ctk
from matplotlib.figure import Figure # Objeto que representa la figura de Matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Para conectar la figura a Tkinter

ANIMATION_MS = 700  # Pausa entre ciclos de la animación (ms)

# Claves del diccionario history del algoritmo
PHASES = [ # Tuplas (clave, título a mostrar)
    ("inicializacion", "Inicialización"),
    ("candidatas_fase_obreras", "Obreras: candidatas"),
    ("reemplazadas_fase_obreras", "Obreras: reemplazos"),
    ("fase_abejas_observadoras", "Observadoras"),
    ("fase_abejas_observadoras_resumen", "Observadoras: resumen"),
    ("fase_abejas_exploradoras", "Exploradoras"),
]

VALUE_COL = "Valor en función objetivo"

def build_data(history: dict):
    """
        Prepara el historial del algoritmo para 
        que la interfaz pueda mostrar cada fase por ciclo 
        y seguir la mejor solución encontrada hasta el momento.
    """
    # Separamos cada fase por ciclo de iteración del algoritmo
    # Ejemplo: tables["candidatas_fase_obreras"][1] devuelve los datos de solo el ciclo 1
    tables = {
        key: (
            pd.DataFrame(history[key])
            if key == "inicializacion"
            else dict(list(pd.DataFrame(history[key]).groupby("Ciclo")))
        )
        for key, _ in PHASES
    }

    """
        best_values guardará el mejor valor objetivo conocido al terminar cada ciclo.
        best_vectors guardará el vector de componentes que produjo ese valor.
        best_cycles guardará el ciclo en el que se encontró ese mejor resultado.
        best_value empieza como None porque todavía no se ha procesado ningún ciclo.
    """
    best_values, best_vectors, best_cycles = [], [], []
    summary = pd.DataFrame(history["fase_abejas_observadoras_resumen"])

    # El mejor global empieza en la población inicial (ciclo 0)
    init = pd.DataFrame(history["inicializacion"])
    row = init.loc[init[VALUE_COL].idxmin()]
    best_value, best_vector, best_cycle = row[VALUE_COL], row["Componentes"], 0

    # Separamos las filas por ciclo
    for cycle, rows in summary.groupby("Ciclo"): # Agrupa las filas por el valor ciclo

        # Fila con menor valor del grupo
        row = rows.loc[rows[VALUE_COL].idxmin()]

        if best_value is None or row[VALUE_COL] < best_value:
            best_value, best_vector, best_cycle = row[VALUE_COL], row["Componentes"], cycle

        # Las listas acumulan el historial de evolución de las mejores soluciones por ciclo
        best_values.append(best_value)
        best_vectors.append(best_vector)
        best_cycles.append(best_cycle)

    return tables, best_values, best_vectors, best_cycles


def fmt(x):
    """
        Convierte un valor en texto legible para mostrarlo en una celda de la tabla. 
        Revisa el tipo de x y aplica una regla distinta
    """
    if isinstance(x, (list, tuple, np.ndarray)):
        return "[" + ", ".join(f"{v:.3f}" for v in x) + "]"
    if isinstance(x, (bool, np.bool_)):
        return "Sí" if x else "No"
    if isinstance(x, (float, np.floating)):
        return "—" if np.isnan(x) else f"{x:.4f}"
    return str(x)

def draw_plots(fig, f, restrictions, population, best, cycle, best_values):

    """
        fig: la figura de Matplotlib donde se dibujarán las gráficas.
        f: la función objetivo que se está minimizando.
        restrictions: los límites (mínimo, máximo) de cada variable.
        population (matriz): las soluciones actuales; cada fila representa una solución y cada columna, una variable.
        best: el vector de componentes de la mejor solución encontrada hasta ahora.
        cycle: el ciclo que se está mostrando.
        best_values: la lista de mejores valores acumulados, uno por ciclo.
    """

    fig.clf() #  borra las gráficas anteriores para no dibujarlas encima.
    ax1, ax2 = fig.subplots(1, 2) # Crea dos áreas de dibujo

    # La forma de la primera gráfica depende de cuántas variables tenga la solución:
    if len(best) == 1:
        # Crea 300 valores de x repartidos entre el límite mínimo y máximo de la primera variable.
        xs = np.linspace(*restrictions[0], 300)
        # Calcula f(x) para cada uno de esos valores y dibuja la curva de la función.
        ax1.plot(xs, [f(x) for x in xs], color="gray", label="f(x)")
        # Dibuja los miembros de la población actual sobre la curva.
        ax1.scatter(population[:, 0], [f(x) for x in population[:, 0]], c="tab:blue",
                    label="Soluciones", zorder=3)
        # Marca la mejor solución actual con una estrella roja: su posición es best[0] y su altura es f(best[0]).
        ax1.scatter(best[0], f(best[0]),  marker="*", s=250, c="red", edgecolors="black",
                    label="Mejor hasta ahora", zorder=4)

        # Etiquetas de ejes y título con el número de ciclo
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.set_title(f"Función objetivo, ciclo {cycle}", fontsize=10)
    else:
        # Si hay dos o más variables, el código muestra un mapa de contornos de las dos primeras variables
        # Crea una cuadrícula de 40 valores para la primera variable y 40 para la segunda. 
        # Z almacenará el valor de la función objetivo en cada punto de esa cuadrícula.
        xs = np.linspace(*restrictions[0], 40)
        ys = np.linspace(*restrictions[1], 40)
        Z = np.zeros((40, 40))

        # Para cada combinación de x e y
        for r, y in enumerate(ys):
            for c, x in enumerate(xs):
                point = np.array(best, dtype=float)
                point[0], point[1] = x, y
                Z[r, c] = f(*point)

        """
            Si hay más de dos variables, las restantes se mantienen 
            fijas en los valores de best. Por eso la gráfica es una sección de la función: 
            solo muestra cómo cambia al variar las dos primeras variables.
        """
        # Dibuja el mapa de colores. Cada color representa un valor distinto de la función; 
        # la barra lateral indica qué valor corresponde a cada color.
        contour = ax1.contourf(xs, ys, Z, levels=25, cmap="viridis")
        fig.colorbar(contour, ax=ax1, label="f(x)")

        # Colocamos la mejor solución y la población en ese mapa
        ax1.scatter(population[:, 0], population[:, 1], c="white", edgecolors="black", label="Soluciones")
        ax1.scatter(best[0], best[1], marker="*", s=250, c="red", edgecolors="black",
                    label="Mejor hasta ahora")

        # Etiquetas y leyendas
        ax1.set_xlabel("x1")
        ax1.set_ylabel("x2")
        title = f"Función objetivo, ciclo {cycle}"
        if len(best) > 2:
            title += "\nSección de x1-x2. Las demás variables se fijan en sus valores de la mejor solución. Los puntos son proyecciones"
        ax1.set_title(title, fontsize=10)

    # Ubicación de la leyenda
    ax1.legend(fontsize=8, loc="upper right")

    # Gráfica 2: evolución de la mejor solución a lo largo de todo el algoritmo (convergencia)
    ax2.plot(range(1, len(best_values) + 1), best_values, color="tab:blue",
             label="Mejor valor hasta ahora")
    ax2.scatter([cycle], [best_values[cycle - 1]], c="red", zorder=3, label="Ciclo seleccionado")
    ax2.set_xlabel("Ciclo")
    ax2.set_ylabel("Mejor valor de función objetivo hasta ahora")
    ax2.set_title("Convergencia", fontsize=10)
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

# Ventana gráfica
class ABCWindow(ctk.CTk):
    """
        Al heredar de ctk.CTk, ABCWindow obtiene el comportamiento 
        básico de una ventana: puede mostrarse, cerrarse y contener controles gráficos. 
        Además, puede agregar sus propios datos y funciones, 
        por ejemplo, botones, gráficos o métodos para ejecutar el algoritmo ABC.
    """
    def __init__(self, history, f, restrictions):
        super().__init__()
        self.f = f
        self.restrictions = restrictions
        self.tables, self.best_values, self.best_vectors, self.best_cycles = build_data(history)
        self.n_cycles = len(self.best_values)
        self.cycle = 1
        self.playing = False
        self.after_id = None



# Ventana gráfica
class ABCWindow(ctk.CTk):
    def __init__(self, history, f, restrictions):
        """
        Inicializa la ventana y prepara los datos que se mostrarán.

        Guarda la función objetivo y sus restricciones, organiza el historial
        por ciclo y establece el estado inicial de la navegación y la animación.
        Después configura la ventana, crea sus controles y muestra el primer ciclo.
        """
        super().__init__()
        self.f = f
        self.restrictions = restrictions
        self.tables, self.best_values, self.best_vectors, self.best_cycles = build_data(history)
        self.n_cycles = len(self.best_values)
        self.cycle = 1
        self.playing = False
        self.after_id = None

        self.title("Colonia Artificial de Abejas")
        self.geometry("1400x850")
        try:
            self.state("zoomed")  # maximizar ventana
        except tk.TclError:
            pass
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.build_widgets()
        self.update_view()

    # Contrucción de Widgets
    def build_widgets(self):
        """
        Crea y organiza los controles, las gráficas y las tablas de la ventana.

        Conecta los botones y el deslizador con los métodos de navegación y
        animación, y crea una pestaña con su tabla para cada fase del algoritmo.
        """
        # Fila 0: controles
        bar = ctk.CTkFrame(self)
        bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 2))
        # Botones
        self.btn_prev = ctk.CTkButton(bar, text="Anterior", width=100, command=lambda: self.go_to(self.cycle - 1))
        self.btn_next = ctk.CTkButton(bar, text="Siguiente", width=100, command=lambda: self.go_to(self.cycle + 1))
        self.btn_play = ctk.CTkButton(bar, text="Ejecutar animación", width=160, command=self.play)
        self.btn_pause = ctk.CTkButton(bar, text="Pausar", width=100, command=self.pause)
        self.btn_reset = ctk.CTkButton(bar, text="Reiniciar", width=100, command=self.reset)
        # Slider
        self.slider = ctk.CTkSlider(bar, from_=1, to=max(self.n_cycles, 2), width=300,
                                    number_of_steps=max(self.n_cycles - 1, 1),
                                    command=lambda v: self.go_to(int(round(v))))
        self.lbl_cycle = ctk.CTkLabel(bar, text="", font=ctk.CTkFont(size=16, weight="bold"))
        for w in (self.btn_prev, self.btn_next, self.btn_play, self.btn_pause, self.btn_reset):
            w.pack(side="left", padx=4, pady=6)
        self.slider.pack(side="left", padx=12)
        self.lbl_cycle.pack(side="left", padx=8)

        # Fila 1: mejor solución hasta ahora
        self.lbl_best = ctk.CTkLabel(self, text="", anchor="w", font=ctk.CTkFont(size=14))
        self.lbl_best.grid(row=1, column=0, sticky="ew", padx=12, pady=2)

        # Fila 2: gráficas, se actulizan en la animación
        self.fig = Figure(figsize=(10, 4), constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew", padx=8, pady=2)

        # Fila 3: one pestaña por fase, cada una con una tabla (ttk.Treeview)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=24, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                        background="#2c3e50", foreground="white")
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=3, column=0, sticky="nsew", padx=8, pady=(2, 8))
        self.trees = {}
        for key, title in PHASES:
            tab = self.tabview.add(title)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)
            phase_data = self.tables[key]
            columns = list(
                phase_data.columns
                if key == "inicializacion"
                else next(iter(phase_data.values())).columns
            )
            tree = ttk.Treeview(tab, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
            yscroll = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
            xscroll = ttk.Scrollbar(tab, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
            tree.grid(row=0, column=0, sticky="nsew")
            yscroll.grid(row=0, column=1, sticky="ns")
            xscroll.grid(row=1, column=0, sticky="ew")
            self.trees[key] = tree

        # Más altura en gráficas que en tablas
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=3)
        self.grid_rowconfigure(3, weight=2)

    # Refrescar la vista dado el ciclo elegido
    def update_view(self):
        """
        Actualiza toda la interfaz para mostrar el ciclo seleccionado.

        Refresca el indicador del ciclo, el estado de los controles, la mejor
        solución, las tablas y las gráficas usando los datos ya guardados.
        No vuelve a ejecutar el algoritmo.
        """
        c = self.cycle
        self.lbl_cycle.configure(text=f"Ciclo {c} de {self.n_cycles}")
        self.slider.set(c)
        self.btn_prev.configure(state="normal" if c > 1 else "disabled")
        self.btn_next.configure(state="normal" if c < self.n_cycles else "disabled")
        self.btn_play.configure(state="disabled" if self.playing else "normal")
        self.btn_pause.configure(state="normal" if self.playing else "disabled")

        best = np.array(self.best_vectors[c - 1], dtype=float)
        found = "Inicialización" if self.best_cycles[c - 1] == 0 else self.best_cycles[c - 1]
        self.lbl_best.configure(
            text=f"Mejor solución global hasta ahora: {fmt(best)}   |   "
                 f"Valor: {self.best_values[c - 1]:.6f}   |   "
                 f"Encontrada en el ciclo: {found}")

        for key, tree in self.trees.items():
            phase_data = self.tables[key]
            df = phase_data if key == "inicializacion" else phase_data[c]
            ABCWindow.fill_table(tree, df)

        population = np.array(list(self.tables["fase_abejas_exploradoras"][c]["Componentes"]), dtype=float)
        draw_plots(self.fig, self.f, self.restrictions, population, best, c, self.best_values)
        self.canvas.draw_idle()

    @staticmethod
    def fill_table(tree, df):
        """
        Reemplaza el contenido de una tabla visual por las filas de un DataFrame.

        Formatea cada valor para mostrarlo como texto, inserta las filas en el
        Treeview y ajusta el ancho de las columnas según el contenido.
        """
        tree.delete(*tree.get_children())
        rows = [[fmt(v) for v in row] for row in df.itertuples(index=False)]
        for row in rows:
            tree.insert("", "end", values=row)

        for i, col in enumerate(df.columns):
            longest = max([len(str(col))] + [len(row[i]) for row in rows])
            tree.column(col, width=min(max(70, longest * 9), 450), anchor="center")

    # Navegación
    def go_to(self, cycle):
        """
        Cambia al ciclo solicitado, limitándolo al rango disponible.

        Si el ciclo cambia, guarda el nuevo número y actualiza la interfaz.
        """
        cycle = min(max(cycle, 1), self.n_cycles)
        if cycle != self.cycle:
            self.cycle = cycle
            self.update_view()

    def reset(self):
        """
        Detiene la animación y vuelve a mostrar el primer ciclo.

        La pausa cancela cualquier avance que ya estuviera programado antes
        de cambiar la selección al ciclo inicial.
        """
        self.pause()
        self.go_to(1)

    def play(self):
        """
        Inicia o reanuda el recorrido automático de los ciclos.

        Si la selección está en el último ciclo, vuelve primero al inicial.
        Luego marca la animación como activa y programa el primer avance para
        más tarde, dejando que el bucle de eventos de Tkinter siga atendiendo
        la ventana mientras transcurre la espera.
        """
        if self.cycle >= self.n_cycles:
            self.go_to(1)
        self.playing = True
        self.update_view()
        self.after_id = self.after(ANIMATION_MS, self.tick)

    def pause(self):
        """
        Detiene el recorrido automático y actualiza el estado de la interfaz.

        Cancela el siguiente avance programado, si existe, para que no se
        ejecute otro paso después de pausar.
        """
        self.playing = False
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.update_view()

    def tick(self):
        """
        Ejecuta un paso de la animación y programa el siguiente.

        Avanza un ciclo si aún quedan ciclos por mostrar. Al llegar al último,
        detiene la animación; de lo contrario, programa otra llamada a este
        método después del intervalo establecido.
        """
        if self.cycle >= self.n_cycles:
            self.pause()
            return
        self.go_to(self.cycle + 1)
        self.after_id = self.after(ANIMATION_MS, self.tick)

    def on_close(self):
        """
        Detiene cualquier avance pendiente y cierra la ventana.

        Este método se llama cuando el usuario solicita cerrar la ventana.
        """
        self.pause_quietly()
        self.destroy()

    def pause_quietly(self):
        """
        Detiene la animación al cerrar la ventana sin refrescar sus controles.

        Marca la animación como inactiva y cancela el siguiente paso, si había
        uno programado. Se usa durante el cierre, cuando ya no hace falta
        redibujar la interfaz.
        """
        self.playing = False
        if self.after_id is not None:
            self.after_cancel(self.after_id)

# Función principal
def show_abc(history, f, restrictions):
    ctk.set_appearance_mode("light")
    ABCWindow(history, f, restrictions).mainloop()