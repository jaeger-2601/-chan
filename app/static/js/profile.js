$("#profileImage").click(function(e) {
  $("#imageUpload").click();
});

/*function fasterPreview( uploader ) {
  if ( uploader.files && uploader.files[0] ){
        $('#profileImage').attr('src', 
           window.URL.createObjectURL(uploader.files[0]) );
  }
}

$("#imageUpload").change(function(){
  fasterPreview( this );
});
*/

function previewProfileImage( uploader ) {   
  //ensure a file was selected 
  if (uploader.files && uploader.files[0]) {
      var imageFile = uploader.files[0];
      var reader = new FileReader();    
      reader.onload = function (e) {
          //set the image data as source
          $('#profileImage').attr('src', e.target.result);
      }    
      reader.readAsDataURL( imageFile );
  }
}

$("#imageUpload").change(function(){
  previewProfileImage( this );
});