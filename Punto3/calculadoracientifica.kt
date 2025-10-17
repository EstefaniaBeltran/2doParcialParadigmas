import kotlin.math.*

// Clase base: tiene las operaciones básicas
open class Calculadora {

    // La memoria es protected
    protected var memoria: Double = 0.0

    open fun sumar(a: Double, b: Double) = a + b
    open fun restar(a: Double, b: Double) = a - b
    open fun multiplicar(a: Double, b: Double) = a * b

    // División con la excepción de división por 0
    open fun dividir(a: Double, b: Double): Double {
        if (b == 0.0) {  // se asegura de capturar cero
            throw ArithmeticException("División por cero no permitida")
        }
        return a / b
    }

    // Funciones de memoria
    fun guardarEnMemoria(valor: Double) { memoria = valor }
    fun recuperarMemoria() = memoria
    fun limpiarMemoria() { memoria = 0.0 }
}

// Clase heredada de Calculadora y realiza las operaciones más complejas
class CalculadoraCientifica : Calculadora() {

    fun seno(g: Double) = sin(Math.toRadians(g))
    fun coseno(g: Double) = cos(Math.toRadians(g))
    fun tangente(g: Double) = tan(Math.toRadians(g))
    fun potencia(base: Double, exp: Double) = base.pow(exp)
    fun raiz(valor: Double): Double {
        if (valor < 0) throw ArithmeticException("No se puede calcular raíz de un número negativo")
        return sqrt(valor)
    }
    fun logBase10(valor: Double): Double {
        if (valor <= 0) throw ArithmeticException("Logaritmo definido solo para positivos")
        return log10(valor)
    }
    fun logNatural(valor: Double): Double {
        if (valor <= 0) throw ArithmeticException("Logaritmo definido solo para positivos")
        return ln(valor)
    }
    fun exponencial(valor: Double) = exp(valor)
    fun gradosARadianes(g: Double) = Math.toRadians(g)
    fun radianesAGrados(r: Double) = Math.toDegrees(r)
}

// Opciones del menú
fun realizarOperacion(calc: CalculadoraCientifica, opcion: Int) {
    try {
        when (opcion) {
            1 -> {
                print("Ingrese primer número: "); val a = readLine()!!.toDouble()
                print("Ingrese segundo número: "); val b = readLine()!!.toDouble()
                println("Resultado: ${calc.sumar(a, b)}")
            }
            2 -> {
                print("Ingrese primer número: "); val a = readLine()!!.toDouble()
                print("Ingrese segundo número: "); val b = readLine()!!.toDouble()
                println("Resultado: ${calc.restar(a, b)}")
            }
            3 -> {
                print("Ingrese primer número: "); val a = readLine()!!.toDouble()
                print("Ingrese segundo número: "); val b = readLine()!!.toDouble()
                println("Resultado: ${calc.multiplicar(a, b)}")
            }
            4 -> {
                print("Ingrese primer número: "); val a = readLine()!!.toDouble()
                print("Ingrese segundo número: "); val b = readLine()!!.toDouble()
                println("Resultado: ${calc.dividir(a, b)}")
            }
            5 -> {
                print("Ingrese ángulo en grados: "); val g = readLine()!!.toDouble()
                println("Seno: ${calc.seno(g)}")
            }
            6 -> {
                print("Ingrese ángulo en grados: "); val g = readLine()!!.toDouble()
                println("Coseno: ${calc.coseno(g)}")
            }
            7 -> {
                print("Ingrese ángulo en grados: "); val g = readLine()!!.toDouble()
                println("Tangente: ${calc.tangente(g)}")
            }
            8 -> {
                print("Ingrese base: "); val base = readLine()!!.toDouble()
                print("Ingrese exponente: "); val exp = readLine()!!.toDouble()
                println("Resultado: ${calc.potencia(base, exp)}")
            }
            9 -> {
                print("Ingrese número: "); val num = readLine()!!.toDouble()
                println("Resultado: ${calc.raiz(num)}")
            }
            10 -> {
                print("Ingrese número: "); val num = readLine()!!.toDouble()
                println("Resultado: ${calc.logBase10(num)}")
            }
            11 -> {
                print("Ingrese número: "); val num = readLine()!!.toDouble()
                println("Resultado: ${calc.logNatural(num)}")
            }
            12 -> {
                print("Ingrese número: "); val num = readLine()!!.toDouble()
                println("Resultado: ${calc.exponencial(num)}")
            }
            13 -> {
                print("Ingrese grados: "); val g = readLine()!!.toDouble()
                println("Radianes: ${calc.gradosARadianes(g)}")
            }
            14 -> {
                print("Ingrese radianes: "); val r = readLine()!!.toDouble()
                println("Grados: ${calc.radianesAGrados(r)}")
            }
            15 -> {
                print("Ingrese valor a guardar en memoria: "); val valor = readLine()!!.toDouble()
                calc.guardarEnMemoria(valor)
                println("El valor se guardó correctamente en memoria.")
            }
            16 -> println("Memoria actual: ${calc.recuperarMemoria()}")
            17 -> {
                calc.limpiarMemoria()
                println("Memoria limpia.")
            }
            else -> println("Opción no válida :(")
        }
    } catch (e: NumberFormatException) {
        println("Error: Ingrese un número válido :(")
    } catch (e: ArithmeticException) {
        println("Error: ${e.message}")
    }
}

// MAIN
fun main() {
    val calc = CalculadoraCientifica()

    while (true) {
        println("\n===  Calculadora Científica ===")
        println("1. Sumar")
        println("2. Restar")
        println("3. Multiplicar")
        println("4. Dividir")
        println("5. Seno")
        println("6. Coseno")
        println("7. Tangente")
        println("8. Potencia")
        println("9. Raíz cuadrada")
        println("10. Log base10")
        println("11. ln")
        println("12. Exponencial")
        println("13. Grados→Radianes")
        println("14. Radianes→Grados")
        println("15. Guardar en memoria")
        println("16. Recuperar memoria")
        println("17. Limpiar memoria")
        println("0. Salir")
        print("Seleccione una opción: ")

        val opcion = readLine()?.toIntOrNull() ?: -1

        if (opcion == 0) {
            println("Hasta luego, ¡Gracias por usar la calculadora!")
            break
        }

        realizarOperacion(calc, opcion)

        print("\n¿Desea realizar otra operación? (s/n): ")
        val continuar = readLine()!!
        if (continuar.toLowerCase() != "s") {
            println("Hasta luego, ¡Gracias por usar la calculadora!")
            break
        }
    }
}


