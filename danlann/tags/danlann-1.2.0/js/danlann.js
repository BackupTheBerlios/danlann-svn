$(document).ready(function() {
    var href = $('.navigation .exif a').attr('href');

    //$('body .photo').load(href + ' table');
    $.ajax({type: "GET", url: href, dataType: "xml",
        success: function(xml) {
            table = $(xml).find('table');
            $('div.photo').append(table);
            $('table.exif').hide();
         }
     });


    $('.navigation .exif a').click(function() {
        $('table.exif').slideToggle('slow');
        return false;
    })
})
