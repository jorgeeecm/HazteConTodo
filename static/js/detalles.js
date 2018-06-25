setInterval(actualizar, 30000);

function actualizar() {

        var slug = document.getElementById("slug").value;
        $.ajax({
               url:'/haztecontodo/ajax/'+slug ,
               type: "get",
               cache: true,
               timeout: 30000,
               dataType: 'json',
               success: function(data) {
                   console.log("success");
                   $('#precio').html(data.precio);
                   $('#tiempo').html(data.tiempo);
               },
               error: function(data) {
                   alert("Got an error dude "+data);
               }
        });
}
