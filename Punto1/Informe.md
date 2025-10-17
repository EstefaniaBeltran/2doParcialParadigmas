**Diseño de la solución**
 -Modelo matemático del perceptrón 

¡Perfecto! Aquí tienes el contenido listo en formato `.md` para que solo lo **copies y pegues** en tu archivo `README.md`. Abajo te explico **cómo y cuándo tomar las capturas** correctamente para cumplir con el entregable.

---

## ✅ Contenido completo para `README.md` (solo copiar y pegar)

````markdown
# 🧠 Simulación de Perceptrón con Agentes en MESA

---

## 🎯 Objetivo

Simular el entrenamiento de un **perceptrón simple** utilizando el paradigma de **agentes** en Python, mediante el framework **MESA**, para clasificar puntos 2D linealmente separables.

---

## 🧠 ¿Qué es un Perceptrón?

El perceptrón es un modelo matemático de neurona artificial propuesto por Frank Rosenblatt en 1958. Es una técnica de clasificación supervisada que determina a qué clase pertenece un punto basándose en una **función lineal**.

Funciona ajustando automáticamente los pesos y el sesgo de una línea de decisión en función del error cometido al clasificar los datos de entrenamiento.

---

## 🛠️ Implementación con MESA

### 🔸 Paradigma: Programación Basada en Agentes (ABM)

- Cada **agente** representa un punto en el plano 2D.
- El **modelo global** contiene los pesos del perceptrón y entrena a través de iteraciones (steps).
- Los agentes no se mueven; su estado cambia si están bien o mal clasificados.

### 🔸 Entradas:

- Coordenadas 2D aleatorias: \( x_1, x_2 \)
- Etiquetas asignadas según una línea real:  
  `label = 1 if x2 > 0.5 * x1 + 0.2 else 0`

### 🔸 Entrenamiento:

- En cada step, los agentes calculan su salida con la fórmula del perceptrón.
- Si hay error, se actualizan los pesos globales según la regla de aprendizaje.

---

## 🧮 Modelo Matemático

El perceptrón simple calcula la salida:

```latex
$$
y = 
\begin{cases}
1 & \text{si } w_1 x_1 + w_2 x_2 + b > 0 \\
0 & \text{en otro caso}
\end{cases}
$$
````

Regla de actualización:

```latex
$$
\text{error} = \hat{y} - y
$$

$$
w_1 \leftarrow w_1 + \eta \cdot \text{error} \cdot x_1
$$

$$
w_2 \leftarrow w_2 + \eta \cdot \text{error} \cdot x_2
$$

$$
b \leftarrow b + \eta \cdot \text{error}
$$
```

---

## 📊 Visualización

* **Puntos en pantalla**:

  * Verdes: bien clasificados
  * Naranjas: mal clasificados
* **Gráfico de error**: muestra la evolución del error promedio por step
* **Frontera de decisión**: se actualiza visualmente durante el entrenamiento

---

## 📷 Capturas de pantalla

### 🖼️ Entrenamiento del Perceptrón

> Muestra la pantalla **cuando la simulación lleva unos 10 a 30 pasos** y todavía hay varios puntos mal clasificados (de color naranja). El gráfico de error aún no ha llegado a 0.

![Entrenamiento en curso](capturas/entrenamiento.png)

---

### ✅ Clasificación final

> Muestra la pantalla cuando el error promedio llegó a 0 o muy cerca, y **todos los puntos están verdes**. Idealmente, después de 30-100 steps.

![Clasificación final](capturas/final.png)

---

## 📈 Resultados

* El perceptrón logró reducir el error promedio a cerca de 0 después de varias iteraciones.
* La línea de decisión aprendida logró separar correctamente los puntos, validando que los datos eran linealmente separables.
* La visualización permitió observar el proceso de aprendizaje paso a paso.

---

## ✅ Conclusión

El modelo implementado demuestra cómo un perceptrón simple puede aprender a clasificar datos de forma efectiva. Además, la simulación basada en agentes permite visualizar el aprendizaje de manera dinámica e interactiva, facilitando la comprensión del funcionamiento interno del algoritmo.
