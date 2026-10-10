"use strict";
const $ = id => document.getElementById(id);
let imagen = null;
let urlVista = null;
let revision = 0;

function limpiar() {
  $("error").hidden = true;
  $("error").textContent = "";
  $("resultado").textContent = "Tu resultado aparecerá aquí.";
}
function error(mensaje) {
  $("error").textContent = mensaje;
  $("error").hidden = false;
}
function ocupado(valor) {
  $("controles").disabled = valor;
  $("consulta").setAttribute("aria-busy", String(valor));
  $("enviar").textContent = valor ? "Preparando consulta…" : "Consultar estado →";
}
async function pedir(url, opciones = {}) {
  const control = new AbortController();
  const reloj = setTimeout(() => control.abort(), 5000);
  try {
    const respuesta = await fetch(url, {...opciones, signal: control.signal});
    if (!respuesta.ok) {
      const fallo = await respuesta.json().catch(() => null);
      throw new Error(fallo?.error?.mensaje || `No se pudo completar la solicitud (${respuesta.status}).`);
    }
    return respuesta;
  } catch (fallo) {
    if (fallo.name === "AbortError") throw new Error("La consulta tardó demasiado. Comprueba el servidor y vuelve a intentarlo.");
    if (fallo instanceof TypeError) throw new Error("No hay conexión con la aplicación. Comprueba que el servidor siga abierto.");
    throw fallo;
  } finally { clearTimeout(reloj); }
}
async function usarImagen(blob, nombre) {
  if (blob.size > 16384) throw new Error("La imagen supera 16 KiB. Elige un PNG pequeño del curso.");
  if (!blob.size) throw new Error("El archivo está vacío.");
  imagen = blob;
  if (urlVista) URL.revokeObjectURL(urlVista);
  urlVista = URL.createObjectURL(blob);
  $("vista").src = urlVista;
  $("vista").hidden = false;
  $("nombre-imagen").textContent = nombre;
}
async function escena() {
  const actual = ++revision;
  limpiar();
  imagen = null;
  $("vista").hidden = true;
  $("archivo").value = "";
  ocupado(true);
  try {
    const respuesta = await pedir($("escena").value);
    const blob = await respuesta.blob();
    if (actual === revision) await usarImagen(blob, $("escena").selectedOptions[0].textContent);
  } catch (fallo) { error(fallo.message); }
  finally { ocupado(false); }
}
$("escena").addEventListener("change", escena);
$("lado").addEventListener("change", limpiar);
$("archivo").addEventListener("change", async () => {
  revision++;
  limpiar(); imagen = null; $("vista").hidden = true;
  const archivo = $("archivo").files[0];
  if (!archivo) return;
  try { await usarImagen(archivo, archivo.name); }
  catch (fallo) { error(fallo.message); }
});
$("consulta").addEventListener("submit", async evento => {
  evento.preventDefault(); limpiar();
  if (!imagen) { error("Selecciona una escena o un archivo PNG."); return; }
  ocupado(true);
  try {
    const bytes = new Uint8Array(await imagen.arrayBuffer());
    const base64 = btoa(String.fromCharCode(...bytes));
    const respuesta = await pedir("/api/predecir", {method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({imagen_base64: base64, texto: `estado ${$("lado").value}`})});
    const datos = await respuesta.json();
    if (datos.estado !== "ok" || !["apagada", "encendida"].includes(datos.resultado?.clase)) throw new Error("El servidor devolvió una respuesta inesperada.");
    $("resultado").textContent = `Predicción · luz ${datos.resultado.lado}`;
    const clase = document.createElement("strong");
    clase.textContent = datos.resultado.clase === "encendida" ? "Encendida" : "Apagada";
    const nota = document.createElement("small");
    nota.textContent = "Resultado del modelo sobre la escena seleccionada.";
    $("resultado").append(clase, nota);
  } catch (fallo) { error(fallo.message); }
  finally { ocupado(false); }
});
async function iniciar() {
  try {
    await pedir("/health");
    const ejemplos = await (await pedir("/api/ejemplos")).json();
    $("escena").replaceChildren(...ejemplos.map(e => {
      const opcion = document.createElement("option"); opcion.value = e.url; opcion.textContent = e.nombre; return opcion;
    }));
    $("escena").value = "/ejemplos/01.png";
    $("conexion").textContent = "● Aplicación lista · puedes consultar una escena";
    await escena();
  } catch (fallo) {
    $("conexion").textContent = "No se pudo iniciar la interfaz. Recarga cuando el servidor esté disponible.";
    error(fallo.message);
  }
}
iniciar();
