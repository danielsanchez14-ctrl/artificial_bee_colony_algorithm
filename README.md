# Algoritmo Artificial Bee Colony (ABC)

Implementación didáctica del algoritmo de optimización **Artificial Bee Colony (ABC)**. El proyecto incluye el algoritmo en un cuaderno de Jupyter y una interfaz gráfica para explorar las fases de su ejecución.

## Contenido

- [`implementacion.ipynb`](./implementacion.ipynb): define `ArtificialBeeColony` y contiene ejemplos de optimización con una, dos y cinco variables.
- [`abc_visualizer.py`](./abc_visualizer.py): visualiza el historial del algoritmo con tablas, gráficas de convergencia y controles para avanzar, retroceder, animar o reiniciar la ejecución.

## Requisitos

- Python 3.9 o posterior.
- JupyterLab e IPython para ejecutar el cuaderno.
- NumPy, pandas, Matplotlib y CustomTkinter para el algoritmo y la interfaz.
- Tkinter, incluido habitualmente con Python. En algunas distribuciones de Linux debe instalarse por separado (por ejemplo, el paquete `python3-tk`).

## Instalación y ejecución

Desde la raíz del repositorio, crea y activa un entorno virtual. En PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala las dependencias y abre JupyterLab:

```bash
python -m pip install jupyterlab ipykernel numpy pandas matplotlib customtkinter
jupyter lab
```

Abre `implementacion.ipynb`, selecciona el kernel del entorno virtual y ejecuta las celdas en orden (o usa **Run All**). Los ejemplos ejecutan el algoritmo y abren el visualizador; se necesita un entorno de escritorio con soporte para Tkinter para mostrar la ventana.

## Uso del algoritmo

`ArtificialBeeColony` recibe los siguientes parámetros:

| Parámetro | Descripción |
| --- | --- |
| `limit` | Número de intentos sin mejora que se permite a una solución antes de reemplazarla en la fase exploradora. |
| `sn` | Número de soluciones o fuentes de alimento de la población. Debe ser al menos 2. |
| `mcn` | Número máximo de ciclos del algoritmo. |
| `f` | Función objetivo de Python que se desea minimizar. |
| `seed` | Semilla para reproducir la inicialización y las decisiones aleatorias. |

`execute(restrictions)` recibe una lista de pares `(mínimo, máximo)`, uno por variable. El número de pares debe coincidir con el número de argumentos de la función objetivo. Devuelve una tupla con la mejor solución encontrada, su valor objetivo y el historial de las fases.

La clase se define en el cuaderno. Después de ejecutar la celda que la declara, un ejemplo de uso es:

```python
from abc_visualizer import show_abc

f = lambda x1, x2: x1**2 + x2**2
restrictions = [(-5.12, 5.12), (-5.12, 5.12)]

abc = ArtificialBeeColony(limit=2, sn=5, mcn=60, f=f, seed=42)
best_solution, best_value, history = abc.execute(restrictions)

print("Mejor solución:", best_solution)
print("Valor objetivo:", best_value)
show_abc(history, abc.f, restrictions)
```

La interfaz muestra el historial de inicialización y de las fases de abejas obreras, observadoras y exploradoras. Para funciones de dos o más variables, el mapa de contorno representa las dos primeras variables; si hay más, las restantes se mantienen fijas en los valores de la mejor solución mostrada.
