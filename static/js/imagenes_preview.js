function previewImages() {

  var preview = document.querySelector('#preview');

  if (this.files) {
    [].forEach.call(this.files, readAndPreview);
  }

  function clear(){
    pre
  }
  function readAndPreview(file) {

    // Make sure `file.name` matches our extensions criteria
    if (!/\.(jpe?g|png|gif)$/i.test(file.name)) {
      return alert(file.name + " is not an image");
    } // else...

    var reader = new FileReader();

    reader.addEventListener("load", function() {
      var image = new Image();
      image.height = 100;
      image.title  = file.name;
      image.src    = this.result;
      preview.appendChild(image);
    }, false);

    reader.readAsDataURL(file);

  }

}

document.querySelector('#file-input').addEventListener("change", previewImages, false);
