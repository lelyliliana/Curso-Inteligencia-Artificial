"""Contraejemplos artificiales: una cita existente no demuestra el dato."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ejemplos'))
from rag import cargar, evaluar_salida, extraer, guardar, preparar_contexto, UNIDAD


def auditar():
    caso=cargar(UNIDAD/'datos/desarrollo.json')[0]
    contexto=preparar_contexto(extraer(),[{'id':'D01:p01'},{'id':'D02:p01'}])
    correcto='{"estado":"ok","dato":"9 días","citas":["D01:p01"]}'
    muestras=[
        ('correcta',correcto,True),
        ('dato falso con ID real','{"estado":"ok","dato":"99 días","citas":["D01:p01"]}',True),
        ('dato correcto con fuente ajena','{"estado":"ok","dato":"9 días","citas":["D02:p01"]}',True),
        ('ID existente fuera del contexto','{"estado":"ok","dato":"9 días","citas":["D01:p02"]}',True),
        ('ID inventado','{"estado":"ok","dato":"9 días","citas":["D99:p01"]}',True),
        ('sin cita','{"estado":"ok","dato":"9 días","citas":[]}',True),
        ('ausencia falsa','{"estado":"ausente","dato":null,"citas":[]}',True),
        ('clave duplicada','{"estado":"ausente","estado":"ok","dato":"9 días","citas":["D01:p01"]}',True),
        ('bloque Markdown','```json\n'+correcto+'\n```',True),
        ('respuesta truncada',correcto,False),
        ('espacios y mayúsculas','{"estado":"ok","dato":" 9 DÍAS ","citas":["D01:p01"]}',True),
        ('conflicto inventado','{"estado":"conflicto","dato":null,"citas":["D01:p01","D02:p01"]}',True),
    ]
    return [{'nombre':n,'texto_artificial':t,**evaluar_salida(t,caso,contexto,fin)} for n,t,fin in muestras]


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--salida',type=Path); args=p.parse_args()
    filas=auditar()
    print(f"Salidas artificiales: {len(filas)}; aceptadas={sum(f['aceptada'] for f in filas)}.")
    for f in filas: print(f"{f['nombre']}: {f.get('fallo','aceptada')}")
    if args.salida:
        guardar(args.salida/'auditoria.json',{'origen':'salidas_artificiales','filas':filas})
        print(f'Exportación: {args.salida}')


if __name__=='__main__': main()
