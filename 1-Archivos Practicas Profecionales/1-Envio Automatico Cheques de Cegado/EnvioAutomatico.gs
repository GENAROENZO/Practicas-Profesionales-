/**
 * Lista de usuarios y sus correos electrónicos.
 */
const usuariosCorreos = [
  { nombre: "Genaro Ferrero", correo: "genaroenzo4@gmail.com" }
];

/**
 * Función principal para procesar y enviar correos basados en vencimientos de cheques y resoluciones.
 */
function enviarCorreosChequeResolucion() {
  const hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const datos = hoja.getDataRange().getValues();
  const hoy = new Date();

  for (let i = 1; i < datos.length; i++) { // Comienza desde la fila 2 para omitir encabezados
    const [solicitante, titularCheque, expteNum, nota,excelMes, anio,expteElectronico,pozo ,estado , diasReemplazo, resolucion,notificada, vencimientoResolucion,pozoNuevo, vencimientoCheque, fechaOrdenDevolucion,directorTecnico, observaciones,acta, fecha, estadoCorreo] = datos[i];

    console.log(`Procesando fila ${i + 1}: ${JSON.stringify({solicitante, titularCheque, expteNum, nota,excelMes, anio,expteElectronico,pozo,estado , diasReemplazo, resolucion,notificada, vencimientoResolucion, pozoNuevo, vencimientoCheque, fechaOrdenDevolucion,directorTecnico, observaciones,acta, fecha, estadoCorreo})}`);
    console.log(`Valor en estadoCorreo (Fila ${i + 1}): "${estadoCorreo}"`);

    // Verificar si el correo ya fue enviado
    if (String(estadoCorreo).trim() === "Correo Enviado") {
      console.log(`Fila ${i + 1}: Correo ya enviado, se omite.`);
      continue;
    }

    try {
      // Verificar vencimiento del cheque
      // NOTA: El rango de aviso se mantiene en 30 días, según tu código.
      if (esFechaValida(vencimientoCheque) && esDentroDelRango(hoy, vencimientoCheque, 30)) { 
        console.log(`Fila ${i + 1}: Correo cheque a enviar.`);
        usuariosCorreos.forEach(usuario => {
          enviarCorreoHTML(
            usuario.nombre, vencimientoCheque, titularCheque, expteNum, resolucion, expteElectronico, observaciones, usuario.correo,
            pozo, directorTecnico, "Cheque Próximo a Vencer", i + 1, hoja, "Cheque"
          );
        });
      }
    } catch (error) {
      console.error(`Error procesando fila ${i + 1}: ${error.message}`);
    }
  }
}

/**
 * Envia un correo en formato HTML.
 */
function enviarCorreoHTML(nombreInterno, fechaVencimiento, titularCheque, expteNum, resolucion, expteElectronico, observaciones, correo, pozo, directorTecnico, asunto, fila, hoja, tipo) {
  try {
    const fechaVencimientoFormateada = new Date(fechaVencimiento).toLocaleDateString('es-AR'); // Formato DD/MM/AAAA

    // 1. DEFINICIÓN DE LAS IDS DE GOOGLE DRIVE (¡ACTUALIZADAS!)
    const ID_BANNER_SUPERIOR = "1UfIXge5hgjedE-jlQrQM0qcVyQmzwstL"; // ID de la primera URL
    const ID_BANNER_INFERIOR = "1q6slx7sBSz9SWjKDN_kJlus9fYPXuLiA"; // ID de la segunda URL
    
    // 2. CARGA DE LAS IMÁGENES COMO BLOB DE DATOS
    // Asumo que ambas son JPEG. Si alguna es PNG, ajusta "image/jpeg" a "image/png"
    const bannerSuperior = DriveApp.getFileById(ID_BANNER_SUPERIOR).getAs("image/jpeg").setName("bannerSup");
    const bannerInferior = DriveApp.getFileById(ID_BANNER_INFERIOR).getAs("image/jpeg").setName("bannerInf");


    // 3. FORMATO DEL MENSAJE HTML USANDO 'cid:'
    const mensajeHTML = `
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="margin-top: 10px; text-align: center;">
            <img src="cid:bannerSup" alt="Banner Superior" style="max-width: 100%; height: auto; border-radius: 5px;">
        </div>
        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px;">
            <h2 style="color: #00aaff;">Hola ${nombreInterno || "Estimado/a"}!</h2>
            <p style="font-size: 16px;">
                El día <strong>${fechaVencimientoFormateada}</strong> 
                se vence el <span style="color: #00aaff;">Cheque</span> a nombre de 
                <span style="color: #00aaff;">${titularCheque}</span>.
            </p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <tr>
                    <td style="background-color: #e1e1e1; padding: 5px; font-weight: bold; width: 20%;">Número de Expediente:</td>
                    <td style="background-color: #fff; padding: 5px; color: #00aaff;">${expteNum || "No tiene"}</td>
                </tr>
                <tr>
                    <td style="background-color: #e1e1e1; padding: 5px; font-weight: bold; width: 20%;">Expediente Electrónico:</td>
                    <td style="background-color: #fff; padding: 5px; color: #00aaff;">${expteElectronico || "No tiene"}</td>
                </tr>
                <tr>
                    <td style="background-color: #e1e1e1; padding: 5px; font-weight: bold; width: 20%;">Número de Pozo:</td>
                    <td style="background-color: #fff; padding: 5px; color: #00aaff;">${pozo || "No tiene"}</td>
                </tr>
                <tr>
                    <td style="background-color: #e1e1e1; padding: 5px; font-weight: bold; width: 20%;">Titular:</td>
                    <td style="background-color: #fff; padding: 5px; color: #00aaff;">${titularCheque || "No tiene"}</td>
                </tr>
                <tr>
                    <td style="background-color: #e1e1e1; padding: 5px; font-weight: bold; width: 20%;">Resolución:</td>
                    <td style="background-color: #fff; padding: 5px; color: #00aaff;">${resolucion || "No tiene"}</td>
                </tr>
                <tr>
                    <td style="background-color: #e1e1e1; padding: 5px; font-weight: bold; width: 20%;">Fecha de Vencimiento Cheque:</td>
                    <td style="background-color: #fff; padding: 5px; color: #00aaff;">${fechaVencimientoFormateada || "No tiene"}</td>
                </tr>
                <tr>
                    <td style="background-color: #e1e1e1; padding: 5px; font-weight: bold; width: 20%;">Director Técnico:</td>
                    <td style="background-color: #fff; padding: 5px; color: #00aaff;">${directorTecnico || "No tiene"}</td>
                </tr>
                <tr>
                    <td style="background-color: #e1e1e1; padding: 5px; font-weight: bold; width: 20%;">Observaciones:</td>
                    <td style="background-color: #fff; padding: 5px; color: #00aaff;">${observaciones || "Sin observaciones"}</td>
                </tr>
            </table>
        </div>
        <div style="margin-top: 10px; text-align: center;">
            <img src="cid:bannerInf" alt="Banner Inferior" style="max-width: 100%; height: auto; border-radius: 5px;">
        </div>
      </body>
    </html>`;

    // 4. ENVÍO DEL CORREO CON LAS IMÁGENES INLINE
    MailApp.sendEmail({
      to: correo,
      subject: asunto,
      htmlBody: mensajeHTML,
      inlineImages: { // Nuevo parámetro crucial
        bannerSup: bannerSuperior,
        bannerInf: bannerInferior
      }
    })

    console.log(`Correo enviado a ${correo} exitosamente.`);

    // Actualizar estado en la hoja
    hoja.getRange(fila, 21).setValue("Correo Enviado").setFontColor("green");
    SpreadsheetApp.flush();

  } catch (error) {
    console.error(`Error al enviar correo a ${correo}: ${error.message}`);
  }
}

/**
 * Verifica si una fecha es válida.
 */
function esFechaValida(fecha) {
  const valid = fecha instanceof Date && !isNaN(fecha);
  console.log(`Fecha ${fecha} válida: ${valid}`);
  return valid;
}

/**
 * Verifica si una fecha está dentro de un rango de días respecto a otra fecha.
 */
function esDentroDelRango(hoy, fechaVencimiento, dias) {
  const fechaVencimientoDate = new Date(fechaVencimiento);
  const diferencia = (fechaVencimientoDate - hoy) / (1000 * 60 * 60 * 24);
  console.log(`Diferencia de días para ${fechaVencimiento}: ${diferencia}`);
  return diferencia >= 0 && diferencia <= dias;
}