#Punto 2: Calculadora con mesa

import ast
import uuid
import math
from collections import defaultdict
from typing import Any, Dict
from mesa import Agent, Model
from mesa.time import BaseScheduler


# Modelo
class CalcModel(Model):
    def __init__(self, max_steps: int = 10000):
        super().__init__()
        self.schedule = BaseScheduler(self)
        self.message_queues = defaultdict(list) 
        self.running = True
        self.step_count = 0
        self.max_steps = max_steps

    def step(self):
        """Avanzar un tick: ejecutar step() de todos los agentes."""
        self.schedule.step()
        self.step_count += 1
        if self.step_count >= self.max_steps:
            self.running = False


# Agente de operaciones genérico

class OpAgent(Agent):
    """
    Agente que ejecuta una operación binaria (o en algunos casos unaria).
    Se procesa **un** mensaje compute por paso para ralentizar/sincronizar.
    """
    def __init__(self, unique_id: str, model: CalcModel, op_name: str):
        super().__init__(unique_id, model)
        self.op_name = op_name

    def step(self):
        q = self.model.message_queues[self.unique_id]
        if not q:
            return
        # Procesar sólo el primer mensaje en cola por paso (control de ritmo)
        msg = q.pop(0)
        try:
            if msg['type'] == 'compute':
                a = msg['payload']['a']
                b = msg['payload'].get('b', None)  # b puede ser None en ops unarias
                result = self._compute(a, b)
                resp = {
                    'from': self.unique_id,
                    'to': msg['from'],
                    'type': 'result',
                    'request_id': msg['request_id'],
                    'payload': {'result': result}
                }
                # enviar respuesta
                self.model.message_queues[msg['from']].append(resp)
            else:
                # otros tipos no gestionados
                err = {
                    'from': self.unique_id,
                    'to': msg['from'],
                    'type': 'error',
                    'request_id': msg.get('request_id', str(uuid.uuid4())),
                    'payload': {'error': f'Unsupported message type {msg["type"]}'}
                }
                self.model.message_queues[msg['from']].append(err)
        except Exception as e:
            err = {
                'from': self.unique_id,
                'to': msg['from'],
                'type': 'error',
                'request_id': msg.get('request_id', str(uuid.uuid4())),
                'payload': {'error': str(e)}
            }
            self.model.message_queues[msg['from']].append(err)

    def _compute(self, a: Any, b: Any):
        # soportar ints y floats; lanzar error si b es None cuando se necesita
        if self.op_name == 'add':
            return a + b
        if self.op_name == 'sub':
            return a - b
        if self.op_name == 'mul':
            return a * b
        if self.op_name == 'div':
            if b == 0:
                raise ZeroDivisionError("Division por cero")
            return a / b
        if self.op_name == 'pow':
            # usar math.pow cuando ambos son floats/ints (mantener compatibilidad)
            return a ** b
        raise NotImplementedError(f'Operación {self.op_name} no implementada')

# -----------------------------
# Agente IO (entrada/salida y orquestador ligero)
# -----------------------------
class IOAgent(Agent):
    """
    IOAgent parsea la expresión con ast, crea requests para sub-nodos y
    correlaciona responses. No bloquea la ejecución; en su lugar avanza el modelo
    hasta recibir el resultado final o agotar un límite de pasos.
    """
    def __init__(self, unique_id: str, model: CalcModel, operator_map: Dict[str, str]):
        super().__init__(unique_id, model)
        # operator_map: claves 'add','sub','mul','div','pow' -> agent_id
        self.operator_map = operator_map
        # waiting: request_id -> {'status': 'pending'|'done', 'result' or 'error'}
        self.waiting: Dict[str, Dict[str, Any]] = {}
        # opcional: logging interno para depuración
        self.trace = []

    def step(self):
        """Procesa mensajes entrantes (resultados/errores) cada tick."""
        q = self.model.message_queues[self.unique_id]
        while q:
            msg = q.pop(0)
            rid = msg.get('request_id', None)
            if msg['type'] == 'result':
                self.waiting[rid] = {'status': 'done', 'result': msg['payload']['result']}
                self.trace.append((self.model.step_count, f"Resultado {rid} = {msg['payload']['result']} (from {msg['from']})"))
            elif msg['type'] == 'error':
                self.waiting[rid] = {'status': 'done', 'error': msg['payload']['error']}
                self.trace.append((self.model.step_count, f"Error {rid} <- {msg['payload']['error']} (from {msg['from']})"))
            else:
                # info u otros tipos: simplemente registrar
                self.trace.append((self.model.step_count, f"Info msg type {msg['type']} recibida"))

    # -----------------------------
    # API pública para evaluar expresiones
    # -----------------------------
    def evaluate_expression(self, expression: str, step_timeout: int = 1000) -> float:
        """
        Inicia la evaluación de una expresión (string).
        Devuelve el resultado numérico o lanza excepción.
        step_timeout: máximo ticks del modelo para esperar resultado.
        """
        # limpiar estado previo
        self.waiting.clear()
        self.trace.clear()
        final_req = str(uuid.uuid4())

        # parseo seguro con ast (modo eval -> sólo expresiones)
        try:
            tree = ast.parse(expression, mode='eval')
        except Exception as e:
            raise ValueError(f"Expresión inválida: {e}")

        # dispatch recursivo: cada nodo crea request_id para su resultado
        self._dispatch_node(tree.body, final_req)

        # avanzar ticks hasta tener el resultado final o agotamiento
        ticks_waited = 0
        while True:
            # revisar si final_req está resuelto
            if final_req in self.waiting and self.waiting[final_req]['status'] == 'done':
                entry = self.waiting[final_req]
                if 'result' in entry:
                    return entry['result']
                else:
                    raise Exception(entry.get('error', 'Error desconocido'))
            # avanzar una iteración del modelo
            if not self.model.running:
                raise RuntimeError("El modelo dejó de ejecutarse antes de completar la evaluación.")
            self.model.step()
            ticks_waited += 1
            if ticks_waited > step_timeout:
                raise TimeoutError(f"Timeout: no se obtuvo resultado después de {step_timeout} ticks.")

    # -----------------------------
    # Dispatch y lógica AST
    # -----------------------------
    def _dispatch_node(self, node: ast.AST, request_id: str):
        """
        Para un nodo AST, asegura que se genere un request cuyo resultado
        será almacenado en self.waiting[request_id] cuando esté disponible.
        """
        # Nodos literales (constantes numéricas)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            # marcar como resuelto inmediatamente
            self.waiting[request_id] = {'status': 'done', 'result': float(node.value)}
            return

        # Nodos numéricos con compatibilidad para versiones antiguas (Num)
        if isinstance(node, ast.Num):
            self.waiting[request_id] = {'status': 'done', 'result': float(node.n)}
            return

        # Unary operations (+, -)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            sub_req = str(uuid.uuid4())
            self._dispatch_node(node.operand, sub_req)
            
            while not (sub_req in self.waiting and self.waiting[sub_req]['status'] == 'done'):
                self.model.step()
            if 'error' in self.waiting[sub_req]:
                self.waiting[request_id] = {'status': 'done', 'error': self.waiting[sub_req]['error']}
            else:
                val = self.waiting[sub_req]['result']
                if isinstance(node.op, ast.USub):
                    val = -val
                self.waiting[request_id] = {'status': 'done', 'result': val}
            return

        # Binary operations
        if isinstance(node, ast.BinOp):
            # Mapear operador AST a agente
            opkey = None
            if isinstance(node.op, ast.Add):
                opkey = 'add'
            elif isinstance(node.op, ast.Sub):
                opkey = 'sub'
            elif isinstance(node.op, ast.Mult):
                opkey = 'mul'
            elif isinstance(node.op, ast.Div):
                opkey = 'div'
            elif isinstance(node.op, ast.Pow):
                opkey = 'pow'
            else:
                raise NotImplementedError(f"Operador {type(node.op)} no soportado")

            op_agent_id = self.operator_map[opkey]

            # Crear request ids para operandos
            left_req = str(uuid.uuid4())
            right_req = str(uuid.uuid4())
            # Dispatch recursivo para subnodos
            self._dispatch_node(node.left, left_req)
            self._dispatch_node(node.right, right_req)

            # Esperar operandos (no bloqueante respecto al scheduler principal)
            while not (left_req in self.waiting and self.waiting[left_req]['status'] == 'done'):
                self.model.step()
            while not (right_req in self.waiting and self.waiting[right_req]['status'] == 'done'):
                self.model.step()

            # Recolectar errores/valores
            if 'error' in self.waiting[left_req]:
                self.waiting[request_id] = {'status': 'done', 'error': self.waiting[left_req]['error']}
                return
            if 'error' in self.waiting[right_req]:
                self.waiting[request_id] = {'status': 'done', 'error': self.waiting[right_req]['error']}
                return

            a = self.waiting[left_req]['result']
            b = self.waiting[right_req]['result']

            # Enviar mensaje compute al agente de operación; el resultado llegará
            # posteriormente con el mismo request_id
            msg = {
                'from': self.unique_id,
                'to': op_agent_id,
                'type': 'compute',
                'request_id': request_id,
                'payload': {'a': a, 'b': b}
            }
            self.model.message_queues[op_agent_id].append(msg)
            # NOTA: no marcamos request_id como pendiente aquí; lo hará cuando el op_agent responda.
            return

        # Soporte para paréntesis y llamadas a funciones simples (opcional)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            # Ejemplo: permitir funciones matemáticas básicas como sin(), cos(), log()
            func_name = node.func.id
            # Evaluar argumentos (soportamos sólo 1 arg por simplicidad)
            if len(node.args) != 1:
                raise NotImplementedError("Funciones con !=1 argumento no soportadas en este ejemplo")
            arg_req = str(uuid.uuid4())
            self._dispatch_node(node.args[0], arg_req)
            while not (arg_req in self.waiting and self.waiting[arg_req]['status'] == 'done'):
                self.model.step()
            if 'error' in self.waiting[arg_req]:
                self.waiting[request_id] = {'status': 'done', 'error': self.waiting[arg_req]['error']}
                return
            val = self.waiting[arg_req]['result']
            # mapear funciones a math
            if func_name == 'sin':
                res = math.sin(val)
            elif func_name == 'cos':
                res = math.cos(val)
            elif func_name == 'tan':
                res = math.tan(val)
            elif func_name == 'log':
                res = math.log(val)
            elif func_name == 'sqrt':
                res = math.sqrt(val)
            else:
                raise NotImplementedError(f"Función {func_name} no implementada")
            self.waiting[request_id] = {'status': 'done', 'result': res}
            return

        # Si llegamos aquí, tipo de nodo no soportado
        raise NotImplementedError(f"Tipo de nodo AST no soportado: {type(node)}")


# Construcción del modelo y agentes

def build_calculator_model(max_steps: int = 10000) -> CalcModel:
    model = CalcModel(max_steps=max_steps)

    # Crear agentes de operación
    add_agent = OpAgent('add_agent', model, 'add')
    sub_agent = OpAgent('sub_agent', model, 'sub')
    mul_agent = OpAgent('mul_agent', model, 'mul')
    div_agent = OpAgent('div_agent', model, 'div')
    pow_agent = OpAgent('pow_agent', model, 'pow')

    # Registrar agentes en scheduler (orden no crítico)
    model.schedule.add(add_agent)
    model.schedule.add(sub_agent)
    model.schedule.add(mul_agent)
    model.schedule.add(div_agent)
    model.schedule.add(pow_agent)

    # Mapear operadores a agentes
    op_map = {
        'add': 'add_agent',
        'sub': 'sub_agent',
        'mul': 'mul_agent',
        'div': 'div_agent',
        'pow': 'pow_agent'
    }

    # Crear IOAgent y añadir al scheduler (preferible primero para iniciar)
    io_agent = IOAgent('io_agent', model, operator_map=op_map)
    model.schedule.add(io_agent)

    # Guardar referencias útiles
    model.io_agent = io_agent
    model.op_agents = {
        'add': add_agent, 'sub': sub_agent, 'mul': mul_agent, 'div': div_agent, 'pow': pow_agent
    }

    return model


# Ejecución de ejemplo (main)

if __name__ == '__main__':
    # Construir modelo
    model = build_calculator_model(max_steps=10000)

    # Expresiones de prueba
    expressions = [
        "5 + 9 * 4 - 5",                      # precedencia: 9*4 primero
        "2 + 3 * 4 - 11 ** 4 / (3 + 1)",      # mezcla + - * / ** y paréntesis
        "-(3 + 4) * 2",                      # unary minus + paren
        "sin(5.32/2) + 5",           # funciones (sin) + constantes
        "10 / (12 - 12)",                      # dividir por cero -> error
        "2 ** 7 ** 2"                        # potencia derecha a izquierda: 7**2=49 then 2**49
    ]
    

    for expr in expressions:
        print("\n--------------------------------------------------------------------------------------------")
        print("Evaluando:", expr)
        try:
            result = model.io_agent.evaluate_expression(expr, step_timeout=2000)
            print("Resultado:", result)
        except Exception as e:
            print("Error en evaluación:", e)
        # Mostrar trazas breves (opcional)
        print("Trazas (ticks,evento):")
        for t, ev in model.io_agent.trace[-10:]:
            print(f"  [{t}] {ev}")

    print("\nFIN de la demostración.")
