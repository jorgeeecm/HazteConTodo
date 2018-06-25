setInterval(myFunction, 3000);

function myFunction() {

        var slug = document.getElementById("slug").value;
        alert(slug)
        $.ajax({
               url:'/haztecontodo/prueba_ajax/'+slug ,
               type: "get",
               cache: true,
               timeout: 30000,
               dataType: 'json',
               success: function(data) {
                   console.log("success");
                   $('#precio').html(data.precio);
                   $('#tiempo').html(data.tiempo);

               },

        });
}

