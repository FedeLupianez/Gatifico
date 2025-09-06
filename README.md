
# Gatifico

## ¿Cómo activar y desactivar el entorno?
Primero hay que crear el entorno lo que se hace con este comando :
`python -m venv venv`

Ejecutar los siguientes comandos en la terminal de vscode :
 - **Activar** : ./venv/scripts/activate
 - **Desactivar** : deactivate
 - Si te sigue dando error en el codigo debes cambiar el intérprete de python, esto se hace así:
   - Tocás `ctrl + shift + p` y buscas `Python: Select interpreter` y seleccionar la opción `Python 3.11.0 (venv)`
 - Después de tener el entorno listo, debemos instalar Arcade, la librería de python en la que desarrollamos el juego, se puede hacer con `pip install -r requirements.txt`

## Tipo : Aventura 2D

## Personajes :
- **Protagonista**
  - **Nombre :** Dr. Miauskis.
  - **Historia : ** Antiguo científico brillante, fue exiliado de la sociedad por ser considerado un “gato loco”. Obsesionado con alcanzar la inmortalidad y decidido a demostrar que no estaba tan equivocado, se retira a un bosque solo, donde lleva a cabo extraños experimentos en busca de la combinación perfecta de elementos que lo convierta en un super-gatito.
Para lograr esto tiene que explorar su entorno para obtener material y llevarlo a su taller, experimentar con estos y conseguir nuevas combinaciones en el camino a la creación de un super gatito.
Sin un camino definido, el jugador podrá alcanzar el objetivo de diferentes formas. El “super-gatito” se consigue con la unificación de distintas habilidades como: visión nocturna, super-fuerza, velocidad, respiración bajo el agua, etc.

- **Antagonistas :**
El antagonista de esta historia es el “**Perro del Orden**” , quien detesta la “ciencia creativa-inalcanzable” del Dr. Miauskis. Quiere que todos sigan las reglas tradicionales de la química, sin mezclar leyendas con la realidad. Es un perro ordenado y con una apariencia prolija. 
Mientras el científico no esta en casa, o sea, esta explorando, el Perro se mete a su laboratorio y cambia cosas de lugar, rompe notas, roba elementos, etc.
La mecánica de que el antagonista rompa notas, se explica como que, al descubrir una nueva combinación el científico la desbloquea y guarda sus ingredientes en una nota, pero el perro rompería esta y por lo tanto borraría los ingredientes de la combinación y arruinaría el progreso del jugador. 
Para evitar esto, el científico debe esconder bien sus cosas y proteger su laboratorio de los extraños.

## ¿Dónde ocurre? :
   Ocurre en un mundo paralelo donde los gatos (y otros animales) ocupan una vida tal cual los humanos en nuestro universo, pero con muchas de sus características y necesidades animales. La sociedad está estructurada como la nuestra: hay escuelas, universidades, trabajos, tecnología, etc.
   Los eventos del juego ocurren en un bosque/pradera, con una cabaña alejada de la sociedad. Sera un mapa abierto, el jugador podrá explorar a su ritmo y decisión el escenario.

## Reglas de este mundo :
  - Los animales son antropomórficos: Caminan en dos patas, usan ropa, hablan y manejan herramientas.
  - Conservan sus necesidades felinas: Duermen muchas horas, cazan, ronronean, y odian el agua.
  - Instinto gatuno parte de su personalidad: Se distraen con luces, cajas, plumas, etc.
  - Tienen 7 vidas: Al morir, un gato puede revivir hasta 7 veces.
  - Hablan en español, los gatos pueden hablar y escribir en este idioma.
  - La tecnología es similar a la humana, pero adaptada: laptops con teclas grandes para sus patitas, por ejemplo.

## Escenas :
  - *Laboratorio*:
El científico tiene su laboratorio donde desarrolla todos sus locos experimentos, esta es un área simple dentro del mapa del mundo, pero es donde se encuentran todas las máquinas que el científico utiliza durante la aventura. Como por ejemplo la máquina de mezclas, horno, picos que haya creado para recolectar minerales, etc. Y también donde estará la sección de cofres para que el personaje pueda guardar los elementos que haya recolectado durante el tiempo que no estuvo en casa.

  - *Mundo Libre :*
Es el mundo donde vive el personaje principal, rodeado de distintos climas y paisajes, lo que afecta a los elementos que puede encontrar dentro de ellos y contribuyendo a las ganas de explorar todo el mapa para abastecerse de materiales.

  - *Mesa de Trabajo:*
Dentro del laboratorio de este curioso gato se encuentra su mesa de trabajo, donde puede realizar las acciones necesarias para conseguir nuevas combinaciones, como juntar elementos en la máquina de mezcla, separar mezclas que no salieron tan bien en la máquina de separación, etc.
