let materiales = []
let entradaMateriales = []
let unidadesMedida = []

$(function(){
    //Se Utiliza para las peticiones ajax con jquery
    $.ajaxSetup({
        headers:{
            'X-CSRFToken':getCookie('csrftoken')
        }
    })
    
    $("#btnAgregarMaterialDetalle").click(function(){
        agregarMaterialADetalle();
    })

    $("#entradaMaterial").click(function(){
        vistaEntradaMaterial();
    })

    $("#btnRegistrarDetalle").click(function(){
        registroDetalleEntrada();
    })

})

/**
 * Funcion Utilizada para hacer peticiones ajax
 * necesarias en django remplaza el csrf utilizado
 * en los Formulario
 * @param {*}
 * @returns
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


/**
 * Realiza la peticion ajax para registrar
 * la entrada de materiales 
 */
function registroDetalleEntrada() {
    var datos = {
        "codigoFactura": $("#txtFactura").val(),
        "entregadoPor": $("#txtEntregadoPor").val(),
        "proveedor": $("#cbProveedor").val(),
        "recibidoPor": $("#cbRecibidoPor").val(),
        "observaciones": $("#txtObservaciones").val(),
        "fechaHora": $("#fechaHora").val(),
        "detalle": JSON.stringify(entradaMateriales),
    };
    $.ajax({
        url : "/registrarEntradaMaterial/",
        data : datos,
        type: 'post',
        dataType: 'json',
        cache: false,
        success: function(resultado){
            console.log(resultado);
            if(resultado.estado){
                setTimeout(function() {
                    location.reload();  // Recarga la página después de 2 segundos
                  }, 2000);
                entradaMateriales.length=0;
                mostrarDatosTabla();
            }
            Swal.fire("Registro de Materiales",resultado.mensaje, "success");
        }
    })
}

/**btnRegistrarDetalle
 * Agrega cada Material al Arreglo de EntradaMateriales,
 * Primero valida que no se haya agregado previamente
 */
function agregarMaterialADetalle() {
    //Averiguar si ya se ha agregado el material 
    const m =entradaMateriales.find(material=>material.idMaterial == $('#cbMaterial').val());
    if (m == null) {
        const material = {
            "idMaterial": $('#cbMaterial').val(),
            "cantidad": $("#txtCantidad").val(),
            "precio": $("#txtPrecio").val(),
            "idUnidadMedida": $("#cbUnidadMedida").val(),
            "estado": $("#cbEstado").val(),
        }
        entradaMateriales.push(material);
        frmEntradaMaterial.reset();
        mostrarDatosTabla();
    } else {
        Swal.fire("Entrada Materiales", 
        "El Material Selecionado ya se ha agregado en el detalle. verifique", "info");
    }
}

/**
 * Agrega los Materiales del Arreglo entradaMateriales
 * en la tabla HTML
 */
function mostrarDatosTabla(){
    datos = "";
    entradaMateriales.forEach(entrada =>{
        //Obtiene la posicion del Material en el arreglo materiales de acuerdo al idMateriales
        //Del Arreglo entradaMateriales, para poder obtener el codigo y nombre del material
        posM = materiales.findIndex(material=>material.idMaterial==entrada.idMaterial);
        //obtiene la posicion de la unidad de medida en el arreglo UnidadesMedida de acuerdo
        // al idUnidadesMedida en el arreglo entradaMateriales para poder obtener el nombre
        posU = unidadesMedida.findIndex(unidad=>unidad.id == entrada.idUnidadMedida);
        datos += "<tr>";
        datos += "<td class='text-center'>" + materiales[posM].codigo + "</td>"; 
        datos += "<td>" + materiales[posM].nombre + "</td>";
        datos += "<td class='text-center'>" + entrada.cantidad + "</td>";
        datos += "<td class='text-end'>" + "$" + entrada.precio + ".00" + "</td>";
        datos += "<td>" + unidadesMedida[posU].nombre + "</td>";
        datos += "<td class ='text-center'>" + entrada.estado + "</td>";
        datos += "</tr>"; 
    });
    //Agregar a la tabla con id datosTableMateriales 
    datosTablaMateriales.innerHTML = datos;
}

/**
 * Obtiene los materiales registrados en el 
 * sistema con los datos necesarios. Los recibe
 * de la vista y los almacena en un arreglo
 * @param {*} idMaterial
 * @param {*} codigo
 * @param {*} nombre
 */
function cargarMateriales(idMaterial, codigo, nombre){
    const material ={
        "idMaterial":idMaterial,
        "codigo":codigo,
        "nombre":nombre,
    }
    materiales.push(material);
}

/**
 * Obtiene Las Unidades de medida y los 
 * almacena en un arreglo 
 * @param {*} id
 * @param {*} nombre
 */
function cargarUnidadesMedida(id, nombre){
    const unidadMedida = {
        "id" : id,  
        "nombre" : nombre,
    }
    unidadesMedida.push(unidadMedida);
}