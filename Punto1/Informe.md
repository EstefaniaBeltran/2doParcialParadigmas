**Diseño de la solución**
 -Modelo matemático del perceptrón 


### Función de decisión

Dado un punto \( (x_1, x_2) \), el perceptrón calcula:

\[
y = 
\begin{cases}
1 & \text{si } w_1 \cdot x_1 + w_2 \cdot x_2 + b > 0 \\
0 & \text{en otro caso}
\end{cases}
\]

Donde:

- \( x_1, x_2 \): entradas (coordenadas del punto)
- \( w_1, w_2 \): pesos
- \( b \): bias (sesgo)
- \( y \): salida predicha (0 o 1)

---

###  Regla de aprendizaje

Durante el entrenamiento, los pesos y el bias se actualizan según el error de predicción:

\[
\text{error} = \hat{y} - y
\]

\[
w_1 \leftarrow w_1 + \eta \cdot \text{error} \cdot x_1
\]
\[
w_2 \leftarrow w_2 + \eta \cdot \text{error} \cdot x_2
\]
\[
b \leftarrow b + \eta \cdot \text{error}
\]

Donde:

- \( \hat{y} \): etiqueta real (target, 0 o 1)
- \( y \): predicción del perceptrón
- \( \eta \): tasa de aprendizaje

---

Este modelo fue implementado en la simulación.

