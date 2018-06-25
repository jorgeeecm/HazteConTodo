function enableBtn() {

    var campod = $('#dias').val();
    var campoh = $('#horas').val();

    if (campod == 0) {
        if ( campoh > 0){
            document.getElementById("publicar").disabled = false;
        }
        else{
            document.getElementById("publicar").disabled = true;
        }
    }
    else if (campod > 0) {

        if (campoh >= 0){
            document.getElementById("publicar").disabled = false;
        }
        else{
            document.getElementById("publicar").disabled = true;
        }
    }
    else {
        document.getElementById("publicar").disabled = true;
    }

}
