
function protegerPrimeraFila() {
  // Obtener la hoja activa
  const hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  // Rango que corresponde a la primera fila
  const rangoPrimeraFila = hoja.getRange(1, 1, 1, hoja.getLastColumn()); // Fila 1 desde la columna 1 hasta la última columna
  
  // Crear la protección para la primera fila
  const proteccion = rangoPrimeraFila.protect();
  proteccion.setDescription("Protección de la primera fila");
  
  // Establece quién puede editar (solo tú)
  const editores = proteccion.getEditors();
  proteccion.removeEditors(editores); // Elimina editores existentes
  proteccion.addEditor(Session.getEffectiveUser()); // Agrega al usuario actual
  
  // Bloquear edición para todos los demás
  if (proteccion.canDomainEdit()) {
    proteccion.setDomainEdit(false);
  }
  
  // Confirmación en la consola
  Logger.log("Primera fila protegida exitosamente");
}