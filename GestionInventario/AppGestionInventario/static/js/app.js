/** 
 * @param {*} idProducto
*/
$(function () {
  $("#fileFoto").on("change", validarImagen);
  $("#fileFoto").on("change", mostrarImagen);
})

function modalEliminar(idProducto) {
  Swal.fire({
    title: "Eliminar Producto",
    text: "¿Estas seguro de eliminar?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#00b347",
    cancelButtonColor: "#d33",
    cancelButtonText: "NO",
    confirmButtonText: "SÍ",
  }).then((result) => {
    if (result.isConfirmed) {
      location.href = "/eliminarProducto/" + idProducto+"/"
    }
  });
}

function validarImagen(evt) {
  let files = evt.target.files;
  // Nombre y tamaño del archivo
  var fileName = files[0].name;
  var fileSize = files[0].size;
  let extension = fileName.split(".").pop();
  extension = extension.toLowerCase();
  if (extension !== "jpg") {
    Swal.fire("Cargar Imagen", 'La imagen debe tener una extensión JPG', 'warning')
    $("#fileFoto").val(""); //Vaciar el campo
    $("#fileFoto").focus();
  } else if (fileSize > 5000000000) {
    Swal.fire("Cargar Imagen", 'La imagen NO puede superar los 500K', 'warning')
    $("#fileFoto").val("");
    $("#fileFoto").focus();
  }
}

function mostrarImagen(evt) {
  const archivos = evt.target.files
  const archivo = archivos[0]
  const url = URL.createObjectURL(archivo)

  $("#imagenProducto").attr("src",url)
}


