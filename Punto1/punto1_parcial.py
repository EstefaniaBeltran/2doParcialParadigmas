#Punto 1 Modelamiento de un Perceptrón

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
import numpy as np

# ------------------------------------------------------------
# AGENTE PERCEPTRÓN
# ------------------------------------------------------------

class PerceptronAgent(Agent):
    def __init__(self, unique_id, model, x1, x2, label, is_test=False):
        super().__init__(unique_id, model)
        self.x1 = x1
        self.x2 = x2
        self.label = label
        self.prediccion = 0
        self.grid_pos = None
        self.is_test = is_test

    def step(self):
        if self.model.iteracion_actual >= self.model.num_iteraciones:
            return

        suma = self.model.w1 * self.x1 + self.model.w2 * self.x2 + self.model.b
        self.prediccion = 1 if suma > 0 else 0

        if not self.is_test:
            error = self.label - self.prediccion
            self.model.w1 += self.model.lr * error * self.x1
            self.model.w2 += self.model.lr * error * self.x2
            self.model.b += self.model.lr * error

# ------------------------------------------------------------
# AGENTE LÍNEA DE DECISIÓN
# ------------------------------------------------------------

class LineaDecisionAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.grid_pos = pos

    def step(self):
        pass

# ------------------------------------------------------------
# MODELO DEL PERCEPTRÓN
# ------------------------------------------------------------

class PerceptronModel(Model):
    def __init__(self, N=50, lr=0.1, num_iteraciones=20):
        self.num_agents = N
        self.lr = lr
        self.num_iteraciones = num_iteraciones
        self.iteracion_actual = 0
        self.schedule = RandomActivation(self)

        self.grid_width = 20
        self.grid_height = 20
        self.grid = MultiGrid(self.grid_width, self.grid_height, True)

        self.w1 = np.random.uniform(-1, 1)
        self.w2 = np.random.uniform(-1, 1)
        self.b = np.random.uniform(-1, 1)

        self.training_agents = []

        for i in range(self.num_agents):
            x1 = np.random.uniform(-1, 1)
            x2 = np.random.uniform(-1, 1)
            label = 1 if x2 > 0.5 * x1 + 0.2 else 0

            a = PerceptronAgent(i, self, x1, x2, label)
            gx = int(((x1 + 1) / 2) * (self.grid_width - 1))
            gy = int(((x2 + 1) / 2) * (self.grid_height - 1))
            a.grid_pos = (gx, gy)

            self.grid.place_agent(a, (gx, gy))
            self.schedule.add(a)
            self.training_agents.append(a)

        self.datacollector = DataCollector(
            model_reporters={"Error_promedio": self.calcular_error_promedio}
        )

        self.dibujar_linea_decision()

    def step(self):
        if self.iteracion_actual < self.num_iteraciones:
            self.schedule.step()
            self.datacollector.collect(self)
            self.dibujar_linea_decision()
            self.iteracion_actual += 1
        elif self.iteracion_actual == self.num_iteraciones:
            self.evaluar_modelo()
            self.iteracion_actual += 1

    def calcular_error_promedio(self):
        errores = []
        for agent in self.training_agents:
            suma = self.w1 * agent.x1 + self.w2 * agent.x2 + self.b
            prediccion = 1 if suma > 0 else 0
            errores.append(abs(agent.label - prediccion))
        return np.mean(errores) if len(errores) > 0 else 0

    def evaluar_modelo(self):
        aciertos = 0
        total = 20

        for i in range(total):
            x1 = np.random.uniform(-1, 1)
            x2 = np.random.uniform(-1, 1)
            label = 1 if x2 > 0.5 * x1 + 0.2 else 0
            suma = self.w1 * x1 + self.w2 * x2 + self.b
            prediccion = 1 if suma > 0 else 0
            if prediccion == label:
                aciertos += 1

        porcentaje = (aciertos / total) * 100
        print(f"Evaluación final: {aciertos} de {total} puntos clasificados correctamente ({porcentaje:.2f}%)")

    def dibujar_linea_decision(self):
        # Eliminar líneas anteriores
        for agent in list(self.schedule.agents):
            if isinstance(agent, LineaDecisionAgent):
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)

        for x1 in np.linspace(-1, 1, 30):
            if self.w2 != 0:
                x2 = -(self.w1 / self.w2) * x1 - (self.b / self.w2)
                if -1 <= x2 <= 1:
                    gx = int(((x1 + 1) / 2) * (self.grid_width - 1))
                    gy = int(((x2 + 1) / 2) * (self.grid_height - 1))
                    line_agent = LineaDecisionAgent(f"line-{x1}", self, (gx, gy))
                    self.grid.place_agent(line_agent, (gx, gy))
                    self.schedule.add(line_agent)

# ------------------------------------------------------------
# VISUALIZACIÓN
# ------------------------------------------------------------

def agent_portrayal(agent):
    if isinstance(agent, LineaDecisionAgent):
        return {
            "Shape": "rect",
            "Color": "purple",
            "Filled": "true",
            "Layer": 0,
            "w": 0.9,
            "h": 0.05
        }

    color = "green" if agent.prediccion == agent.label else "red"
    return {
        "Shape": "circle",
        "Color": color,
        "Filled": "true",
        "Layer": 1,
        "r": 0.6,
    }

grid = CanvasGrid(agent_portrayal, 20, 20, 400, 400)

chart = ChartModule(
    [{"Label": "Error_promedio", "Color": "salmon"}],
    data_collector_name="datacollector"
)

model_params = {
    "N": UserSettableParameter("slider", "Número de puntos", 50, 10, 100, 10),
    "lr": UserSettableParameter("slider", "Tasa de aprendizaje", 0.1, 0.01, 1, 0.01),
    "num_iteraciones": UserSettableParameter("slider", "Número de iteraciones", 20, 5, 100, 5)
}

server = ModularServer(
    PerceptronModel,
    [grid, chart],
    "Punto 1 - Modelamiento de un Perceptrón",
    model_params
)

server.port = 8521

if __name__ == "__main__":
    server.launch()

