"""Colección ficticia propia: textos y juicios escritos antes de recuperar."""
import json
from pathlib import Path

DOCUMENTOS = [
    ('D01', 'Recuperar acceso', 'Si olvidaste la contraseña del aula virtual, pulsa Restablecer acceso e indica tu correo registrado. Recibirás un enlace de recuperación.'),
    ('D02', 'Reloj de la estación', 'Para corregir la hora de la estación meteorológica, abre Ajustes, selecciona Sincronizar reloj y confirma la zona America/Bogota.'),
    ('D03', 'Hora incorrecta: guía rápida', 'La estación meteorológica ajusta su hora desde Ajustes > Sincronizar reloj. Comprueba que la zona sea America/Bogota antes de guardar.'),
    ('D04', 'Devolución de libros', 'El préstamo de libros de la biblioteca dura catorce días. Puedes renovarlo una vez desde Mi biblioteca si no hay reservas pendientes.'),
    ('D05', 'Inscripción en el taller', 'Para inscribirte en el taller de energía solar, completa el formulario Taller solar en el portal académico. La confirmación llega por correo.'),
    ('D06', 'Alimentación del S-31', 'El sensor S-31 utiliza dos pilas AA. Para cambiarlas, apágalo, abre la tapa inferior, sustituye ambas respetando la polaridad y cierra la tapa.'),
    ('D07', 'Mantenimiento del S-31', 'Cuando el S-31 indique batería baja, apaga el equipo y reemplaza las dos pilas AA del compartimento inferior, con la polaridad marcada. Cierra antes de encender.'),
    ('D08', 'Descarga de mediciones', 'Para exportar las lecturas del panel de sensores, elige un intervalo de fechas y pulsa Descargar CSV. El archivo contiene fecha, identificador y valor.'),
    ('D09', 'Anular una reserva de sala', 'Para cancelar una reserva de la sala de estudio, entra en Mis reservas, selecciona la cita y pulsa Anular. El sistema libera el horario.'),
    ('D10', 'Bases para estudiar IA', 'Antes de iniciar el curso de inteligencia artificial conviene practicar variables, condicionales, bucles y funciones de Python. La Unidad 0 ofrece una ruta de preparación.'),
    ('D11', 'Cambio de correo', 'Para cambiar el correo del aula virtual, inicia sesión, abre Perfil y guarda la nueva dirección. Esto no modifica tu contraseña.'),
    ('D12', 'Reloj del aula', 'El reloj de pared del aula funciona con una pila. Su hora se ajusta girando la rueda trasera; no se conecta a la estación meteorológica.'),
    ('D13', 'Reserva de libros', 'Para reservar un libro prestado, busca su título en el catálogo y pulsa Reservar. Recibirás un aviso cuando puedas recogerlo.'),
    ('D14', 'Materiales del taller', 'El taller de energía solar usa maquetas y fichas de trabajo. Los materiales se entregan durante la sesión; esta ficha no describe la inscripción.'),
    ('D15', 'Alimentación del S-13', 'El sensor S-13 funciona con una batería recargable USB. Para cargarlo conecta el cable al puerto lateral; no utiliza pilas AA.'),
    ('D16', 'Importación de mediciones', 'Para importar un CSV al panel de sensores, abre Cargar archivo, selecciona el documento y revisa las columnas. Esta operación añade lecturas al panel.'),
    ('D17', 'Pedir una sala', 'La sala de estudio se reserva desde Calendario: selecciona un horario libre y confirma. La biblioteca tiene un sistema distinto para reservar libros.'),
    ('D18', 'Red inalámbrica', 'La red inalámbrica para visitantes se llama AulaInvitados. La contraseña se solicita presencialmente en recepción y no aparece en esta guía.'),
    ('D19', 'Acceso al curso', 'El curso de inteligencia artificial se consulta desde el portal académico. Este texto no especifica precios, descuentos ni formas de pago.'),
    ('D20', 'Reinicio del S-31', 'Para reiniciar el sensor S-31, mantén pulsado el botón central durante cinco segundos. El reinicio conserva su identificador y no cambia las pilas.'),
]

# Dos formulaciones por intención. Una familia nunca cruza la partición.
FAMILIAS = [
    ('desarrollo', 'F01', ['D01'], 'El procedimiento recupera acceso por contraseña olvidada.',
     ['No recuerdo mi clave para entrar a clase, ¿cómo vuelvo a acceder?', 'Olvidé la contraseña del aula virtual. ¿Qué hago?']),
    ('desarrollo', 'F02', ['D02', 'D03'], 'Ambos documentos explican por completo la sincronización de la estación.',
     ['Las marcas temporales de mi estación meteorológica están desfasadas, ¿cómo las corrijo?', '¿Cómo sincronizo el reloj de la estación meteorológica?']),
    ('desarrollo', 'F03', ['D04'], 'Solo D04 especifica el plazo del préstamo.',
     ['¿Cuánto tiempo puedo quedarme con un ejemplar que me prestaron?', '¿Cuántos días dura el préstamo de libros de la biblioteca?']),
    ('desarrollo', 'F04', ['D05'], 'Solo D05 explica cómo inscribirse.',
     ['Quiero apuntarme a la actividad sobre aprovechar la luz del sol. ¿Qué trámite hago?', '¿Cómo me inscribo en el taller de energía solar?']),
    ('desarrollo', 'F05', [], 'D18 indica dónde pedir la clave, pero no dice cuál es.',
     ['Dime la contraseña exacta de AulaInvitados.', '¿Cuál es la clave de la red inalámbrica para visitantes?']),
    ('cierre', 'F06', ['D06', 'D07'], 'Ambos describen el reemplazo de pilas del S-31, no del S-13.',
     ['¿Cómo reemplazo la fuente de energía del S-31 cuando se agota?', '¿Cómo cambio las pilas del sensor S-31?']),
    ('cierre', 'F07', ['D08'], 'D08 explica sacar lecturas; importar no satisface exportar.',
     ['Necesito llevarme las lecturas del panel a una hoja de cálculo. ¿Cómo las saco?', '¿Cómo exporto las mediciones del panel de sensores a CSV?']),
    ('cierre', 'F08', ['D09'], 'Anular una reserva de sala es distinto de crearla o reservar libros.',
     ['Ya no voy a usar el espacio de estudio que aparté. ¿Cómo libero ese turno?', '¿Cómo cancelo mi reserva de la sala de estudio?']),
    ('cierre', 'F09', ['D10'], 'La consulta pide preparación, no acceso administrativo.',
     ['¿Qué debería saber programar antes de empezar a aprender inteligencia artificial?', '¿Qué bases de Python necesito para iniciar el curso de IA?']),
    ('cierre', 'F10', [], 'D19 no informa ningún precio.',
     ['¿Cuánto cuesta inscribirse en el curso de inteligencia artificial?', 'Dime el precio exacto del curso de IA.']),
]


def construir():
    corpus = [dict(id=i, titulo=t, texto=x) for i, t, x in DOCUMENTOS]
    consultas = {fase: [] for fase in ('desarrollo', 'cierre')}
    for fase, familia, relevantes, razon, textos in FAMILIAS:
        for j, texto in enumerate(textos):
            consultas[fase].append(dict(id=f'{familia}{chr(97+j)}', familia=familia,
                                       texto=texto, relevantes=relevantes, razon=razon))
    return {'corpus': corpus, **consultas}


if __name__ == '__main__':
    for nombre, filas in construir().items():
        (Path(__file__).parent / f'{nombre}.json').write_text(
            json.dumps(filas, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
